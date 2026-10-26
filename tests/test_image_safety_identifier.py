import json
import inspect
from typing import Optional

import httpx2
import pytest

from openai import OpenAI, Stream, AsyncOpenAI, AsyncStream
from openai.types import ImageGenCompletedEvent, ImageEditCompletedEvent


@pytest.mark.parametrize("operation", ["generate", "edit"])
@pytest.mark.parametrize("streaming", [False, True])
@pytest.mark.parametrize("value", ["synthetic-image-safety-user", None, "omitted"])
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_image_safety_identifier(
    operation: str, streaming: bool, value: Optional[str], asynchronous: bool
) -> None:
    requests: list[httpx2.Request] = []
    field = {} if value == "omitted" else {"safety_identifier": value}
    expected = None if value == "omitted" else value
    event_type = "image_generation.completed" if operation == "generate" else "image_edit.completed"
    payload = (
        {
            "type": event_type,
            "b64_json": "c3ludGhldGlj",
            "created_at": 1620000000,
            "size": "1024x1024",
            "quality": "high",
            "background": "transparent",
            "output_format": "png",
            "usage": {
                "total_tokens": 100,
                "input_tokens": 50,
                "output_tokens": 50,
                "input_tokens_details": {"text_tokens": 10, "image_tokens": 40},
            },
            **field,
        }
        if streaming
        else {"created": 1620000000, "data": [{"b64_json": "c3ludGhldGlj"}], **field}
    )

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        if streaming:
            return httpx2.Response(
                200, headers={"content-type": "text/event-stream"}, content=f"data: {json.dumps(payload)}\n\n"
            )
        return httpx2.Response(200, json=payload)

    if asynchronous:
        client = AsyncOpenAI(
            api_key="synthetic-key",
            base_url="https://example.com/v1",
            http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler), trust_env=False),
        )
    else:
        client = OpenAI(
            api_key="synthetic-key",
            base_url="https://example.com/v1",
            http_client=httpx2.Client(transport=httpx2.MockTransport(handler), trust_env=False),
        )
    try:
        if operation == "generate":
            pending = client.images.generate(
                prompt="A synthetic image",
                stream=streaming,
                safety_identifier="synthetic-request-user",
                user="legacy-user",
            )
        else:
            pending = client.images.edit(
                prompt="A synthetic image",
                image=("test.png", b"synthetic", "image/png"),
                stream=streaming,
                safety_identifier="synthetic-request-user",
                user="legacy-user",
            )
        result = await pending if inspect.isawaitable(pending) else pending
        if isinstance(result, (Stream, AsyncStream)):
            events = [event async for event in result] if isinstance(result, AsyncStream) else list(result)
            assert len(events) == 1
            event = events[0]
            assert event.type == event_type
            assert isinstance(event, (ImageGenCompletedEvent, ImageEditCompletedEvent))
            assert event.safety_identifier == expected
        else:
            assert result.safety_identifier == expected
    finally:
        if isinstance(client, AsyncOpenAI):
            await client.close()
        else:
            client.close()
    assert len(requests) == 1
    request = requests[0]
    endpoint = "generations" if operation == "generate" else "edits"
    assert request.url.path == f"/v1/images/{endpoint}"
    assert request.method == "POST"
    if operation == "generate":
        body = json.loads(request.content)
        assert body["safety_identifier"] == "synthetic-request-user"
        assert body["user"] == "legacy-user"
    else:
        assert b'name="safety_identifier"\r\n\r\nsynthetic-request-user' in request.content
        assert b'name="user"\r\n\r\nlegacy-user' in request.content
