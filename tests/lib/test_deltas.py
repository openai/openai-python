from __future__ import annotations

from typing import Any, cast

from openai.lib.streaming._deltas import accumulate_delta


def test_duplicate_indexes_in_unseeded_slot_are_merged() -> None:
    acc: dict[object, object] = {}
    accumulate_delta(
        acc,
        {
            "tool_calls": [
                {"index": 0, "id": "call_abc", "function": {"name": "get_weather"}, "type": "function"},
                {"index": 0, "function": {"arguments": '{"city"'}},
                {"index": 0, "function": {"arguments": ': "Reykjavik"}'}},
            ],
        },
    )
    tool_calls = cast("list[Any]", acc["tool_calls"])
    assert len(tool_calls) == 1
    assert tool_calls[0]["id"] == "call_abc"
    assert tool_calls[0]["function"]["name"] == "get_weather"
    assert tool_calls[0]["function"]["arguments"] == '{"city": "Reykjavik"}'


def test_unique_indexes_preserved() -> None:
    acc: dict[object, object] = {}
    accumulate_delta(
        acc,
        {
            "tool_calls": [
                {"index": 0, "id": "call_1", "function": {"name": "fn_a"}, "type": "function"},
                {"index": 1, "id": "call_2", "function": {"name": "fn_b"}, "type": "function"},
            ],
        },
    )
    tool_calls = cast("list[Any]", acc["tool_calls"])
    assert len(tool_calls) == 2
    assert tool_calls[0]["id"] == "call_1"
    assert tool_calls[1]["id"] == "call_2"
