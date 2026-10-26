from __future__ import annotations

from email import policy
from pathlib import Path
from email.parser import BytesParser
from email.message import EmailMessage

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI, BadRequestError
from openai._types import FileTypes
from openai.types.audio import VoiceConsent

RECORDING = b"RIFF\x00synthetic-private-consent-recording\xff"
API_KEY = "sk-synthetic-consent-security-test"
CRAFTED_FILENAME = 'consent"\r\nX-Injected: true\r\n.wav'


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("input_kind", ["file", "path", "tuple", "crafted", "tuple_bytes"])
@pytest.mark.parametrize("status", [200, 400])
async def test_consent_upload_security(
    is_async: bool,
    input_kind: str,
    status: int,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    recording_path = tmp_path / "consent.wav"
    recording_path.write_bytes(RECORDING)
    requests: list[httpx2.Request] = []
    caplog.set_level("DEBUG", logger="openai")

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        assert request.method == "POST"
        assert str(request.url) == "https://consent.example.test/v1/audio/voice_consents"
        assert request.headers["authorization"] == f"Bearer {API_KEY}"
        assert "x-injected" not in request.headers
        content_type = request.headers["content-type"]
        assert content_type.startswith("multipart/form-data;")
        message = BytesParser(_class=EmailMessage, policy=policy.default).parsebytes(
            f"Content-Type: {content_type}\r\n\r\n".encode() + request.read()
        )
        parts = list(message.iter_parts())
        assert len(parts) == 3
        named = {part.get_param("name", header="content-disposition"): part for part in parts}
        assert set(named) == {"recording", "language", "name"}
        recording = named["recording"]
        assert recording.get_payload(decode=True) == RECORDING
        if input_kind in {"file", "path"}:
            assert recording.get_content_type() in {"audio/wav", "audio/x-wav"}
        else:
            assert recording.get_content_type() == "audio/wav"
        filename = recording.get_filename()
        assert filename is not None
        if input_kind == "crafted":
            assert filename == "consent%22%0D%0AX-Injected: true%0D%0A.wav"
        else:
            assert filename == "consent.wav"
        assert set(key.lower() for key in recording.keys()) == {"content-disposition", "content-type"}
        assert named["language"].get_payload(decode=True) == b"en-US"
        assert named["name"].get_payload(decode=True) == b"Synthetic consent"
        if status == 400:
            return httpx2.Response(
                400, json={"error": {"message": "Invalid recording", "type": "invalid_request_error"}}
            )
        return httpx2.Response(
            200,
            json={
                "id": "cons_synthetic",
                "object": "audio.voice_consent",
                "name": "Synthetic consent",
                "language": "en-US",
                "created_at": 1734220800,
            },
        )

    transport = httpx2.MockTransport(handler)
    client = (
        AsyncOpenAI(
            api_key=API_KEY,
            base_url="https://consent.example.test/v1",
            max_retries=0,
            http_client=httpx2.AsyncClient(transport=transport),
        )
        if is_async
        else OpenAI(
            api_key=API_KEY,
            base_url="https://consent.example.test/v1",
            max_retries=0,
            http_client=httpx2.Client(transport=transport),
        )
    )
    try:
        with recording_path.open("rb") as recording_file:
            recording_input: FileTypes = recording_file
            if input_kind == "path":
                recording_input = recording_path
            elif input_kind == "tuple_bytes":
                recording_input = ("consent.wav", RECORDING, "audio/wav")
            elif input_kind in {"tuple", "crafted"}:
                recording_input = (
                    CRAFTED_FILENAME if input_kind == "crafted" else "consent.wav",
                    recording_file,
                    "audio/wav",
                )
            try:
                if isinstance(client, AsyncOpenAI):
                    consent = await client.audio.voice_consents.create(
                        recording=recording_input, language="en-US", name="Synthetic consent"
                    )
                else:
                    consent = client.audio.voice_consents.create(
                        recording=recording_input, language="en-US", name="Synthetic consent"
                    )
            except BadRequestError as error:
                assert status == 400
                assert "synthetic-private-consent-recording" not in str(error)
                assert API_KEY not in str(error)
            else:
                assert status == 200
                assert isinstance(consent, VoiceConsent)
                assert consent.id == "cons_synthetic"
    finally:
        if isinstance(client, AsyncOpenAI):
            await client.close()
        else:
            client.close()

    assert len(requests) == 1
    assert any("Sending HTTP Request" in record.getMessage() for record in caplog.records)
    assert "synthetic-private-consent-recording" not in caplog.text
    assert API_KEY not in caplog.text
    assert recording_path.read_bytes() == RECORDING
