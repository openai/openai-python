from __future__ import annotations

from copy import deepcopy

import pytest

from openai.lib.streaming._deltas import accumulate_delta


@pytest.mark.parametrize("initial", [{}, {"tool_calls": None}, {"tool_calls": []}])
def test_duplicate_indexes_in_initial_list(initial: dict[object, object]) -> None:
    acc = deepcopy(initial)
    accumulate_delta(
        acc,
        {
            "tool_calls": [
                {"index": 0, "id": "call_abc", "type": "function", "function": {"name": "list_files"}},
                {"index": 0, "function": {"arguments": '{"path"'}},
            ]
        },
    )
    accumulate_delta(acc, {"tool_calls": [{"index": 0, "function": {"arguments": ': "."}'}}]})
    assert acc["tool_calls"] == [
        {
            "index": 0,
            "id": "call_abc",
            "type": "function",
            "function": {"name": "list_files", "arguments": '{"path": "."}'},
        }
    ]


@pytest.mark.parametrize(
    "initial,delta,expected",
    [
        ({}, {"value": [1, "a"]}, {"value": [1, "a"]}),
        ({"value": None}, {"value": [1, "a"]}, {"value": [1, "a"]}),
        ({"value": []}, {"value": [1, "a"]}, {"value": [1, "a"]}),
        ({"value": [1]}, {"value": [2, "a"]}, {"value": [1, 2, "a"]}),
        ({"value": []}, {"value": [{"text": "a"}]}, {"value": [{"text": "a"}]}),
        ({}, {"value": [{"text": "a"}]}, {"value": [{"text": "a"}]}),
        ({"value": [1]}, {"value": []}, {"value": [1]}),
        # Full Assistants snapshots omit the delta-only index field.
        (
            {"value": [{"text": "a"}]},
            {"value": [{"index": 0, "text": "b"}]},
            {"value": [{"index": 0, "text": "ab"}]},
        ),
        (
            {"index": 1, "type": "text", "text": {"value": "a"}, "count": 2},
            {"index": 1, "type": "text", "text": {"value": "b"}, "count": 3},
            {"index": 1, "type": "text", "text": {"value": "ab"}, "count": 5},
        ),
        (
            {"function": {"name": "list_", "arguments": "{"}},
            {"function": {"name": "files", "arguments": "}"}},
            {"function": {"name": "list_files", "arguments": "{}"}},
        ),
    ],
)
def test_existing_delta_semantics(
    initial: dict[object, object], delta: dict[object, object], expected: dict[object, object]
) -> None:
    assert accumulate_delta(deepcopy(initial), deepcopy(delta)) == expected


@pytest.mark.parametrize(
    "entry,error,match",
    [
        ("invalid", TypeError, "not a dictionary"),
        ({"text": "invalid"}, RuntimeError, "an `index` key"),
        ({"index": "0"}, TypeError, "not an integer"),
    ],
)
def test_invalid_indexed_delta(entry: object, error: type[Exception], match: str) -> None:
    with pytest.raises(error, match=match):
        accumulate_delta({"content": [{"index": 0, "text": "a"}]}, {"content": [entry]})
