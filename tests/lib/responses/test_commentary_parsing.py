from __future__ import annotations

import json
import asyncio
import contextvars
from typing import Any

import httpx2
import pytest
from pydantic import BaseModel, ValidationError

from openai import OpenAI, AsyncOpenAI, omit, _models
from openai._types import Omit
from openai.types.responses import ParsedResponse
from openai.lib.streaming.responses import ResponseStreamEvent

# Pydantic v2 warns when serializing a response containing a future enum value.
# These probes retain the SDK's default warning behavior, rather than treating it
# as an error under the test suite's global warnings policy.
NON_FINAL_PHASES = [
    "commentary",
    pytest.param("future_phase", marks=pytest.mark.filterwarnings("ignore:Pydantic serializer warnings:UserWarning")),
]


class Result(BaseModel):
    answer: str


def _message(text: str, phase: str | None = "final_answer") -> dict[str, Any]:
    message: dict[str, Any] = {
        "id": f"msg_{phase}",
        "type": "message",
        "role": "assistant",
        "status": "completed",
        "phase": phase,
        "content": [{"type": "output_text", "text": text, "annotations": [], "logprobs": []}],
    }
    if phase == "missing":
        del message["phase"]
    return message


def _response(output: list[dict[str, Any]] | None) -> dict[str, Any]:
    return {
        "id": "resp_test",
        "object": "response",
        "created_at": 0,
        "model": "test-model",
        "status": "completed",
        "output": output,
        "parallel_tool_calls": True,
        "tool_choice": "auto",
        "tools": [],
    }


def _transport(response: httpx2.Response, *, structured: bool = True) -> httpx2.MockTransport:
    def respond(request: httpx2.Request) -> httpx2.Response:
        body = json.loads(request.content)
        if structured:
            assert body["text"]["format"] == {
                "type": "json_schema",
                "name": "Result",
                "strict": True,
                "schema": {
                    "title": "Result",
                    "type": "object",
                    "properties": {"answer": {"title": "Answer", "type": "string"}},
                    "required": ["answer"],
                    "additionalProperties": False,
                },
            }
        else:
            assert "format" not in body.get("text", {})
        return response

    return httpx2.MockTransport(respond)


async def _parse(
    sync: bool, output: list[dict[str, Any]], *, text_format: type[Result] | Omit = Result
) -> ParsedResponse[Result]:
    transport = _transport(httpx2.Response(200, json=_response(output)), structured=text_format is not omit)
    if sync:
        with OpenAI(api_key="fake-test-key", http_client=httpx2.Client(transport=transport)) as client:
            return client.responses.parse(model="test-model", input="test", text_format=text_format)
    async with AsyncOpenAI(api_key="fake-test-key", http_client=httpx2.AsyncClient(transport=transport)) as client:
        return await client.responses.parse(model="test-model", input="test", text_format=text_format)


def _events(
    commentary: str,
    final_text: str,
    completion: str = "supplied",
    *,
    commentary_phase: str = "commentary",
    final_phase: str | None = "final_answer",
) -> list[dict[str, Any]]:
    messages = [_message(commentary, commentary_phase), _message(final_text, final_phase)]
    tool = {"type": "function_call", "id": "fc_test", "call_id": "call_test", "name": "lookup", "arguments": "{}"}
    events: list[dict[str, Any]] = [{"type": "response.created", "response": _response([])}]
    for index, message in zip((0, 2), messages, strict=True):
        part = message["content"][0]
        events.extend(
            [
                {
                    "type": "response.output_item.added",
                    "output_index": index,
                    "item": {**message, "status": "in_progress", "content": []},
                },
                {
                    "type": "response.content_part.added",
                    "output_index": index,
                    "content_index": 0,
                    "part": {**part, "text": ""},
                },
                {
                    "type": "response.output_text.delta",
                    "output_index": index,
                    "content_index": 0,
                    "item_id": message["id"],
                    "delta": part["text"],
                    "logprobs": [],
                },
                {
                    "type": "response.output_text.done",
                    "output_index": index,
                    "content_index": 0,
                    "item_id": message["id"],
                    "text": part["text"],
                    "logprobs": [],
                },
                {"type": "response.output_item.done", "output_index": index, "item": message},
            ]
        )
        if index == 0:
            events.extend(
                [
                    {"type": "response.output_item.added", "output_index": 1, "item": tool},
                    {"type": "response.output_item.done", "output_index": 1, "item": tool},
                ]
            )
    response = _response([messages[0], tool, messages[1]])
    if completion == "null":
        response["output"] = None
    elif completion == "missing":
        del response["output"]
    elif completion == "empty":
        response["output"] = []
    events.append({"type": "response.completed", "response": response})
    return events


