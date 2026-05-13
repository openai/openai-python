from __future__ import annotations

import json
from copy import deepcopy
from collections.abc import Callable

import pytest

from openai.types.chat import ChatCompletionChunk
from openai.lib.streaming.chat import ChatCompletionStreamState
from openai.lib.streaming._deltas import accumulate_delta as accumulate_chat_delta
from openai.lib.streaming._assistants import accumulate_delta as accumulate_assistant_delta

AccumulateDelta = Callable[[dict[object, object], dict[object, object]], dict[object, object]]


@pytest.mark.parametrize("accumulate_delta", [accumulate_chat_delta, accumulate_assistant_delta])
@pytest.mark.parametrize("initial_acc", [{}, {"tool_calls": None}])
def test_accumulate_delta_merges_duplicate_index_entries_in_initial_list(
    accumulate_delta: AccumulateDelta,
    initial_acc: dict[object, object],
) -> None:
    acc = deepcopy(initial_acc)

    accumulate_delta(
        acc,
        {
            "tool_calls": [
                {
                    "index": 0,
                    "id": "call_abc",
                    "function": {"name": "get_weather"},
                    "type": "function",
                },
                {
                    "index": 0,
                    "function": {"arguments": '{"city"'},
                },
            ]
        },
    )
    accumulate_delta(
        acc,
        {
            "tool_calls": [
                {
                    "index": 0,
                    "function": {"arguments": ': "London"}'},
                },
            ]
        },
    )

    tool_calls = acc["tool_calls"]
    assert isinstance(tool_calls, list)
    assert len(tool_calls) == 1

    arguments = tool_calls[0]["function"]["arguments"]
    assert arguments == '{"city": "London"}'
    assert json.loads(arguments) == {"city": "London"}


@pytest.mark.parametrize("accumulate_delta", [accumulate_chat_delta, accumulate_assistant_delta])
@pytest.mark.parametrize("initial_acc", [{}, {"content": None}])
def test_accumulate_delta_preserves_initial_primitive_lists(
    accumulate_delta: AccumulateDelta,
    initial_acc: dict[object, object],
) -> None:
    acc = deepcopy(initial_acc)

    accumulate_delta(acc, {"content": ["hello", " ", "world"]})

    assert acc["content"] == ["hello", " ", "world"]


def test_chat_stream_state_merges_duplicate_tool_call_indexes_in_first_chunk() -> None:
    state = ChatCompletionStreamState[object]()

    state.handle_chunk(
        ChatCompletionChunk(
            id="chatcmpl_123",
            created=1,
            model="gpt-4o",
            object="chat.completion.chunk",
            choices=[
                {
                    "index": 0,
                    "finish_reason": None,
                    "delta": {
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "index": 0,
                                "id": "call_abc",
                                "function": {"name": "get_weather"},
                                "type": "function",
                            },
                            {
                                "index": 0,
                                "function": {"arguments": '{"city"'},
                            },
                        ],
                    },
                }
            ],
        )
    )
    state.handle_chunk(
        ChatCompletionChunk(
            id="chatcmpl_123",
            created=1,
            model="gpt-4o",
            object="chat.completion.chunk",
            choices=[
                {
                    "index": 0,
                    "finish_reason": None,
                    "delta": {
                        "tool_calls": [
                            {
                                "index": 0,
                                "function": {"arguments": ': "London"}'},
                            },
                        ],
                    },
                }
            ],
        )
    )

    tool_calls = state.current_completion_snapshot.choices[0].message.tool_calls
    assert tool_calls is not None
    assert len(tool_calls) == 1
    assert tool_calls[0].function.arguments == '{"city": "London"}'
