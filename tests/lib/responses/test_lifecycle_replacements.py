import json
from contextlib import nullcontext

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("terminal", ["null", "missing"])
@pytest.mark.parametrize("duplicate", [False, True], ids=["replacement", "duplicate"])
@pytest.mark.parametrize("tool_id", ["present", "null", "missing", "changed", "dropped"])
async def test_final_output_keeps_completed_lifecycle_replacements(
    sync: bool, terminal: str, duplicate: bool, tool_id: str
) -> None:
    message: dict[str, object] = {
        "id": "msg_fixture",
        "type": "message",
        "role": "assistant",
        "status": "completed",
        "content": [{"type": "output_text", "text": "Original result", "annotations": []}],
    }
    tool: dict[str, object] = {
        "type": "function_call",
        "call_id": "call_fixture",
        "name": "lookup",
        "arguments": '{"answer":4}',
        "status": "completed",
    }
    if tool_id != "missing":
        tool["id"] = None if tool_id == "null" else "fc_fixture"
    updated_message: dict[str, object] = {
        **message,
        "content": [{"type": "output_text", "text": "Updated result", "annotations": []}],
    }
    updated_tool: dict[str, object] = {**tool, "id": "fc_fixture", "arguments": '{"answer":5}'}
    if tool_id == "changed":
        updated_tool["id"] = "fc_other"
    elif tool_id == "dropped":
        del updated_tool["id"]
    events: list[dict[str, object]] = [
        {"type": "response.created", "response": {"id": "resp_fixture", "output": []}},
        {"type": "response.output_item.added", "output_index": 3, "item": message},
        {"type": "response.output_item.done", "output_index": 3, "item": message},
        {"type": "response.output_item.added", "output_index": 7, "item": tool},
        {"type": "response.output_item.done", "output_index": 7, "item": tool},
        {
            "type": "response.in_progress",
            "response": {
                "id": "resp_fixture",
                "output": [updated_tool, updated_message] + ([updated_message] if duplicate else []),
            },
        },
        {
            "type": "response.queued",
            "response": {
                "id": "resp_fixture",
                "output": [{**updated_tool, "arguments": '{"answer":6}'}],
            },
        },
        {
            "type": "response.in_progress",
            "response": {
                "id": "resp_fixture",
                "output": [updated_tool],
            },
        },
        {
            "type": "response.completed",
            "response": {
                "id": "resp_fixture",
                "status": "completed",
                **({"output": None} if terminal == "null" else {}),
            },
        },
    ]
    body = "".join(f"data: {json.dumps({**event, 'sequence_number': index})}\n\n" for index, event in enumerate(events))
    transport = httpx2.MockTransport(
        lambda _: httpx2.Response(200, text=body, headers={"content-type": "text/event-stream"})
    )
    refused = duplicate or tool_id in ("changed", "dropped")
    with pytest.raises(RuntimeError, match="conflicting output identities") if refused else nullcontext():
        if sync:
            with OpenAI(api_key="synthetic-key", http_client=httpx2.Client(transport=transport)) as client:
                with client.responses.stream(model="fixture", input="Read the stream.") as stream:
                    result = stream.get_final_response()
        else:
            async with AsyncOpenAI(
                api_key="synthetic-key", http_client=httpx2.AsyncClient(transport=transport)
            ) as async_client:
                async with async_client.responses.stream(model="fixture", input="Read the stream.") as async_stream:
                    result = await async_stream.get_final_response()
    if refused:
        return
    assert len(result.output) == 2
    first, second = result.output
    assert first.type == "message"
    assert first.id == "msg_fixture"
    assert first.content[0].type == "output_text"
    assert first.content[0].text == "Updated result"
    assert second.type == "function_call"
    assert second.id == "fc_fixture"
    assert second.arguments == '{"answer":5}'
    assert result.output_text == "Updated result"


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("tool_id", ["acquired", "changed", "dropped"])
async def test_assigned_id_survives_final_replacement_without_done(sync: bool, tool_id: str) -> None:
    tool: dict[str, object] = {
        "type": "function_call",
        "call_id": "call_fixture",
        "name": "lookup",
        "arguments": "",
        **({} if tool_id == "acquired" else {"id": "fc_fixture"}),
    }
    final_tool = {**tool, "id": "fc_other", "arguments": '{"answer":5}', "status": "completed"}
    if tool_id == "dropped":
        del final_tool["id"]
    events: list[dict[str, object]] = [
        {"type": "response.created", "response": {"id": "resp_fixture", "output": []}},
        {"type": "response.output_item.added", "output_index": 4, "item": tool},
        {
            "type": "response.completed",
            "response": {"id": "resp_fixture", "status": "completed", "output": [final_tool]},
        },
    ]
    body = "".join(f"data: {json.dumps({**event, 'sequence_number': index})}\n\n" for index, event in enumerate(events))
    transport = httpx2.MockTransport(
        lambda _: httpx2.Response(200, text=body, headers={"content-type": "text/event-stream"})
    )
    with pytest.raises(RuntimeError, match="unfinished output items") if tool_id != "acquired" else nullcontext():
        if sync:
            with OpenAI(api_key="synthetic-key", http_client=httpx2.Client(transport=transport)) as client:
                with client.responses.stream(model="fixture", input="Read the stream.") as stream:
                    result = stream.get_final_response()
        else:
            async with AsyncOpenAI(
                api_key="synthetic-key", http_client=httpx2.AsyncClient(transport=transport)
            ) as client_async:
                async with client_async.responses.stream(model="fixture", input="Read the stream.") as stream_async:
                    result = await stream_async.get_final_response()
    if tool_id == "acquired":
        assert len(result.output) == 1
        item = result.output[0]
        assert item.type == "function_call"
        assert item.id == "fc_other"
        assert item.arguments == '{"answer":5}'


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("position", ["same-index", "different-index", "reuse-previous"])
async def test_completed_identity_belongs_to_one_sparse_position(sync: bool, position: str) -> None:
    tool: dict[str, object] = {
        "type": "function_call",
        "call_id": "call_fixture",
        "name": "lookup",
        "arguments": '{"answer":4}',
        "status": "completed",
    }
    updated = {**tool, "id": "fc_fixture", "arguments": '{"answer":5}'}
    events: list[dict[str, object]] = [
        {"type": "response.created", "response": {"id": "resp_fixture", "output": []}},
        {"type": "response.output_item.done", "output_index": 7, "item": tool},
        *(
            [{"type": "response.output_item.done", "output_index": 7, "item": {**tool, "call_id": "call_other"}}]
            if position == "reuse-previous"
            else []
        ),
        {
            "type": "response.output_item.done",
            "output_index": 7 if position == "same-index" else 19,
            "item": tool,
        },
        {"type": "response.in_progress", "response": {"id": "resp_fixture", "output": [updated]}},
        {"type": "response.completed", "response": {"id": "resp_fixture", "status": "completed", "output": None}},
    ]
    body = "".join(f"data: {json.dumps({**event, 'sequence_number': index})}\n\n" for index, event in enumerate(events))
    transport = httpx2.MockTransport(
        lambda _: httpx2.Response(200, text=body, headers={"content-type": "text/event-stream"})
    )
    completed: list[int] = []
    with (
        pytest.raises(RuntimeError, match="conflicting output identities")
        if position == "different-index"
        else nullcontext()
    ):
        if sync:
            with OpenAI(api_key="synthetic-key", http_client=httpx2.Client(transport=transport)) as client:
                with client.responses.stream(model="fixture", input="Read the stream.") as stream:
                    for event in stream:
                        if event.type == "response.output_item.done":
                            completed.append(event.output_index)
                    result = stream.get_final_response()
        else:
            async with AsyncOpenAI(
                api_key="synthetic-key", http_client=httpx2.AsyncClient(transport=transport)
            ) as client_async:
                async with client_async.responses.stream(model="fixture", input="Read the stream.") as stream_async:
                    async for event in stream_async:
                        if event.type == "response.output_item.done":
                            completed.append(event.output_index)
                    result = await stream_async.get_final_response()
    if position == "different-index":
        assert completed == [7], "Do not emit the duplicate or process its lifecycle snapshot."
    else:
        assert completed == ([7, 7, 19] if position == "reuse-previous" else [7, 7])
        assert len(result.output) == (2 if position == "reuse-previous" else 1)
        last = result.output[-1]
        assert last.type == "function_call" and last.call_id == "call_fixture"
        assert last.id == "fc_fixture" and last.arguments == '{"answer":5}'
