from __future__ import annotations

from openai.lib.streaming._deltas import accumulate_delta


def test_duplicate_index_in_first_chunk() -> None:
    """
    Regression test for issue #3201:
    When the first chunk contains multiple tool_calls entries with the same
    `index`, they should be merged into a single entry by logical index,
    not stored as separate physical entries.
    """
    chunk1 = {
        "tool_calls": [
            {
                "index": 0,
                "id": "call_1",
                "type": "function",
                "function": {"name": "get_weather", "arguments": ""},
            },
            {
                "index": 0,
                "function": {"arguments": ' {"cit'},
            },
        ]
    }

    chunk2 = {
        "tool_calls": [
            {
                "index": 0,
                "function": {"arguments": 'y": "London"}'},
            }
        ]
    }

    acc: dict = {}
    acc = accumulate_delta(acc, chunk1)
    assert len(acc["tool_calls"]) == 1, f"Expected 1 tool call, got {len(acc['tool_calls'])}"
    assert acc["tool_calls"][0]["function"]["arguments"] == ' {"cit'

    acc = accumulate_delta(acc, chunk2)
    assert len(acc["tool_calls"]) == 1, f"Expected 1 tool call, got {len(acc['tool_calls'])}"
    assert acc["tool_calls"][0]["function"]["arguments"] == ' {"city": "London"}'


def test_multiple_tool_calls_different_indexes() -> None:
    """Multiple tool calls with different indexes should remain separate."""
    chunk1 = {
        "tool_calls": [
            {"index": 0, "id": "call_1", "type": "function", "function": {"name": "get_weather", "arguments": ""}},
            {"index": 1, "id": "call_2", "type": "function", "function": {"name": "get_time", "arguments": ""}},
        ]
    }

    chunk2 = {
        "tool_calls": [
            {"index": 0, "function": {"arguments": ' {"city": "London"}'}},
            {"index": 1, "function": {"arguments": ' {"tz": "UTC"}'}},
        ]
    }

    acc: dict = {}
    acc = accumulate_delta(acc, chunk1)
    assert len(acc["tool_calls"]) == 2

    acc = accumulate_delta(acc, chunk2)
    assert len(acc["tool_calls"]) == 2
    assert acc["tool_calls"][0]["function"]["arguments"] == ' {"city": "London"}'
    assert acc["tool_calls"][1]["function"]["arguments"] == ' {"tz": "UTC"}'


def test_sparse_indexes() -> None:
    """Sparse indexes (index 2 arriving before index 1) should be handled correctly.
    
    Note: The accumulator inserts at the physical position matching the index,
    so index 2 is stored at position 0 when the list is empty, then index 1
    is inserted at position 1 (append). This is existing behavior.
    """
    chunk1 = {
        "tool_calls": [
            {"index": 2, "id": "call_3", "type": "function", "function": {"name": "search", "arguments": ""}},
        ]
    }

    chunk2 = {
        "tool_calls": [
            {"index": 1, "id": "call_2", "type": "function", "function": {"name": "get_time", "arguments": ""}},
        ]
    }

    acc: dict = {}
    acc = accumulate_delta(acc, chunk1)
    assert len(acc["tool_calls"]) == 1
    assert acc["tool_calls"][0]["index"] == 2

    acc = accumulate_delta(acc, chunk2)
    assert len(acc["tool_calls"]) == 2
    assert acc["tool_calls"][0]["index"] == 2
    assert acc["tool_calls"][1]["index"] == 1


def test_normal_case_no_duplicates() -> None:
    """Normal case with no duplicate indexes should work as before."""
    chunk1 = {
        "tool_calls": [
            {"index": 0, "id": "call_1", "type": "function", "function": {"name": "get_weather", "arguments": ""}},
        ]
    }

    chunk2 = {
        "tool_calls": [
            {"index": 0, "function": {"arguments": ' {"city": "London"}'}},
        ]
    }

    acc: dict = {}
    acc = accumulate_delta(acc, chunk1)
    assert len(acc["tool_calls"]) == 1

    acc = accumulate_delta(acc, chunk2)
    assert len(acc["tool_calls"]) == 1
    assert acc["tool_calls"][0]["function"]["arguments"] == ' {"city": "London"}'


def test_three_duplicate_indexes_in_first_chunk() -> None:
    """Three entries with the same index in the first chunk should all be merged."""
    chunk1 = {
        "tool_calls": [
            {"index": 0, "id": "call_1", "type": "function", "function": {"name": "test", "arguments": ""}},
            {"index": 0, "function": {"arguments": ' {"a"'}},
            {"index": 0, "function": {"arguments": ': 1}'}},
        ]
    }

    acc: dict = {}
    acc = accumulate_delta(acc, chunk1)
    assert len(acc["tool_calls"]) == 1
    assert acc["tool_calls"][0]["function"]["arguments"] == ' {"a": 1}'
