from __future__ import annotations

from openai.lib.streaming import _deltas, _assistants


def test_accumulate_delta_merges_duplicate_indexes_on_first_chunk() -> None:
    acc: dict[object, object] = {}

    _deltas.accumulate_delta(
        acc,
        {
            "tool_calls": [
                {"index": 0, "id": "call_abc", "type": "function", "function": {"name": "list_files"}},
                {"index": 0, "function": {"arguments": ' {"'}},
            ]
        },
    )
    _deltas.accumulate_delta(acc, {"tool_calls": [{"index": 0, "function": {"arguments": 'path": "."}'}}]})

    assert acc["tool_calls"] == [
        {
            "index": 0,
            "id": "call_abc",
            "type": "function",
            "function": {"name": "list_files", "arguments": ' {"path": "."}'},
        }
    ]


def test_assistants_accumulate_delta_merges_duplicate_indexes_on_first_chunk() -> None:
    acc: dict[object, object] = {}

    _assistants.accumulate_delta(
        acc,
        {
            "tool_calls": [
                {"index": 0, "id": "call_abc", "type": "function", "function": {"name": "list_files"}},
                {"index": 0, "function": {"arguments": ' {"'}},
            ]
        },
    )
    _assistants.accumulate_delta(acc, {"tool_calls": [{"index": 0, "function": {"arguments": 'path": "."}'}}]})

    assert acc["tool_calls"] == [
        {
            "index": 0,
            "id": "call_abc",
            "type": "function",
            "function": {"name": "list_files", "arguments": ' {"path": "."}'},
        }
    ]
