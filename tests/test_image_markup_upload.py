from __future__ import annotations

import io
from email import policy
from email.parser import BytesParser
from email.message import EmailMessage

import httpx2
import pytest

from openai import OpenAI, Stream, AsyncOpenAI, AsyncStream, BadRequestError, omit
from openai.types import ImagesResponse

API_KEY = "sk-synthetic-image-upload-test"
IMAGE = b"\x89PNG\r\nsynthetic-private-original-image"
OVERLAY = b"\x89PNG\r\nsynthetic-private-overlay-image"
PROMPT = "synthetic-private-edit-prompt"


@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("stream", [False, True])
@pytest.mark.parametrize("field", [None, "markup", "mask"])
@pytest.mark.parametrize("status", [200, 400])
async def test_image_edit_upload(
    is_async: bool,
    stream: bool,
    field: str | None,
    status: int,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level("DEBUG", logger="openai")
    requests: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        assert request.method == "POST"
        assert str(request.url) == "https://images.example.test/v1/images/edits"
        assert request.headers["authorization"] == f"Bearer {API_KEY}"
        content_type = request.headers["content-type"]
        assert content_type.startswith("multipart/form-data; boundary=")
        message = BytesParser(_class=EmailMessage, policy=policy.default).parsebytes(
            f"Content-Type: {content_type}\r\n\r\n".encode() + request.read()
        )
        parts = list(message.iter_parts())
        named = {part.get_param("name", header="content-disposition"): part for part in parts}
        expected = {"image", "prompt", "stream"} | ({field} if field else set())
        assert set(named) == expected
        assert len(parts) == len(expected)
        assert named["image"].get_payload(decode=True) == IMAGE
        assert named["prompt"].get_payload(decode=True) == PROMPT.encode()
        assert named["stream"].get_payload(decode=True) == (b"true" if stream else b"false")
        if field:
            assert named[field].get_payload(decode=True) == OVERLAY
            assert named[field].get_filename() == "overlay.png"
            assert named[field].get_content_type() == "image/png"
        if status == 400:
            return httpx2.Response(400, json={"error": {"message": "Invalid image", "type": "invalid_request_error"}})
        if stream:
            return httpx2.Response(200, headers={"content-type": "text/event-stream"}, content=b"data: [DONE]\n\n")
        return httpx2.Response(200, json={"created": 1, "data": []})

    transport = httpx2.MockTransport(handler)
    client = (
        AsyncOpenAI(
            api_key=API_KEY,
            base_url="https://images.example.test/v1",
            max_retries=0,
            http_client=httpx2.AsyncClient(transport=transport),
        )
        if is_async
        else OpenAI(
            api_key=API_KEY,
            base_url="https://images.example.test/v1",
            max_retries=0,
            http_client=httpx2.Client(transport=transport),
        )
    )
    try:
        with io.BytesIO(IMAGE) as image, io.BytesIO(OVERLAY) as overlay:
            try:
                if isinstance(client, AsyncOpenAI):
                    result = await client.images.edit(
                        image=("original.png", image, "image/png"),
                        prompt=PROMPT,
                        stream=stream,
                        markup=("overlay.png", overlay, "image/png") if field == "markup" else omit,
                        mask=("overlay.png", overlay, "image/png") if field == "mask" else omit,
                    )
                    if stream:
                        assert isinstance(result, AsyncStream)
                        assert [event async for event in result] == []
                    else:
                        assert isinstance(result, ImagesResponse)
                        assert result.data == []
                else:
                    sync_result = client.images.edit(
                        image=("original.png", image, "image/png"),
                        prompt=PROMPT,
                        stream=stream,
                        markup=("overlay.png", overlay, "image/png") if field == "markup" else omit,
                        mask=("overlay.png", overlay, "image/png") if field == "mask" else omit,
                    )
                    if stream:
                        assert isinstance(sync_result, Stream)
                        assert list(sync_result) == []
                    else:
                        assert isinstance(sync_result, ImagesResponse)
                        assert sync_result.data == []
            except BadRequestError as error:
                assert status == 400
                assert all(value not in str(error) for value in (API_KEY, PROMPT, "synthetic-private"))
            else:
                assert status == 200
            assert not image.closed and not overlay.closed
    finally:
        if isinstance(client, AsyncOpenAI):
            await client.close()
        else:
            client.close()

    assert len(requests) == 1
    assert any("Sending HTTP Request" in record.getMessage() for record in caplog.records)
    for record in caplog.records:
        assert all(
            value not in record.getMessage() and value not in repr(record.args)
            for value in (API_KEY, PROMPT, "synthetic-private")
        )
        assert record.exc_info is None
