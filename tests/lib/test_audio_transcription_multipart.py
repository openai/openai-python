from __future__ import annotations

import io
import json
from copy import deepcopy
from email import policy
from typing import Any, cast
from email.parser import BytesParser

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI, omit
from openai.types.audio import Transcription

FILE_BYTES = b"RIFF\x00synthetic audio\xff\r\nWAVE"
VAD = {"type": "server_vad", "threshold": 0, "prefix_padding_ms": 0, "silence_duration_ms": 0}
UNSERIALIZABLE = object()
CASES = [
    pytest.param({"chunking_strategy": VAD}, VAD, id="vad-zero"),
    pytest.param({"chunking_strategy": {"type": "server_vad"}}, {"type": "server_vad"}, id="vad-defaults"),
    pytest.param({"chunking_strategy": {**VAD, "future": True}}, {**VAD, "future": True}, id="extra-object-field"),
    pytest.param(
        {"chunking_strategy": "auto", "extra_body": {"chunking_strategy": VAD, "extra_flag": False}},
        VAD,
        id="override-vad",
    ),
    pytest.param(
        {"chunking_strategy": {"unserializable": UNSERIALIZABLE}, "extra_body": {"chunking_strategy": VAD}},
        VAD,
        id="override-losing-object",
    ),
    pytest.param(
        {"chunking_strategy": {"unserializable": UNSERIALIZABLE}, "extra_body": {"chunking_strategy": "auto"}},
        "auto",
        id="override-auto",
    ),
    pytest.param({"chunking_strategy": VAD, "extra_body": {"chunking_strategy": None}}, None, id="override-null"),
    pytest.param({"chunking_strategy": VAD, "extra_body": {"chunking_strategy": omit}}, None, id="override-omit"),
    pytest.param({"chunking_strategy": "auto"}, "auto", id="auto"),
    pytest.param({}, None, id="omitted"),
    pytest.param({"chunking_strategy": None}, None, id="null"),
    pytest.param({"chunking_strategy": omit}, None, id="omit"),
    pytest.param({"chunking_strategy": {}}, {}, id="empty-object"),
    pytest.param({"extra_body": {"chunking_strategy": 0}}, "0", id="scalar-zero"),
    pytest.param({"extra_body": {"chunking_strategy": False}}, "false", id="scalar-false"),
    pytest.param({"extra_body": {"chunking_strategy": json.dumps(VAD)}}, VAD, id="preencoded-json"),
    pytest.param({"chunking_strategy": VAD, "extra_body": {"extra_flag": False}}, VAD, id="unrelated-override"),
]


@pytest.fixture(autouse=True)
def clean_sdk_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    import os

    for key in os.environ:
        if key.startswith(("OPENAI_", "AZURE_OPENAI_")):
            monkeypatch.delenv(key)


def assert_multipart(request: httpx2.Request, expected: object, *, has_extra_flag: bool) -> None:
    assert request.url.path == "/v1/audio/transcriptions"
    assert request.headers["x-request-marker"] == "request"
    assert request.url.params["probe"] == "request"
    content_type = request.headers["content-type"]
    assert content_type.startswith("multipart/form-data; boundary=")
    message = BytesParser(policy=policy.default).parsebytes(
        f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode() + request.read()
    )
    fields: dict[str, list[bytes]] = {}
    files: list[tuple[str, str | None, str, bytes]] = []
    for part in message.iter_parts():
        name = part.get_param("name", header="content-disposition")
        assert isinstance(name, str)
        payload = part.get_payload(decode=True)
        assert isinstance(payload, bytes)
        if part.get_filename() is not None:
            files.append((name, part.get_filename(), part.get_content_type(), payload))
        else:
            fields.setdefault(name, []).append(payload)

    assert files == [("file", "test.wav", "audio/wav", FILE_BYTES)]
    assert fields["model"] == [b"gpt-4o-transcribe"]
    assert fields["temperature"] == [b"0"]
    assert fields["stream"] == [b"false"]
    assert fields["include[]"] == [b"logprobs"]
    assert fields["timestamp_granularities[]"] == [b"word", b"segment"]
    assert fields["known_speaker_names[]"] == [b"Alice", b"Bob"]
    assert fields["known_speaker_references[]"] == [b"data:audio/wav;base64,AA==", b"data:audio/wav;base64,AQ=="]
    assert fields.get("extra_flag", []) == ([b"false"] if has_extra_flag else [])
    assert not any(name.startswith("chunking_strategy[") for name in fields)
    values = fields.get("chunking_strategy", [])
    if isinstance(expected, dict):
        assert len(values) == 1
        assert json.loads(values[0]) == expected
    else:
        assert values == ([] if expected is None else [str(expected).encode()])


@pytest.mark.parametrize("changes,expected", CASES)
@pytest.mark.parametrize("async_client", [False, True], ids=["sync", "async"])
async def test_chunking_strategy_wire(changes: dict[str, Any], expected: object, async_client: bool) -> None:
    changes = deepcopy(changes, {id(UNSERIALIZABLE): UNSERIALIZABLE, id(omit): omit})
    before = deepcopy(changes, {id(UNSERIALIZABLE): UNSERIALIZABLE, id(omit): omit})
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        request.read()
        requests.append(request)
        return httpx2.Response(200, json={"text": "synthetic"})

    common: dict[str, Any] = {
        "api_key": "sk-synthetic",
        "base_url": "https://multipart.invalid/v1",
        "max_retries": 0,
        "default_headers": {"x-request-marker": "client"},
        "default_query": {"probe": "client"},
    }
    with io.BytesIO(FILE_BYTES) as file:
        kwargs: dict[str, Any] = {
            "file": ("test.wav", file, "audio/wav"),
            "model": "gpt-4o-transcribe",
            "temperature": 0,
            "stream": False,
            "include": ["logprobs"],
            "timestamp_granularities": ["word", "segment"],
            "known_speaker_names": ["Alice", "Bob"],
            "known_speaker_references": ["data:audio/wav;base64,AA==", "data:audio/wav;base64,AQ=="],
            "extra_headers": {"x-request-marker": "request"},
            "extra_query": {"probe": "request"},
            **changes,
        }
        if async_client:
            async with AsyncOpenAI(
                **common, http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False)
            ) as client:
                response = cast(Transcription, await client.audio.transcriptions.create(**kwargs))
                assert response.text == "synthetic"
        else:
            with OpenAI(
                **common, http_client=httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False)
            ) as sync_client:
                response = cast(Transcription, sync_client.audio.transcriptions.create(**kwargs))
                assert response.text == "synthetic"
        assert not file.closed
        assert changes == before
        assert len(requests) == 1
        assert_multipart(requests[0], expected, has_extra_flag="extra_flag" in changes.get("extra_body", {}))
