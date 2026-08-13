from __future__ import annotations

from typing import cast

from openai.types.chat import ChatCompletionChunk
from openai.lib.streaming.chat import ChatCompletionStreamState
from openai.lib.streaming._deltas import accumulate_delta as accumulate_chat_delta
from openai.lib.streaming._assistants import accumulate_delta as accumulate_assistant_delta
from openai.types.chat.chat_completion_chunk import (
    Choice,
    ChoiceDelta,
    ChoiceDeltaToolCall,
    ChoiceDeltaToolCallFunction,
)


def test_accumulate_delta_merges_duplicate_indexed_entries_on_initial_chunk() -> None:
    acc: dict[object, object] = {"tool_calls": None}

    accumulate_chat_delta(
        acc,
        {
            "tool_calls": [
                {
                    "index": 0,
                    "id": "call_abc",
                    "function": {"name": "get_weather"},
                    "type": "function",
                },
                {"index": 0, "function": {"arguments": '{"city"'}},
            ]
        },
    )
    accumulate_chat_delta(acc, {"tool_calls": [{"index": 0, "function": {"arguments": ': "London"}'}}]})

    assert acc == {
        "tool_calls": [
            {
                "index": 0,
                "id": "call_abc",
                "function": {"name": "get_weather", "arguments": '{"city": "London"}'},
                "type": "function",
            }
        ]
    }


def test_chat_completion_state_merges_duplicate_indexed_entries_on_initial_chunk() -> None:
    state = ChatCompletionStreamState()

    state.handle_chunk(
        ChatCompletionChunk(
            id="chatcmpl_abc",
            choices=[
                Choice(
                    delta=ChoiceDelta(
                        role="assistant",
                        tool_calls=[
                            ChoiceDeltaToolCall(
                                index=0,
                                id="call_abc",
                                function=ChoiceDeltaToolCallFunction(name="get_weather", arguments='{"city"'),
                                type="function",
                            ),
                            ChoiceDeltaToolCall(
                                index=0,
                                function=ChoiceDeltaToolCallFunction(arguments=': "London"}'),
                            ),
                        ],
                    ),
                    finish_reason=None,
                    index=0,
                    logprobs=None,
                )
            ],
            created=1,
            model="gpt-test",
            object="chat.completion.chunk",
        )
    )
    state.handle_chunk(
        ChatCompletionChunk(
            id="chatcmpl_abc",
            choices=[
                Choice(delta=ChoiceDelta(), finish_reason="tool_calls", index=0, logprobs=None),
            ],
            created=1,
            model="gpt-test",
            object="chat.completion.chunk",
        )
    )

    tool_calls = state.get_final_completion().choices[0].message.tool_calls
    assert tool_calls is not None
    assert len(tool_calls) == 1
    assert tool_calls[0].id == "call_abc"
    assert tool_calls[0].function.name == "get_weather"
    assert tool_calls[0].function.arguments == '{"city": "London"}'


def test_assistant_accumulate_delta_uses_logical_index_for_initial_chunk() -> None:
    acc: dict[object, object] = {}

    accumulate_assistant_delta(
        acc,
        {
            "tool_calls": [
                {"index": 0, "id": "call_abc", "function": {"name": "get_weather"}, "type": "function"},
                {"index": 0, "function": {"arguments": '{"path"'}},
                {"index": 1, "id": "call_def", "function": {"name": "list_files"}, "type": "function"},
            ]
        },
    )
    accumulate_assistant_delta(
        acc,
        {
            "tool_calls": [
                {"index": 1, "function": {"arguments": '{"limit": 10}'}},
                {"index": 0, "function": {"arguments": ': "."}'}},
            ]
        },
    )

    assert acc == {
        "tool_calls": [
            {
                "index": 0,
                "id": "call_abc",
                "function": {"name": "get_weather", "arguments": '{"path": "."}'},
                "type": "function",
            },
            {
                "index": 1,
                "id": "call_def",
                "function": {"name": "list_files", "arguments": '{"limit": 10}'},
                "type": "function",
            },
        ]
    }


def test_assistant_accumulate_delta_merges_indexed_delta_into_full_snapshot() -> None:
    acc: dict[object, object] = {
        "tool_calls": [
            {
                "id": "call_abc",
                "function": {"name": "get_weather", "arguments": ""},
                "type": "function",
            }
        ]
    }

    accumulate_assistant_delta(
        acc,
        {"tool_calls": [{"index": 0, "function": {"arguments": '{"city": "London"}'}}]},
    )

    tool_calls = cast(list[object], acc["tool_calls"])
    assert len(tool_calls) == 1
    assert tool_calls[0] == {
        "index": 0,
        "id": "call_abc",
        "function": {"name": "get_weather", "arguments": '{"city": "London"}'},
        "type": "function",
    }
