from __future__ import annotations

from openai.lib.streaming._deltas import accumulate_delta as accumulate_chat_delta
from openai.lib.streaming._assistants import accumulate_delta as accumulate_assistant_delta


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
