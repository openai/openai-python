from __future__ import annotations

import json

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from openai.types.responses import ParsedResponse
from openai.lib.streaming.responses import ResponseStreamEvent


async def _consume(
    sync: bool, events: list[dict[str, object]]
) -> tuple[list[ResponseStreamEvent[None]], ParsedResponse[None]]:
    body = "".join(
        f"data: {json.dumps({**event, 'sequence_number': index})}\n\n" for index, event in enumerate(events)
    ).encode()
    transport = httpx2.MockTransport(
        lambda _request: httpx2.Response(200, content=body, headers={"content-type": "text/event-stream"})
    )
    if sync:
        with OpenAI(api_key="fake-test-key", http_client=httpx2.Client(transport=transport)) as client:
            with client.responses.stream(model="test-model", input="test") as stream:
                return list(stream), stream.get_final_response()
    async with AsyncOpenAI(api_key="fake-test-key", http_client=httpx2.AsyncClient(transport=transport)) as client:
        async with client.responses.stream(model="test-model", input="test") as stream:
            emitted = [event async for event in stream]
            return emitted, await stream.get_final_response()


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("missing", [False, True], ids=["null", "missing"])
@pytest.mark.parametrize("index", [0, 1, 1_000_000], ids=["reused-index", "gap", "large-gap"])
@pytest.mark.parametrize("null_completion", [False, True])
async def test_stream_preserves_output_after_empty_item(
    sync: bool, missing: bool, index: int, null_completion: bool
) -> None:
    empty: dict[str, object] = {"type": "response.output_item.added", "output_index": 0}
    if not missing:
        empty["item"] = None
    text = '{"answer":4}'
    part: dict[str, object] = {"type": "output_text", "text": text, "annotations": [], "logprobs": []}
    message: dict[str, object] = {
        "id": "msg_test",
        "type": "message",
        "role": "assistant",
        "status": "completed",
        "content": [part],
    }
    tool = {
        "id": "fc_test",
        "type": "function_call",
        "call_id": "call_test",
        "name": "lookup",
        "arguments": text,
        "status": "completed",
    }
    events: list[dict[str, object]] = [
        {"type": "response.created", "response": {"id": "resp_test", "output": []}},
        empty,
        {
            "type": "response.output_item.added",
            "output_index": index,
            "item": {**message, "status": "in_progress", "content": []},
        },
        # An empty event must not remove an existing valid item.
        {**empty, "output_index": index},
        {
            "type": "response.output_item.added",
            "output_index": index + 1,
            "item": {**tool, "status": "in_progress", "arguments": ""},
        },
        {
            "type": "response.content_part.added",
            "output_index": index,
            "content_index": 0,
            "part": {**part, "text": ""},
        },
    ]
    for delta in ('{"answer":', "4}"):
        events.extend(
            [
                {
                    "type": "response.output_text.delta",
                    "output_index": index,
                    "content_index": 0,
                    "item_id": "msg_test",
                    "delta": delta,
                    "logprobs": [],
                },
                {
                    "type": "response.function_call_arguments.delta",
                    "output_index": index + 1,
                    "item_id": "fc_test",
                    "delta": delta,
                },
            ]
        )
    events.extend(
        [
            {
                "type": "response.output_text.done",
                "output_index": index,
                "content_index": 0,
                "item_id": "msg_test",
                "text": text,
                "logprobs": [],
            },
            {"type": "response.output_item.done", "output_index": index + 1, "item": tool},
            {"type": "response.output_item.done", "output_index": index, "item": message},
            {
                "type": "response.completed",
                "response": {
                    "id": "resp_test",
                    "status": "completed",
                    "output": None if null_completion else [message, tool],
                },
            },
        ]
    )
    emitted, final = await _consume(sync, events)
    assert len(emitted) == len(events)
    assert [event.snapshot for event in emitted if event.type == "response.output_text.delta"] == ['{"answer":', text]
    assert [event.snapshot for event in emitted if event.type == "response.function_call_arguments.delta"] == [
        '{"answer":',
        text,
    ]
    assert [event.output_index for event in emitted if event.type == "response.output_text.delta"] == [index] * 2
    assert final.output_text == text
    assert len(final.output) == 2
    final_message = final.output[0]
    assert final_message.type == "message" and final_message.id == "msg_test"
    final_tool = final.output[1]
    assert final_tool.type == "function_call" and final_tool.arguments == text
    assert final_tool.id == "fc_test"


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize(
    "event_type",
    [
        "response.content_part.added",
        "response.output_text.delta",
        "response.output_text.done",
        "response.function_call_arguments.delta",
    ],
)
async def test_stream_reports_content_without_an_output_item(sync: bool, event_type: str) -> None:
    with pytest.raises(RuntimeError, match="output index 0 before receiving its output item"):
        await _consume(
            sync,
            [
                {"type": "response.created", "response": {"id": "resp_test", "output": []}},
                {"type": "response.output_item.added", "output_index": 0, "item": None},
                {
                    "type": event_type,
                    "output_index": 0,
                    "content_index": 0,
                    "item_id": "msg_test",
                    "delta": "hello",
                    "text": "hello",
                    "part": {"type": "output_text", "text": ""},
                    "logprobs": [],
                },
            ],
        )


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_stream_keeps_initial_output_after_empty_item(sync: bool) -> None:
    message: dict[str, object] = {
        "id": "msg_test",
        "type": "message",
        "role": "assistant",
        "status": "in_progress",
        "content": [{"type": "output_text", "text": "", "annotations": [], "logprobs": []}],
    }
    emitted, _ = await _consume(
        sync,
        [
            {"type": "response.created", "response": {"id": "resp_test", "output": [message]}},
            {"type": "response.output_item.added", "output_index": 1, "item": None},
            {
                "type": "response.output_text.delta",
                "output_index": 0,
                "content_index": 0,
                "item_id": "msg_test",
                "delta": "hello",
                "logprobs": [],
            },
            {"type": "response.completed", "response": {"id": "resp_test", "output": []}},
        ],
    )
    assert [event.snapshot for event in emitted if event.type == "response.output_text.delta"] == ["hello"]


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("initial_output", ["empty", "null", "missing"])
@pytest.mark.parametrize("empty_added_event", [False, True])
async def test_stream_completes_with_only_empty_items(sync: bool, initial_output: str, empty_added_event: bool) -> None:
    response: dict[str, object] = {"id": "resp_test"}
    if initial_output != "missing":
        response["output"] = [] if initial_output == "empty" else None
    events: list[dict[str, object]] = [{"type": "response.created", "response": response}]
    if empty_added_event:
        events.append({"type": "response.output_item.added", "output_index": 0, "item": None})
    events.append({"type": "response.completed", "response": {"id": "resp_test", "output": None}})
    _, final = await _consume(sync, events)
    assert final.output == []
