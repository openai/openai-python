from __future__ import annotations

import json
import asyncio
from typing import Any
from unittest.mock import Mock, AsyncMock
from typing_extensions import override

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from openai._models import construct_type_unchecked
from openai.types.responses import (
    ParsedResponse,
    ResponseCreatedEvent,
    ResponseCompletedEvent as RawResponseCompletedEvent,
    ResponseFunctionToolCall,
    ResponseOutputItemDoneEvent,
    ResponseOutputItemAddedEvent,
)
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
@pytest.mark.parametrize(
    ("kind", "output", "identity"),
    [
        ("response.created", "missing", "changed"),
        ("response.queued", "null", "changed"),
        ("response.in_progress", "supplied", "changed"),
        ("response.failed", "null", "null"),
        ("response.incomplete", "missing", "missing"),
        ("response.completed", "missing", "changed"),
        ("response.completed", "null", "changed"),
        ("response.completed", "supplied", "changed"),
    ],
)
async def test_lifecycle_response_cannot_change_identity(sync: bool, kind: str, output: str, identity: str) -> None:
    item: dict[str, object] = {
        "id": "fc_identity",
        "type": "function_call",
        "call_id": "call_identity",
        "name": "lookup",
        "arguments": "{}",
        "status": "completed",
    }
    replacement: dict[str, object] = {"id": "resp_other", "status": "completed", "output": [item]}
    if output == "missing":
        del replacement["output"]
    if output == "null":
        replacement["output"] = None
    if identity == "missing":
        del replacement["id"]
    if identity == "null":
        replacement["id"] = None
    events: list[dict[str, object]] = [
        {"type": "response.created", "response": {"id": "resp_test", "output": []}},
        {"type": "response.output_item.added", "output_index": 3, "item": item},
        {"type": "response.output_item.done", "output_index": 3, "item": item},
        {"type": kind, "response": replacement},
    ]
    body = "".join(f"data: {json.dumps({**event, 'sequence_number': index})}\n\n" for index, event in enumerate(events))
    transport = httpx2.MockTransport(
        lambda _request: httpx2.Response(200, text=body, headers={"content-type": "text/event-stream"})
    )
    observed: list[int] = []
    with pytest.raises(RuntimeError, match="Lifecycle response identity changed"):
        if sync:
            with OpenAI(api_key="fake-test-key", http_client=httpx2.Client(transport=transport)) as client:
                with client.responses.stream(model="test-model", input="test") as stream:
                    observed.extend(event.sequence_number for event in stream)
                    stream.get_final_response()
        else:
            async with AsyncOpenAI(
                api_key="fake-test-key", http_client=httpx2.AsyncClient(transport=transport)
            ) as async_client:
                async with async_client.responses.stream(model="test-model", input="test") as async_stream:
                    async for event in async_stream:
                        observed.append(event.sequence_number)
                    await async_stream.get_final_response()
    assert observed == [0, 1, 2]


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
    assert len(emitted) == len(events) - 2
    assert [event.item.type for event in emitted if event.type == "response.output_item.added"] == [
        "message",
        "function_call",
    ]
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
            {
                "type": "response.output_item.done",
                "output_index": 0,
                "item": {**message, "status": "completed"},
            },
            {"type": "response.completed", "response": {"id": "resp_test", "output": None}},
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


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("index,terminal", [(0, "null"), (1_000_000, "null"), (7, "empty"), (7, "finished")])
async def test_final_output_rejects_unfinished_real_item(sync: bool, index: int, terminal: str) -> None:
    message: dict[str, object] = {
        "id": "msg_test",
        "type": "message",
        "role": "assistant",
        "status": "in_progress",
        "content": [],
    }
    tool = {
        "id": "fc_test",
        "type": "function_call",
        "call_id": "call_test",
        "name": "lookup",
        "arguments": "{}",
        "status": "completed",
    }
    with pytest.raises(RuntimeError, match="identity|unfinished.*output"):
        await _consume(
            sync,
            [
                {"type": "response.created", "response": {"id": "resp_test", "output": []}},
                {"type": "response.output_item.added", "output_index": index, "item": message},
                {"type": "response.output_item.added", "output_index": index + 1, "item": tool},
                {"type": "response.output_item.done", "output_index": index + 1, "item": tool},
                {
                    "type": "response.completed",
                    "response": {
                        "id": "resp_test",
                        "status": "completed",
                        "output": None if terminal == "null" else [] if terminal == "empty" else [tool],
                    },
                },
            ],
        )


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("terminal", ["null", "partial", "wrong", "complete"])
async def test_unfinished_item_remains_tracked_after_nonterminal_snapshot(sync: bool, terminal: str) -> None:
    message: dict[str, object] = {
        "id": "msg_test",
        "type": "message",
        "role": "assistant",
        "status": "completed",
        "content": [{"type": "output_text", "text": "done", "annotations": [], "logprobs": []}],
    }
    initial: dict[str, object] = {**message, "status": "in_progress", "content": []}
    tool = {
        "id": "fc_test",
        "type": "function_call",
        "call_id": "call_test",
        "name": "lookup",
        "arguments": "{}",
        "status": "completed",
    }
    output = (
        None
        if terminal == "null"
        else [message]
        if terminal == "partial"
        else [message, {**tool, "call_id": "other"}]
        if terminal == "wrong"
        else [message, tool]
    )
    events: list[dict[str, object]] = [
        {"type": "response.created", "response": {"id": "resp_test", "output": [initial]}},
        {"type": "response.output_item.added", "output_index": 99, "item": {**tool, "arguments": ""}},
        {"type": "response.in_progress", "response": {"id": "resp_test", "output": [initial]}},
        {"type": "response.output_item.done", "output_index": 0, "item": message},
        {"type": "response.completed", "response": {"id": "resp_test", "status": "completed", "output": output}},
    ]
    if terminal == "complete":
        _, final = await _consume(sync, events)
        assert final.output_text == "done"
        assert [item.type for item in final.output] == ["message", "function_call"]
    else:
        with pytest.raises(RuntimeError, match="unfinished.*output"):
            await _consume(sync, events)


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("terminal", ["null", "whole", "authoritative-omission"])
async def test_completed_items_survive_intermediate_omission_for_null_fallback(sync: bool, terminal: str) -> None:
    message: dict[str, object] = {
        "id": "msg_test",
        "type": "message",
        "role": "assistant",
        "status": "completed",
        "content": [{"type": "output_text", "text": "done", "annotations": [], "logprobs": []}],
    }
    initial: dict[str, object] = {**message, "status": "in_progress", "content": []}
    tool = {
        "id": "fc_test",
        "type": "function_call",
        "call_id": "call_test",
        "name": "lookup",
        "arguments": "{}",
        "status": "completed",
    }
    _, final = await _consume(
        sync,
        [
            {"type": "response.created", "response": {"id": "resp_test", "output": [initial]}},
            {"type": "response.output_item.added", "output_index": 99, "item": {**tool, "arguments": ""}},
            {"type": "response.output_item.done", "output_index": 99, "item": tool},
            {"type": "response.in_progress", "response": {"id": "resp_test", "output": [initial]}},
            {"type": "response.output_item.done", "output_index": 0, "item": message},
            {
                "type": "response.completed",
                "response": {
                    "id": "resp_test",
                    "status": "completed",
                    "output": None
                    if terminal == "null"
                    else [message]
                    if terminal == "authoritative-omission"
                    else [message, tool],
                },
            },
        ],
    )
    expected = ["message"] if terminal == "authoritative-omission" else ["message", "function_call"]
    assert [item.type for item in final.output] == expected
    assert final.output_text == "done"


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("missing", [False, True], ids=["null", "missing"])
async def test_typed_lifecycle_output_and_sparse_reintroduction(sync: bool, missing: bool) -> None:
    empty: dict[str, object] = {"id": "resp_test"}
    if not missing:
        empty["output"] = None
    tool = {
        "id": "fc_test",
        "type": "function_call",
        "call_id": "call_test",
        "name": "lookup",
        "arguments": "{}",
        "status": "completed",
    }
    initial = {**tool, "arguments": "", "status": "in_progress"}
    events, final = await _consume(
        sync,
        [
            {"type": "response.created", "response": empty},
            {"type": "response.queued", "response": empty},
            {"type": "response.in_progress", "response": empty},
            {"type": "response.incomplete", "response": empty},
            {"type": "response.failed", "response": empty},
            {"type": "response.output_item.added", "output_index": 99, "item": initial},
            {"type": "response.in_progress", "response": {"id": "resp_test", "output": []}},
            {"type": "response.in_progress", "response": {"id": "resp_test", "output": [initial]}},
            {"type": "response.function_call_arguments.delta", "output_index": 99, "item_id": "fc_test", "delta": "{}"},
            {"type": "response.output_item.done", "output_index": 99, "item": tool},
            {"type": "response.completed", "response": empty},
        ],
    )
    assert [
        [item.type for item in event.response.output]
        for event in events
        if (
            event.type == "response.created"
            or event.type == "response.queued"
            or event.type == "response.in_progress"
            or event.type == "response.incomplete"
            or event.type == "response.failed"
            or event.type == "response.completed"
        )
    ] == [
        [],
        [],
        [],
        [],
        [],
        [],
        ["function_call"],
        ["function_call"],
    ]
    assert [event.snapshot for event in events if event.type == "response.function_call_arguments.delta"] == ["{}"]
    assert [item.type for item in final.output] == ["function_call"]


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("terminal_type", ["response.failed", "response.incomplete"])
@pytest.mark.parametrize("output", ["missing", "null", "empty", "provided"])
async def test_failed_stream_retains_partial_output(sync: bool, terminal_type: str, output: str) -> None:
    message: dict[str, object] = {
        "id": "msg_test",
        "type": "message",
        "role": "assistant",
        "status": "in_progress",
        "content": [{"type": "output_text", "text": "partial", "annotations": [], "logprobs": []}],
    }
    tool: dict[str, object] = {
        "id": "fc_test",
        "type": "function_call",
        "call_id": "call_test",
        "name": "lookup",
        "arguments": "{}",
        "status": "in_progress",
    }
    terminal: dict[str, object] = {"id": "resp_test", "status": terminal_type.removeprefix("response.")}
    if output != "missing":
        terminal["output"] = None if output == "null" else [] if output == "empty" else [tool]
    events: list[dict[str, object]] = [
        {"type": "response.created", "response": {"id": "resp_test", "output": []}},
        {"type": "response.output_item.added", "output_index": 99, "item": {**message, "content": []}},
        {"type": "response.output_item.added", "output_index": 100, "item": {**tool, "arguments": ""}},
        {
            "type": "response.content_part.added",
            "output_index": 99,
            "content_index": 0,
            "part": {"type": "output_text", "text": "", "annotations": [], "logprobs": []},
        },
        {
            "type": "response.output_text.delta",
            "output_index": 99,
            "content_index": 0,
            "item_id": "msg_test",
            "delta": "partial",
            "logprobs": [],
        },
        {"type": "response.function_call_arguments.delta", "output_index": 100, "item_id": "fc_test", "delta": "{}"},
        {"type": terminal_type, "response": terminal},
    ]
    body = "".join(
        f"data: {json.dumps({**event, 'sequence_number': index})}\n\n" for index, event in enumerate(events)
    ).encode()
    transport = httpx2.MockTransport(
        lambda _request: httpx2.Response(200, content=body, headers={"content-type": "text/event-stream"})
    )
    if sync:
        with OpenAI(api_key="fake-test-key", http_client=httpx2.Client(transport=transport)) as client:
            with client.responses.stream(model="", input="test") as stream:
                emitted = list(stream)
                with pytest.raises(RuntimeError, match="Didn't receive a `response.completed` event"):
                    stream.get_final_response()
    else:
        async with AsyncOpenAI(
            api_key="fake-test-key", http_client=httpx2.AsyncClient(transport=transport)
        ) as async_client:
            async with async_client.responses.stream(model="", input="test") as async_stream:
                emitted = [event async for event in async_stream]
                with pytest.raises(RuntimeError, match="Didn't receive a `response.completed` event"):
                    await async_stream.get_final_response()
    response = next(
        event.response for event in emitted if event.type == "response.failed" or event.type == "response.incomplete"
    )
    expected: list[dict[str, object]] = [] if output == "empty" else [tool] if output == "provided" else [message, tool]
    assert len(response.output) == len(expected)
    for actual, wanted in zip(response.output, expected, strict=True):
        assert actual.id == wanted["id"]
        if actual.type == "message":
            assert actual.status == "in_progress"
            assert actual.content[0].type == "output_text"
            assert actual.content[0].text == "partial"
        else:
            assert actual.type == "function_call"
            assert actual.status == "in_progress"
            assert actual.arguments == "{}"


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_low_level_stream_retains_raw_lifecycle_placeholders(sync: bool) -> None:
    events = [
        {"type": "response.created", "sequence_number": 0, "response": {"id": "resp_test"}},
        {"type": "response.completed", "sequence_number": 1, "response": {"id": "resp_test", "output": None}},
    ]
    body = "".join(f"data: {json.dumps(event)}\n\n" for event in events).encode()
    transport = httpx2.MockTransport(
        lambda _request: httpx2.Response(200, content=body, headers={"content-type": "text/event-stream"})
    )
    if sync:
        with OpenAI(api_key="fake-test-key", http_client=httpx2.Client(transport=transport)) as client:
            raw = client.responses.create(model="", input="test", stream=True)
            received = list(raw)
    else:
        async with AsyncOpenAI(
            api_key="fake-test-key", http_client=httpx2.AsyncClient(transport=transport)
        ) as async_client:
            async_raw = await async_client.responses.create(model="", input="test", stream=True)
            received = [event async for event in async_raw]
    first, last = received
    assert first.type == "response.created" and last.type == "response.completed"
    assert "output" not in first.response.model_fields_set
    assert last.response.to_dict()["output"] is None
    assert "output" in last.response.model_fields_set


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("with_delta", [False, True])
async def test_omitted_sparse_output_can_continue_directly(sync: bool, with_delta: bool) -> None:
    tool = {
        "id": "fc_test",
        "type": "function_call",
        "call_id": "call_test",
        "name": "lookup",
        "arguments": "{}",
        "status": "completed",
    }
    events, final = await _consume(
        sync,
        [
            {"type": "response.created", "response": {"id": "resp_test", "output": []}},
            {"type": "response.output_item.added", "output_index": 99, "item": {**tool, "arguments": ""}},
            {"type": "response.in_progress", "response": {"id": "resp_test", "output": []}},
            *(
                [
                    {
                        "type": "response.function_call_arguments.delta",
                        "output_index": 99,
                        "item_id": "fc_test",
                        "delta": "{}",
                    }
                ]
                if with_delta
                else []
            ),
            {"type": "response.output_item.done", "output_index": 99, "item": tool},
            {"type": "response.completed", "response": {"id": "resp_test", "output": None}},
        ],
    )
    assert [event.response.output for event in events if event.type == "response.in_progress"] == [[]]
    assert [event.snapshot for event in events if event.type == "response.function_call_arguments.delta"] == (
        ["{}"] if with_delta else []
    )
    assert [item.type for item in final.output] == ["function_call"]
    assert final.output[0].to_dict()["arguments"] == "{}"


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_unfinished_sparse_index_cannot_be_reused_after_omission(sync: bool) -> None:
    tool = {
        "id": "fc_test",
        "type": "function_call",
        "call_id": "call_test",
        "name": "lookup",
        "arguments": "",
        "status": "in_progress",
    }
    with pytest.raises(RuntimeError, match="Duplicate response output index 99"):
        await _consume(
            sync,
            [
                {"type": "response.created", "response": {"id": "resp_test", "output": []}},
                {"type": "response.output_item.added", "output_index": 99, "item": tool},
                {"type": "response.in_progress", "response": {"id": "resp_test", "output": []}},
                {"type": "response.output_item.added", "output_index": 99, "item": {**tool, "id": "other"}},
                {"type": "response.output_item.done", "output_index": 99, "item": {**tool, "id": "other"}},
                {"type": "response.completed", "response": {"id": "resp_test", "output": None}},
            ],
        )


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_captured_output_item_events_preserve_unknown_api_fields(sync: bool) -> None:
    item = {
        "id": "fc_test",
        "type": "function_call",
        "call_id": "call_test",
        "name": "lookup",
        "arguments": "{}",
        "status": "completed",
    }
    emitted, _ = await _consume(
        sync,
        [
            {"type": "response.created", "response": {"id": "resp_test", "output": []}},
            {
                "type": "response.output_item.added",
                "output_index": 0,
                "item": item,
                "future_metadata": {"source": "added"},
            },
            {
                "type": "response.output_item.done",
                "output_index": 0,
                "item": item,
                "future_metadata": {"source": "done"},
            },
            {
                "type": "response.completed",
                "response": {"id": "resp_test", "status": "completed", "output": [item]},
            },
        ],
    )
    assert [
        event.to_dict().get("future_metadata")
        for event in emitted
        if event.type in ("response.output_item.added", "response.output_item.done")
    ] == [{"source": "added"}, {"source": "done"}]


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_native_done_event_keeps_captured_call_after_await(sync: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    flipped = False
    original = construct_type_unchecked(
        type_=ResponseFunctionToolCall,
        value={
            "type": "function_call",
            "id": "fc_one",
            "call_id": "call_one",
            "name": "record",
            "arguments": '{"value":"original"}',
            "status": "completed",
        },
    )
    changed = construct_type_unchecked(
        type_=ResponseFunctionToolCall,
        value={
            "type": "function_call",
            "id": "fc_one",
            "call_id": "call_one",
            "name": "record",
            "arguments": '{"value":"changed"}',
            "status": "completed",
        },
    )

    class MutableDoneEvent(ResponseOutputItemDoneEvent):
        @override
        def __getattribute__(self, name: str) -> Any:
            if flipped and name == "item":
                return changed
            if flipped and name == "output_index":
                return 0
            return super().__getattribute__(name)

    wire = [
        construct_type_unchecked(
            type_=ResponseCreatedEvent,
            value={"type": "response.created", "sequence_number": 0, "response": {"id": "resp_test", "output": []}},
        ),
        construct_type_unchecked(
            type_=ResponseOutputItemAddedEvent,
            value={"type": "response.output_item.added", "sequence_number": 1, "output_index": 99, "item": original},
        ),
        construct_type_unchecked(
            type_=MutableDoneEvent,
            value={"type": "response.output_item.done", "sequence_number": 2, "output_index": 99, "item": original},
        ),
        construct_type_unchecked(
            type_=RawResponseCompletedEvent,
            value={
                "type": "response.completed",
                "sequence_number": 3,
                "response": {"id": "resp_test", "status": "completed", "output": None},
            },
        ),
    ]

    class Transport:
        response = httpx2.Response(200)

        def __iter__(self) -> Any:
            return iter(wire)

        async def __aiter__(self) -> Any:
            for event in wire:
                yield event

    if sync:
        with OpenAI(api_key="fake-test-key") as client:
            monkeypatch.setattr(client.responses, "create", Mock(return_value=Transport()))
            with client.responses.stream(model="", input="read") as stream:
                done = next(event for event in stream if event.type == "response.output_item.done")
                await asyncio.sleep(0)
                flipped = True
                assert done.output_index == 99
                assert done.item.type == "function_call" and done.item.arguments == '{"value":"original"}'
                final = stream.get_final_response()
    else:
        async with AsyncOpenAI(api_key="fake-test-key") as async_client:
            monkeypatch.setattr(async_client.responses, "create", AsyncMock(return_value=Transport()))
            async with async_client.responses.stream(model="", input="read") as async_stream:
                async for event in async_stream:
                    if event.type == "response.output_item.done":
                        await asyncio.sleep(0)
                        flipped = True
                        assert event.output_index == 99
                        assert event.item.type == "function_call" and event.item.arguments == '{"value":"original"}'
                final = await async_stream.get_final_response()
    item = final.output[0]
    assert item.type == "function_call" and item.arguments == '{"value":"original"}'
