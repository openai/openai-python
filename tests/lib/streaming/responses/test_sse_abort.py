from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from openai.lib.streaming.responses._sse_abort import (
    ResponsesSSEStream,
    AsyncResponsesSSEStream,
    _function_call_item_to_param,
    _track_response_event,
)


def test_function_call_item_to_param() -> None:
    param = _function_call_item_to_param(
        {
            "type": "function_call",
            "id": "fc_1",
            "call_id": "call_1",
            "name": "get_weather",
            "arguments": '{"city":"AMS"}',
            "status": "in_progress",
        }
    )
    assert param == {
        "type": "function_call",
        "id": "fc_1",
        "call_id": "call_1",
        "name": "get_weather",
        "arguments": '{"city":"AMS"}',
        "status": "in_progress",
    }


def test_track_response_event_buffers_function_call() -> None:
    pending: dict[str, dict[str, Any]] = {}
    event = MagicMock(
        type="response.output_item.added",
        item=MagicMock(
            type="function_call",
            id="fc_1",
            call_id="call_1",
            name="get_weather",
            arguments="",
            status="in_progress",
            model_dump=lambda exclude_unset=True: {
                "type": "function_call",
                "id": "fc_1",
                "call_id": "call_1",
                "name": "get_weather",
                "arguments": "",
                "status": "in_progress",
            },
        ),
    )
    assert _track_response_event(event=event, pending=pending) is False
    assert "call_1" in pending


def _function_call_sse_body() -> bytes:
    events = [
        {
            "type": "response.created",
            "response": {"id": "resp_test", "output": []},
            "sequence_number": 0,
        },
        {
            "type": "response.output_item.added",
            "output_index": 0,
            "sequence_number": 1,
            "item": {
                "id": "fc_test",
                "type": "function_call",
                "call_id": "call_test",
                "name": "get_weather",
                "arguments": "",
                "status": "in_progress",
            },
        },
    ]
    return "".join(f"data: {json.dumps(event)}\n\n" for event in events).encode()


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_aborted_stream_commits_function_call_to_conversation(sync: bool, respx_mock: Any = None) -> None:
    body = _function_call_sse_body()
    committed: list[dict[str, Any]] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        path = request.url.path
        if path.endswith("/responses") and request.method == "POST":
            return httpx2.Response(200, content=body, headers={"content-type": "text/event-stream"})
        if "/conversations/" in path and path.endswith("/items") and request.method == "POST":
            payload = json.loads(request.content.decode())
            committed.extend(payload.get("items", []))
            return httpx2.Response(
                200,
                json={"object": "list", "data": payload.get("items", []), "first_id": None, "last_id": None, "has_more": False},
            )
        return httpx2.Response(404, json={"error": {"message": f"unexpected {request.method} {path}"}})

    transport = httpx2.MockTransport(handler)

    if sync:
        with OpenAI(api_key="fake-test-key", http_client=httpx2.Client(transport=transport)) as client:
            stream = client.responses.create(
                model="test-model",
                input="weather?",
                conversation="conv_test",
                stream=True,
                tools=[{"type": "function", "name": "get_weather", "parameters": {"type": "object", "properties": {}}}],
            )
            assert isinstance(stream, ResponsesSSEStream)
            for event in stream:
                if getattr(event, "type", None) == "response.output_item.added":
                    stream.close()
                    break
        assert committed == [
            {
                "type": "function_call",
                "id": "fc_test",
                "call_id": "call_test",
                "name": "get_weather",
                "arguments": "",
                "status": "in_progress",
            }
        ]
    else:
        async with AsyncOpenAI(api_key="fake-test-key", http_client=httpx2.AsyncClient(transport=transport)) as client:
            stream = await client.responses.create(
                model="test-model",
                input="weather?",
                conversation="conv_test",
                stream=True,
                tools=[{"type": "function", "name": "get_weather", "parameters": {"type": "object", "properties": {}}}],
            )
            assert isinstance(stream, AsyncResponsesSSEStream)
            async for event in stream:
                if getattr(event, "type", None) == "response.output_item.added":
                    await stream.close()
                    break
        assert committed == [
            {
                "type": "function_call",
                "id": "fc_test",
                "call_id": "call_test",
                "name": "get_weather",
                "arguments": "",
                "status": "in_progress",
            }
        ]
