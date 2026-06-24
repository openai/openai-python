from __future__ import annotations

from collections.abc import Callable

import pytest

from openai.lib.streaming._deltas import accumulate_delta as accumulate_chat_delta
from openai.lib.streaming._assistants import accumulate_delta as accumulate_assistants_delta


@pytest.mark.parametrize("accumulate_delta", [accumulate_chat_delta, accumulate_assistants_delta])
def test_accumulate_delta_merges_duplicate_index_entries_in_initial_list(
    accumulate_delta: Callable[[dict[object, object], dict[object, object]], dict[object, object]],
) -> None:
    acc: dict[object, object] = {}

    accumulate_delta(
        acc,
        {
            "tool_calls": [
                {"index": 0, "id": "call_abc", "function": {"name": "list_files"}, "type": "function"},
                {"index": 0, "function": {"arguments": '{"path"'}},
            ]
        },
    )
    accumulate_delta(acc, {"tool_calls": [{"index": 0, "function": {"arguments": ': "."}'}}]})

    assert acc == {
        "tool_calls": [
            {
                "index": 0,
                "id": "call_abc",
                "function": {"name": "list_files", "arguments": '{"path": "."}'},
                "type": "function",
            }
        ]
    }
