from __future__ import annotations

import json

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI


def _null_content_item() -> dict[str, object]:
    return {
        "id": "msg_test",
        "type": "message",
        "role": "assistant",
        "status": "completed",
        "content": None,
    }


def _completed_event(output: object) -> dict[str, object]:
    return {
        "type": "response.completed",
        "sequence_number": 1,
        "response": {
            "id": "resp_test",
            "status": "completed",
            "model": "test-model",
            "output": output,
        },
    }


def _stream_body(output: object) -> bytes:
    events: list[dict[str, object]] = [
        {"type": "response.created", "sequence_number": 0, "response": {"id": "resp_test", "status": "in_progress"}},
        _completed_event(output),
    ]
    return "".join(f"data: {json.dumps(event)}\n\n" for event in events).encode()


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_stream_explicit_null_message_content(sync: bool) -> None:
    """An explicit completed output whose message has content:null must parse to empty content, not TypeError."""
    transport = httpx2.MockTransport(
        lambda _request: httpx2.Response(
            200, content=_stream_body([_null_content_item()]), headers={"content-type": "text/event-stream"}
        )
    )
    if sync:
        with OpenAI(api_key="fake-test-key", http_client=httpx2.Client(transport=transport)) as client:
            with client.responses.stream(model="test-model", input="test") as stream:
                list(stream)
                final = stream.get_final_response()
    else:
        async with AsyncOpenAI(
            api_key="fake-test-key", http_client=httpx2.AsyncClient(transport=transport)
        ) as async_client:
            async with async_client.responses.stream(model="test-model", input="test") as async_stream:
                [event async for event in async_stream]
                final = await async_stream.get_final_response()

    assert len(final.output) == 1
    message = final.output[0]
    assert message.type == "message"
    assert message.content == []


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_parse_null_message_content(sync: bool) -> None:
    """Non-streaming responses.parse must not raise TypeError on content:null either."""
    body = json.dumps(
        {
            "id": "resp_test",
            "object": "response",
            "created_at": 1,
            "model": "test-model",
            "status": "completed",
            "parallel_tool_calls": False,
            "tool_choice": "auto",
            "tools": [],
            "output": [_null_content_item()],
        }
    )
    transport = httpx2.MockTransport(
        lambda _request: httpx2.Response(200, content=body, headers={"content-type": "application/json"})
    )
    if sync:
        with OpenAI(api_key="fake-test-key", http_client=httpx2.Client(transport=transport)) as client:
            parsed = client.responses.parse(model="test-model", input="test")
    else:
        async with AsyncOpenAI(
            api_key="fake-test-key", http_client=httpx2.AsyncClient(transport=transport)
        ) as async_client:
            parsed = await async_client.responses.parse(model="test-model", input="test")

    assert len(parsed.output) == 1
    message = parsed.output[0]
    assert message.type == "message"
    assert message.content == []
