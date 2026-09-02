from __future__ import annotations

import json
from typing import Any, cast
from collections.abc import Callable

import pytest

from openai.lib.streaming._deltas import accumulate_delta as accumulate_chat_delta
from openai.lib.streaming._assistants import accumulate_delta as accumulate_assistant_delta


@pytest.mark.parametrize("accumulate", [accumulate_chat_delta, accumulate_assistant_delta])
def test_accumulate_delta_merges_duplicate_index_entries_in_initial_list(
    accumulate: Callable[[dict[object, object], dict[object, object]], dict[object, object]],
) -> None:
    acc: dict[object, object] = {}

    accumulate(
        acc,
        {
            "tool_calls": [
                {
                    "index": 0,
                    "id": "functions.list_files:0",
                    "function": {"name": "list_files"},
                    "type": "function",
                },
                {"index": 0, "function": {"arguments": ' {"path"'}},
            ],
        },
    )
    accumulate(
        acc,
        {
            "tool_calls": [
                {"index": 0, "function": {"arguments": ': "."}'}},
            ],
        },
    )

    tool_calls = acc["tool_calls"]
    assert isinstance(tool_calls, list)
    assert tool_calls == [
        {
            "index": 0,
            "id": "functions.list_files:0",
            "function": {"name": "list_files", "arguments": ' {"path": "."}'},
            "type": "function",
        }
    ]
    tool_call = cast(dict[str, Any], tool_calls[0])
    function = cast(dict[str, str], tool_call["function"])
    assert json.loads(function["arguments"]) == {"path": "."}
