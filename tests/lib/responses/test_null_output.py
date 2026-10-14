from __future__ import annotations

import json

import httpx2
import pytest
from pydantic import BaseModel

from openai import OpenAI, AsyncOpenAI
from openai._types import omit
from openai._models import construct_type_unchecked
from openai.types.responses import Response, ToolParam
from openai.lib._parsing._responses import parse_response


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize(
    "identity",
    ["same", "changed", "enriched", "dropped", "replacement", "done-type", "done-id", "done-call", "done-enriched"],
)
async def test_retained_completed_call_identity(sync: bool, identity: str) -> None:
    item: dict[str, object] = {
        "type": "function_call",
        "call_id": "call_original",
        "name": "lookup",
        "arguments": "{}",
        "status": "completed",
        **({} if identity in ("enriched", "done-enriched") else {"id": "fc_original"}),
    }
    final_item = {
        **item,
        "id": "fc_final" if identity in ("changed", "enriched") else "fc_original",
        "call_id": "call_replacement" if identity == "replacement" else "call_original",
    }
    output = [] if identity == "dropped" else [final_item]
    done_item: dict[str, object] = item
    if identity.startswith("done-"):
        done_item = {**item, "id": "fc_final" if identity in ("done-id", "done-enriched") else "fc_original"}
        if identity == "done-call":
            done_item["call_id"] = "different"
        elif identity == "done-type":
            done_item = {"id": "msg", "type": "message", "role": "assistant", "status": "completed", "content": []}
        output = [done_item]
    events: list[dict[str, object]] = [
        {"type": "response.created", "response": {"id": "resp_test", "output": []}},
        {"type": "response.output_item.added", "output_index": 7, "item": item},
        {"type": "response.output_item.done", "output_index": 7, "item": done_item},
        {"type": "response.completed", "response": {"id": "resp_test", "status": "completed", "output": output}},
    ]
    body = "".join(
        f"data: {json.dumps({**event, 'sequence_number': index})}\n\n" for index, event in enumerate(events)
    ).encode()
    transport = httpx2.MockTransport(
        lambda _request: httpx2.Response(200, content=body, headers={"content-type": "text/event-stream"})
    )
    if sync:
        with OpenAI(api_key="fake-test-key", http_client=httpx2.Client(transport=transport)) as client:
            with client.responses.stream(model="test-model", input="test") as stream:
                if identity in ("changed", "done-type", "done-id", "done-call"):
                    with pytest.raises(RuntimeError, match="identity"):
                        stream.get_final_response()
                else:
                    final = stream.get_final_response()
                    assert [entry.to_dict() for entry in final.output] == [
                        {**entry, "parsed_arguments": None} for entry in output
                    ]
    else:
        async with AsyncOpenAI(
            api_key="fake-test-key", http_client=httpx2.AsyncClient(transport=transport)
        ) as async_client:
            async with async_client.responses.stream(model="test-model", input="test") as async_stream:
                if identity in ("changed", "done-type", "done-id", "done-call"):
                    with pytest.raises(RuntimeError, match="identity"):
                        await async_stream.get_final_response()
                else:
                    final = await async_stream.get_final_response()
                    assert [entry.to_dict() for entry in final.output] == [
                        {**entry, "parsed_arguments": None} for entry in output
                    ]


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("terminal", ["failed", "incomplete"])
@pytest.mark.parametrize("null_output", [False, True])
async def test_partial_terminal_uses_wire_order(sync: bool, terminal: str, null_output: bool) -> None:
    early: dict[str, object] = {
        "type": "function_call",
        "id": "fc_early",
        "call_id": "call_early",
        "name": "lookup",
        "arguments": "{",
        "status": "in_progress",
    }
    late: dict[str, object] = {
        "type": "message",
        "id": "msg_late",
        "role": "assistant",
        "status": "completed",
        "content": [{"type": "output_text", "text": "retained", "annotations": []}],
    }
    events: list[dict[str, object]] = [
        {"type": "response.created", "response": {"id": "resp_test", "output": []}},
        {"type": "response.output_item.added", "output_index": 7, "item": {**late, "content": []}},
        {"type": "response.output_item.added", "output_index": 3, "item": early},
        {"type": "response.output_item.done", "output_index": 7, "item": late},
        {
            "type": "response." + terminal,
            "response": {"id": "resp_test", "status": terminal, **({"output": None} if null_output else {})},
        },
    ]
    body = "".join(
        f"data: {json.dumps({**event, 'sequence_number': index})}\n\n" for index, event in enumerate(events)
    ).encode()
    transport = httpx2.MockTransport(
        lambda _request: httpx2.Response(200, content=body, headers={"content-type": "text/event-stream"})
    )
    if sync:
        with OpenAI(api_key="fake-test-key", http_client=httpx2.Client(transport=transport)) as client:
            with client.responses.stream(model="test-model", input="test") as stream:
                emitted = list(stream)
    else:
        async with AsyncOpenAI(
            api_key="fake-test-key", http_client=httpx2.AsyncClient(transport=transport)
        ) as async_client:
            async with async_client.responses.stream(model="test-model", input="test") as async_stream:
                emitted = [event async for event in async_stream]
    last = emitted[-1]
    assert last.type == "response.failed" or last.type == "response.incomplete"
    assert [item.id for item in last.response.output] == ["fc_early", "msg_late"]
    assert last.response.output[0].to_dict() == early
    assert last.response.output[1].to_dict() == late


