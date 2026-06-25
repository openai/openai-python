"""Tests for accumulate_delta handling of duplicate-index entries.

Issue #3201: when the first streamed chunk contains multiple tool_calls entries
with the same `index`, the accumulator stores them as separate list entries.
Subsequent chunks only merge into the first one, leaving the second stranded.
"""

from __future__ import annotations

from openai.lib.streaming._deltas import accumulate_delta


def test_single_index_in_first_chunk():
    """Normal case: one entry per index in the first chunk."""
    acc: dict[object, object] = {}
    # First chunk: one tool_call at index 0
    acc = accumulate_delta(acc, {
        "tool_calls": [
            {"index": 0, "id": "call_1", "function": {"name": "list_files"}, "type": "function"},
        ]
    })
    # Second chunk: arguments for index 0
    acc = accumulate_delta(acc, {
        "tool_calls": [
            {"index": 0, "function": {"arguments": ' {"path": "."}'}},
        ]
    })

    tool_calls = acc["tool_calls"]
    assert isinstance(tool_calls, list)
    assert len(tool_calls) == 1
    assert tool_calls[0]["id"] == "call_1"
    assert tool_calls[0]["function"]["name"] == "list_files"
    assert tool_calls[0]["function"]["arguments"] == ' {"path": "."}'


def test_duplicate_index_in_first_chunk():
    """Issue #3201: first chunk has two entries with the same index."""
    acc: dict[object, object] = {}
    # First chunk: two entries both at index 0 (id+name, then start of arguments)
    acc = accumulate_delta(acc, {
        "tool_calls": [
            {"index": 0, "id": "call_1", "function": {"name": "list_files"}, "type": "function"},
            {"index": 0, "function": {"arguments": ' {"'}},
        ]
    })
    # Second chunk: rest of arguments for index 0
    acc = accumulate_delta(acc, {
        "tool_calls": [
            {"index": 0, "function": {"arguments": 'path": "."}'}},
        ]
    })

    tool_calls = acc["tool_calls"]
    assert isinstance(tool_calls, list)
    assert len(tool_calls) == 1, f"Expected 1 tool_call, got {len(tool_calls)}: {tool_calls}"
    assert tool_calls[0]["id"] == "call_1"
    assert tool_calls[0]["function"]["name"] == "list_files"
    assert tool_calls[0]["function"]["arguments"] == ' {"path": "."}'


def test_duplicate_index_preserves_type_and_id():
    """Ensure merged entry keeps id and type from the first occurrence."""
    acc: dict[object, object] = {}
    acc = accumulate_delta(acc, {
        "tool_calls": [
            {"index": 0, "id": "call_abc", "type": "function", "function": {"name": "search"}},
            {"index": 0, "function": {"arguments": '{"q":'}},
        ]
    })

    tool_calls = acc["tool_calls"]
    assert len(tool_calls) == 1
    assert tool_calls[0]["id"] == "call_abc"
    assert tool_calls[0]["type"] == "function"
    assert tool_calls[0]["function"]["name"] == "search"
    assert tool_calls[0]["function"]["arguments"] == '{"q":'


def test_multiple_distinct_indices_in_first_chunk():
    """Multiple entries with different indices should stay separate."""
    acc: dict[object, object] = {}
    acc = accumulate_delta(acc, {
        "tool_calls": [
            {"index": 0, "id": "call_1", "function": {"name": "fn_a"}, "type": "function"},
            {"index": 1, "id": "call_2", "function": {"name": "fn_b"}, "type": "function"},
        ]
    })

    tool_calls = acc["tool_calls"]
    assert isinstance(tool_calls, list)
    assert len(tool_calls) == 2
    assert tool_calls[0]["id"] == "call_1"
    assert tool_calls[1]["id"] == "call_2"


def test_multiple_indices_with_duplicates_in_first_chunk():
    """Mix of duplicate and distinct indices."""
    acc: dict[object, object] = {}
    acc = accumulate_delta(acc, {
        "tool_calls": [
            {"index": 0, "id": "call_1", "function": {"name": "fn_a"}, "type": "function"},
            {"index": 0, "function": {"arguments": '{"a":'}},
            {"index": 1, "id": "call_2", "function": {"name": "fn_b"}, "type": "function"},
            {"index": 1, "function": {"arguments": '{"b":'}},
        ]
    })
    # More args for both
    acc = accumulate_delta(acc, {
        "tool_calls": [
            {"index": 0, "function": {"arguments": '"x"}'}},
            {"index": 1, "function": {"arguments": '"y"}'}},
        ]
    })

    tool_calls = acc["tool_calls"]
    assert isinstance(tool_calls, list)
    assert len(tool_calls) == 2
    assert tool_calls[0]["id"] == "call_1"
    assert tool_calls[0]["function"]["arguments"] == '{"a":"x"}'
    assert tool_calls[1]["id"] == "call_2"
    assert tool_calls[1]["function"]["arguments"] == '{"b":"y"}'


def test_non_indexed_lists_unchanged():
    """Lists without integer `index` fields should pass through normally."""
    acc: dict[object, object] = {}
    acc = accumulate_delta(acc, {
        "content": ["hello", "world"]
    })
    acc = accumulate_delta(acc, {
        "content": ["!"]
    })

    assert acc["content"] == ["hello", "world", "!"]
