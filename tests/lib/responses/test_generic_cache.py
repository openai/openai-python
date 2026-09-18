from __future__ import annotations

import json
import asyncio
import contextvars
from typing import Any

import httpx2
import pytest
from pydantic import BaseModel

from openai import OpenAI, AsyncOpenAI, _models
from openai.types.responses import ParsedResponse
from openai.lib.streaming.responses import ResponseStreamEvent


class Answer(BaseModel):
    value: int


def mock_response(request: httpx2.Request) -> httpx2.Response:
    part: dict[str, object] = {"type": "output_text", "text": '{"value":7}', "annotations": [], "logprobs": []}
    message: dict[str, object] = {
        "id": "msg_test",
        "type": "message",
        "role": "assistant",
        "status": "completed",
        "content": [part],
    }
    response: dict[str, object] = {
        "id": "resp_test",
        "object": "response",
        "created_at": 0,
        "model": "test-model",
        "status": "completed",
        "output": [message],
        "parallel_tool_calls": True,
        "tool_choice": "auto",
        "tools": [],
    }
    if not json.loads(request.content).get("stream"):
        return httpx2.Response(200, json=response)

    events: list[dict[str, Any]] = [
        {"type": "response.created", "response": {**response, "status": "in_progress", "output": []}},
        {
            "type": "response.output_item.added",
            "output_index": 0,
            "item": {**message, "status": "in_progress", "content": []},
        },
        {
            "type": "response.content_part.added",
            "output_index": 0,
            "content_index": 0,
            "item_id": "msg_test",
            "part": {**part, "text": ""},
        },
        {
            "type": "response.output_text.delta",
            "output_index": 0,
            "content_index": 0,
            "item_id": "msg_test",
            "delta": part["text"],
            "logprobs": [],
        },
        {
            "type": "response.output_text.done",
            "output_index": 0,
            "content_index": 0,
            "item_id": "msg_test",
            "text": part["text"],
            "logprobs": [],
        },
        {"type": "response.completed", "response": response},
    ]
    body = "".join(f"data: {json.dumps({**event, 'sequence_number': index})}\n\n" for index, event in enumerate(events))
    return httpx2.Response(200, headers={"content-type": "text/event-stream"}, content=body)


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("streaming", [False, True], ids=["parse", "stream"])
async def test_parsing_reuses_types_across_contexts(sync: bool, streaming: bool) -> None:
    response_types: set[tuple[type, type, type]] = set()
    event_types: set[type] = set()

    def check_response(response: ParsedResponse[Answer]) -> None:
        assert isinstance(response.output_parsed, Answer)
        assert response.output_parsed.value == 7
        message = response.output[0]
        assert message.type == "message"
        part = message.content[0]
        assert part.type == "output_text"
        assert isinstance(part.parsed, Answer)
        assert part.parsed.value == 7
        response_types.add((type(response), type(message), type(part)))

    def check_event(event: ResponseStreamEvent[Answer]) -> None:
        if event.type == "response.output_text.done":
            assert isinstance(event.parsed, Answer)
            assert event.parsed.value == 7
            event_types.add(type(event))

    transport = httpx2.MockTransport(mock_response)
    with OpenAI(api_key="fake-test-key", http_client=httpx2.Client(transport=transport)) as client:
        async with AsyncOpenAI(
            api_key="fake-test-key", http_client=httpx2.AsyncClient(transport=transport)
        ) as async_client:

            async def request() -> None:
                if sync:
                    if streaming:
                        with client.responses.stream(model="test-model", input="test", text_format=Answer) as stream:
                            for event in stream:
                                check_event(event)
                            check_response(stream.get_final_response())
                    else:
                        check_response(client.responses.parse(model="test-model", input="test", text_format=Answer))
                elif streaming:
                    async with async_client.responses.stream(
                        model="test-model", input="test", text_format=Answer
                    ) as async_stream:
                        async for event in async_stream:
                            check_event(event)
                        check_response(await async_stream.get_final_response())
                else:
                    check_response(
                        await async_client.responses.parse(model="test-model", input="test", text_format=Answer)
                    )

            # A task normally inherits its parent's context, which can hide this leak
            # by sharing Pydantic's generic cache. Start each request in an empty context.
            for _ in range(3):
                await contextvars.Context().run(asyncio.create_task, request())

            # Pydantic v1 has no TypeAdapter cache; it still exercises the behavior above.
            cache_info = getattr(getattr(_models, "_CachedTypeAdapter", None), "cache_info", None)
            before = cache_info().currsize if cache_info is not None else None
            for _ in range(10):
                await contextvars.Context().run(asyncio.create_task, request())
            if cache_info is not None:
                assert cache_info().currsize == before

    assert len(response_types) == 1
    if streaming:
        assert len(event_types) == 1