class Answer(BaseModel):
    answer: int


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("terminal_output", ["null", "missing", "empty", "present"])
@pytest.mark.parametrize("has_items", [True, False], ids=["with-items", "without-items"])
@pytest.mark.parametrize("wire_text", [False, True])
async def test_stream_recovers_finalized_output(
    sync: bool, terminal_output: str, has_items: bool, wire_text: bool
) -> None:
    items: list[dict[str, object]] = (
        [
            {
                "id": "msg_test",
                "type": "message",
                "role": "assistant",
                "status": "completed",
                "content": [
                    {
                        "type": "output_text",
                        "text": '{"answer": 4}',
                        "annotations": [
                            {
                                "type": "url_citation",
                                "url": "https://example.com",
                                "title": "Example",
                                "start_index": 0,
                                "end_index": 1,
                            }
                        ],
                    },
                    {"type": "refusal", "refusal": "Final refusal"},
                ],
            },
            {
                "id": "fc_test",
                "type": "function_call",
                "call_id": "call_test",
                "name": "lookup",
                "arguments": '{"answer": 4}',
                "status": "completed",
            },
        ]
        if has_items
        else []
    )
    response: dict[str, object] = {"id": "resp_test", "status": "in_progress", "output": []}
    events: list[dict[str, object]] = [{"type": "response.created", "response": response}]
    for index, item in enumerate(items):
        added = {**item, "status": "in_progress"}
        if item["type"] == "message":
            added["content"] = []
        else:
            added["arguments"] = ""
        events.append({"type": "response.output_item.added", "output_index": index, "item": added})
    # Final items carry data absent from the live snapshot. Preserve output_index order.
    for index in reversed(range(len(items))):
        events.append({"type": "response.output_item.done", "output_index": index, "item": items[index]})
    completed: dict[str, object] = {
        "id": "resp_test",
        "status": "completed",
        "usage": {"input_tokens": 1, "output_tokens": 2, "total_tokens": 3},
    }
    if wire_text:
        completed["output_text"] = ""
    if terminal_output != "missing":
        completed["output"] = {"null": None, "empty": [], "present": items[:1]}[terminal_output]
    events.append({"type": "response.completed", "response": completed})
    body = "".join(
        f"data: {json.dumps({**event, 'sequence_number': index})}\n\n" for index, event in enumerate(events)
    ).encode()
    transport = httpx2.MockTransport(
        lambda _request: httpx2.Response(200, content=body, headers={"content-type": "text/event-stream"})
    )
    tools: list[ToolParam] = [{"type": "function", "name": "lookup", "parameters": {}, "strict": True}]
    if sync:
        with OpenAI(api_key="fake-test-key", http_client=httpx2.Client(transport=transport)) as client:
            with client.responses.stream(model="test-model", input="test", text_format=Answer, tools=tools) as stream:
                emitted = list(stream)
                final = stream.get_final_response()
    else:
        async with AsyncOpenAI(
            api_key="fake-test-key", http_client=httpx2.AsyncClient(transport=transport)
        ) as async_client:
            async with async_client.responses.stream(
                model="test-model", input="test", text_format=Answer, tools=tools
            ) as async_stream:
                emitted = [event async for event in async_stream]
                final = await async_stream.get_final_response()

    last_event = emitted[-1]
    assert last_event.type == "response.completed"
    assert last_event.response == final
    assert final.id == "resp_test"
    assert final.status == "completed"
    assert final.usage is not None and final.usage.total_tokens == 3
    if not has_items or terminal_output == "empty":
        assert final.output == []
        assert final.output_text == ""
        return

    assert final.output_text == '{"answer": 4}'
    assert len(final.output) == (1 if terminal_output == "present" else 2)
    message = final.output[0]
    assert message.type == "message" and message.status == "completed"
    assert message.id == "msg_test"
    assert final.output_parsed == Answer(answer=4)
    text = message.content[0]
    assert text.type == "output_text"
    citation = text.annotations[0]
    assert citation.type == "url_citation" and citation.url == "https://example.com"
    refusal = message.content[1]
    assert refusal.type == "refusal" and refusal.refusal == "Final refusal"
    if terminal_output != "present":
        tool = final.output[1]
        assert tool.type == "function_call" and tool.status == "completed"
        assert tool.id == "fc_test"
        assert tool.parsed_arguments == {"answer": 4}


def test_parse_response_with_null_message_content() -> None:
    response = construct_type_unchecked(
        type_=Response,
        value={
            "id": "resp_test",
            "status": "completed",
            "output": [
                {
                    "id": "msg_test",
                    "type": "message",
                    "role": "assistant",
                    "status": "completed",
                    "content": None,
                }
            ],
        },
    )

    parsed = parse_response(text_format=omit, input_tools=omit, response=response)

    assert len(parsed.output) == 1
    message = parsed.output[0]
    assert message.type == "message"
    assert message.content == []
