from __future__ import annotations

import json
from typing import Any

import pytest
from jiter import from_json
from pydantic import BaseModel

from openai._models import construct_type_unchecked
from openai.types.chat import ChatCompletionChunk
from openai.lib.streaming.chat import ChatCompletionStreamState
from openai.lib.streaming._partial_json import PartialJSONParser


@pytest.mark.parametrize("step", [1, 2, 3, 7, 10, 1000])
@pytest.mark.parametrize(
    "document",
    [
        json.dumps({"path": "a.py", "content": 'quotes: " \\ /\n\t\r\b\f' * 5}),
        json.dumps({"nested": [1, -2.3, True, None, {"unicode": "😀 café 漢字"}]}),
        json.dumps({"unicode": "😀 café 漢字"}, ensure_ascii=False),
        '{"a": "\\uD800x"}',
        '{"a": "\\uDC00"}',
        '{"a": "\\uD800\\uDC00"}',
        '{"a": "\\u00xz"}',
        '{"a": "\\q"}',
        '{"a": "line\n"}',
        '{"a": "\ud800"}',
        '{"a": "unterminated',
        '{"a": [1, 2,',
        '{"a": 1e+2, "b": false}',
        '{"a": "first", "a": "second"}',
    ],
)
def test_partial_json_matches_jiter(document: str, step: int) -> None:
    parser = PartialJSONParser()
    for end in range(step, len(document) + step, step):
        value = document[:end]
        try:
            expected = from_json(value.encode("utf-8"), partial_mode=True)
        except (ValueError, UnicodeEncodeError) as exc:
            with pytest.raises(type(exc)) as actual:
                parser.parse(value)
            assert str(actual.value) == str(exc)
            # A failed stream ends here, as it does in the streaming helper.
            break
        else:
            assert parser.parse(value) == expected


def test_partial_json_does_not_share_mutable_values() -> None:
    parser = PartialJSONParser()
    prefix = '{"done": [1], "content": "'
    parsed = parser.parse(prefix)
    parsed["done"].append(2)
    assert parser.parse(prefix + "text") == {"done": [1]}


def test_partial_json_parses_fixed_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    from openai.lib.streaming import _partial_json

    lengths: list[int] = []

    def recording_parse(data: bytes, *, partial_mode: bool) -> Any:
        lengths.append(len(data))
        return from_json(data, partial_mode=partial_mode)

    monkeypatch.setattr(_partial_json, "from_json", recording_parse)
    parser = PartialJSONParser()
    prefix = '{"content": "'
    for size in range(0, 10000, 10):
        parser.parse(prefix + "a" * size)
    assert set(lengths) == {len(prefix)}
    assert parser.parse(prefix + "a" * 9990 + '"}') == {"content": "a" * 9990}


class Output(BaseModel):
    content: str


@pytest.mark.parametrize("tool", [False, True])
def test_stream_partial_json_events(tool: bool) -> None:
    tools: Any = [{"type": "function", "function": {"name": "write", "strict": True}}]
    state: ChatCompletionStreamState[Output] = (
        ChatCompletionStreamState(input_tools=tools) if tool else ChatCompletionStreamState(response_format=Output)
    )
    document = json.dumps({"content": 'line\nquote"slash\\😀' * 3})
    pieces = [document[:4], "", *[document[i : i + 3] for i in range(4, len(document), 3)]]
    accumulated = ""
    for index, piece in enumerate(pieces):
        accumulated += piece
        delta: dict[str, Any] = {"content": piece, "role": "assistant"}
        if tool:
            delta = {
                "tool_calls": [{"index": 0, "id": "call_test", "type": "function", "function": {"arguments": piece}}]
            }
            if index == 0:
                delta["tool_calls"][0]["function"]["name"] = "write"
        chunk = construct_type_unchecked(
            type_=ChatCompletionChunk,
            value={
                "id": "chat_test",
                "object": "chat.completion.chunk",
                "created": 0,
                "model": "test-model",
                "choices": [{"index": 0, "delta": delta, "finish_reason": None}],
            },
        )
        events = list(state.handle_chunk(chunk))
        if index == 0:
            continue  # Initial snapshots retain the helper's existing parsing behavior.
        event = events[-1]
        if tool:
            assert event.type == "tool_calls.function.arguments.delta"
            assert event.parsed_arguments == from_json(accumulated.encode(), partial_mode=True)
        else:
            assert event.type == "content.delta"
            assert event.parsed == from_json(accumulated.encode(), partial_mode=True)
    final = state.get_final_completion().choices[0].message
    if tool:
        assert final.tool_calls is not None
        assert final.tool_calls[0].type == "function"
        assert final.tool_calls[0].function.parsed_arguments == json.loads(document)
    else:
        assert final.parsed == Output(content=json.loads(document)["content"])


@pytest.mark.parametrize("tool", [False, True])
def test_interleaved_choices(tool: bool) -> None:
    tools: Any = [{"type": "function", "function": {"name": "write", "strict": True}}]
    state: ChatCompletionStreamState[Output] = (
        ChatCompletionStreamState(input_tools=tools) if tool else ChatCompletionStreamState(response_format=Output)
    )
    documents = [json.dumps({"content": str(i) * (8 + i)}) for i in range(2)]
    accumulated = ["", ""]
    for offset in range(max(map(len, documents))):
        choices: list[dict[str, Any]] = []
        for index, document in enumerate(documents):
            piece = document[offset : offset + 1]
            accumulated[index] += piece
            delta: dict[str, Any] = {"role": "assistant", "content": piece}
            if tool:
                function: dict[str, Any] = {"arguments": piece}
                call: dict[str, Any] = {"index": 0, "function": function}
                if offset == 0:
                    function["name"] = "write"
                    call.update(type="function", id=f"call_{index}")
                delta = {"tool_calls": [call]}
            choices.append({"index": index, "delta": delta, "finish_reason": None})
        chunk = construct_type_unchecked(
            type_=ChatCompletionChunk,
            value={"id": "test", "created": 0, "model": "test", "object": "chat.completion.chunk", "choices": choices},
        )
        list(state.handle_chunk(chunk))
        if offset == 0:
            continue
        for snapshot in state.current_completion_snapshot.choices:
            expected = from_json(accumulated[snapshot.index].encode(), partial_mode=True)
            if tool:
                assert snapshot.message.tool_calls is not None
                parsed_call = snapshot.message.tool_calls[0]
                assert parsed_call.type == "function"
                assert parsed_call.function.parsed_arguments == expected
            else:
                assert snapshot.message.parsed == expected
