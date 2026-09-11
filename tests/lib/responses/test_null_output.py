from __future__ import annotations

import json

import httpx2
import pytest
from pydantic import BaseModel

from openai import OpenAI, AsyncOpenAI
from openai.types.responses import ToolParam


class Answer(BaseModel):
    answer: int


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("terminal_output", ["null", "missing", "empty", "present"])
@pytest.mark.parametrize("has_items", [True, False], ids=["with-items", "without-items"])
async def test_stream_recovers_finalized_output(sync: bool, terminal_output: str, has_items: bool) -> None:
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
    if terminal_output != "missing":
        # A supplied list must win, even when it differs from the streamed items.
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
        return

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