async def _stream(
    sync: bool, events: list[dict[str, Any]]
) -> tuple[list[ResponseStreamEvent[Result]], ParsedResponse[Result]]:
    body = "".join(f"data: {json.dumps({**event, 'sequence_number': i})}\n\n" for i, event in enumerate(events))
    transport = _transport(httpx2.Response(200, content=body, headers={"content-type": "text/event-stream"}))
    if sync:
        with OpenAI(api_key="fake-test-key", http_client=httpx2.Client(transport=transport)) as client:
            with client.responses.stream(model="test-model", input="test", text_format=Result) as stream:
                return list(stream), stream.get_final_response()
    async with AsyncOpenAI(api_key="fake-test-key", http_client=httpx2.AsyncClient(transport=transport)) as client:
        async with client.responses.stream(model="test-model", input="test", text_format=Result) as stream:
            emitted = [event async for event in stream]
            return emitted, await stream.get_final_response()


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("phase", ["final_answer", None, "missing"])
@pytest.mark.parametrize("commentary", [None, "Preparing.", '{"answer":"intermediate"}'])
@pytest.mark.parametrize("intermediate_phase", NON_FINAL_PHASES)
async def test_parse_skips_commentary(
    sync: bool, phase: str | None, commentary: str | None, intermediate_phase: str
) -> None:
    output = [_message('{"answer":"final"}', phase)]
    if commentary is not None:
        output.insert(0, _message(commentary, intermediate_phase))
    response = await _parse(sync, output)
    assert response.output_parsed == Result(answer="final")
    assert response.output_text == (commentary or "") + '{"answer":"final"}'
    for actual, expected in zip(response.output, output, strict=True):
        assert actual.type == "message"
        assert actual.phase == expected.get("phase")
        content = actual.content[0]
        assert content.type == "output_text"
        assert content.text == expected["content"][0]["text"]
        assert content.annotations == []
        assert content.parsed == (Result(answer="final") if actual.phase in (None, "final_answer") else None)


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("refusal", [False, True])
async def test_parse_does_not_use_commentary_without_a_final_result(sync: bool, refusal: bool) -> None:
    output = [_message('{"answer":"intermediate"}', "commentary")]
    if refusal:
        output.append({**_message(""), "content": [{"type": "refusal", "refusal": "Cannot comply"}]})
    response = await _parse(sync, output)
    assert response.output_parsed is None
    assert response.output_text == '{"answer":"intermediate"}'
    last_message = response.output[-1]
    assert last_message.type == "message"
    assert last_message.content[0].type == ("refusal" if refusal else "output_text")


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("text", ["not json", '{"wrong":"field"}'])
@pytest.mark.parametrize("phase", ["final_answer", None])
async def test_parse_still_rejects_invalid_final_output(sync: bool, text: str, phase: str | None) -> None:
    with pytest.raises(ValidationError):
        await _parse(sync, [_message('{"answer":"intermediate"}', "commentary"), _message(text, phase)])


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_parse_preserves_unphased_selection_and_unstructured_text(sync: bool) -> None:
    response = await _parse(sync, [_message('{"answer":"first"}', "missing"), _message('{"answer":"second"}', None)])
    assert response.output_parsed == Result(answer="first")
    response = await _parse(sync, [_message("Preparing.", "commentary"), _message("Done.")], text_format=omit)
    assert response.output_parsed is None
    assert response.output_text == "Preparing.Done."


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("commentary", ["Preparing.", '{"answer":"intermediate"}'])
@pytest.mark.parametrize("completion", ["supplied", "null", "missing", "empty"])
@pytest.mark.parametrize("intermediate_phase", NON_FINAL_PHASES)
async def test_stream_skips_commentary_without_losing_events(
    sync: bool, commentary: str, completion: str, intermediate_phase: str
) -> None:
    events = _events(commentary, '{"answer":"final"}', completion, commentary_phase=intermediate_phase)
    emitted, final = await _stream(sync, events)
    assert len(emitted) == len(events)
    deltas = [event for event in emitted if event.type == "response.output_text.delta"]
    assert [event.snapshot for event in deltas] == [commentary, '{"answer":"final"}']
    done = [event for event in emitted if event.type == "response.output_text.done"]
    assert [event.text for event in done] == [commentary, '{"answer":"final"}']
    assert [event.parsed for event in done] == [None, Result(answer="final")]
    completed = emitted[-1]
    assert completed.type == "response.completed"
    assert completed.response == final
    assert final.output_parsed == (None if completion == "empty" else Result(answer="final"))
    assert final.output_text == ("" if completion == "empty" else commentary + '{"answer":"final"}')
    if completion != "empty":
        assert final.output[0].type == "message"
        assert final.output[0].content[0].type == "output_text"
        assert final.output[0].content[0].parsed is None
        assert final.output[1].type == "function_call"
        assert final.output[1].arguments == "{}"


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_stream_parses_completion_without_text_done_events(sync: bool) -> None:
    events = _events("Preparing.", '{"answer":"final"}')
    _, response = await _stream(sync, [events[0], events[-1]])
    assert response.output_parsed == Result(answer="final")


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("completion_only", [False, True])
@pytest.mark.parametrize("text", ["not json", '{"wrong":"field"}'])
async def test_stream_still_rejects_invalid_final_output(sync: bool, completion_only: bool, text: str) -> None:
    events = _events('{"answer":"intermediate"}', text)
    if completion_only:
        events = [events[0], events[-1]]
    with pytest.raises(ValidationError):
        await _stream(sync, events)


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("phase", [None, "missing", "final_answer"])
async def test_stream_preserves_legacy_and_final_phase_parsing(sync: bool, phase: str | None) -> None:
    events = _events("Preparing.", '{"answer":"final"}', final_phase=phase)
    emitted, response = await _stream(sync, events)
    done = [event for event in emitted if event.type == "response.output_text.done"]
    assert [event.parsed for event in done] == [None, Result(answer="final")]
    assert response.output_parsed == Result(answer="final")


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("streaming", [False, True], ids=["parse", "stream-completion"])
@pytest.mark.parametrize("phase", NON_FINAL_PHASES)
@pytest.mark.parametrize("final_kind", ["text", "refusal", "absent"])
async def test_phase_selection_preserves_content(sync: bool, streaming: bool, phase: str, final_kind: str) -> None:
    # Unknown phases probe forward compatibility; they do not represent a known live model.
    intermediate = _message('{"answer":"intermediate"}', phase)
    intermediate["content"].append({"type": "output_text", "text": "Still working.", "annotations": []})
    output = [intermediate]
    if final_kind != "absent":
        final = _message('{"answer":"final"}')
        if final_kind == "refusal":
            final["content"] = [{"type": "refusal", "refusal": "Cannot comply"}]
        output.extend([final, {**intermediate, "id": "msg_after_final"}])
    if streaming:
        _, response = await _stream(
            sync,
            [
                {"type": "response.created", "response": _response([])},
                {"type": "response.completed", "response": _response(output)},
            ],
        )
    else:
        response = await _parse(sync, output)
    assert response.output_parsed == (Result(answer="final") if final_kind == "text" else None)
    for actual, expected in zip(response.output, output, strict=True):
        assert actual.type == "message"
        assert actual.phase == expected["phase"]
        for content, raw in zip(actual.content, expected["content"], strict=True):
            if content.type == "output_text":
                assert content.text == raw["text"]
                assert content.parsed == (Result(answer="final") if actual.phase == "final_answer" else None)
            else:
                assert content.refusal == raw["refusal"]


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("streaming", [False, True], ids=["parse", "stream"])
async def test_parsing_reuses_types_across_contexts(sync: bool, streaming: bool) -> None:
    response_types: set[tuple[type, type, type]] = set()
    event_types: set[type] = set()

    async def request() -> None:
        if streaming:
            emitted, response = await _stream(sync, _events("Preparing.", '{"answer":"final"}'))
            done = [event for event in emitted if event.type == "response.output_text.done"]
            assert [event.parsed for event in done] == [None, Result(answer="final")]
            event_types.update(type(event) for event in done)
        else:
            response = await _parse(sync, [_message('{"answer":"final"}')])
        assert response.output_parsed == Result(answer="final")
        message = response.output[-1]
        assert message.type == "message"
        part = message.content[0]
        assert part.type == "output_text"
        assert part.parsed == Result(answer="final")
        response_types.add((type(response), type(message), type(part)))

    # Inherited contexts can share Pydantic's generic cache and hide the leak.
    for _ in range(3):
        await contextvars.Context().run(asyncio.create_task, request())

    # Pydantic v1 has no TypeAdapter cache, but still exercises type reuse below.
    cache_info = getattr(getattr(_models, "_CachedTypeAdapter", None), "cache_info", None)
    before = cache_info().currsize if cache_info is not None else None
    for _ in range(10):
        await contextvars.Context().run(asyncio.create_task, request())
    if cache_info is not None:
        assert cache_info().currsize == before
    assert len(response_types) == 1
    if streaming:
        assert len(event_types) == 1
