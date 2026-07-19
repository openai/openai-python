"""Tests for accumulate_delta from openai.lib.streaming._deltas.

Regression tests for https://github.com/openai/openai-python/issues/3201:
streaming tool_call deltas with duplicate indexes accumulated incorrectly.
"""
from __future__ import annotations

from openai.lib.streaming._deltas import accumulate_delta


class TestAccumulateDeltaToolCallsDuplicateIndex:
    """Issue #3201: when the first streaming chunk contains multiple tool_calls
    at the same index, they should be merged into a single entry."""

    def test_duplicate_index_in_first_chunk(self) -> None:
        """Simulate the exact scenario from issue #3201:
        first chunk has two tool_call entries both with index=0."""
        acc: dict[object, object] = {}

        # First chunk: two entries both at index 0
        # (e.g. first provides id+name, second provides initial arguments)
        chunk1 = {
            "tool_calls": [
                {
                    "index": 0,
                    "id": "functions.list_files:0",
                    "function": {"name": "list_files"},
                    "type": "function",
                },
                {
                    "index": 0,
                    "function": {"arguments": ' {"'},
                },
            ]
        }

        acc = accumulate_delta(acc, chunk1)

        # Should have a single entry in tool_calls, not two
        tool_calls = acc["tool_calls"]  # type: ignore[index]
        assert isinstance(tool_calls, list)
        assert len(tool_calls) == 1, (
            f"Expected 1 tool_call entry after merging duplicate indexes, "
            f"got {len(tool_calls)}: {tool_calls}"
        )

        tc = tool_calls[0]  # type: ignore[index]
        assert tc["index"] == 0
        assert tc["id"] == "functions.list_files:0"
        assert tc["function"]["name"] == "list_files"
        assert tc["function"]["arguments"] == ' {"'

    def test_subsequent_chunks_merge_into_existing(self) -> None:
        """After the first chunk with duplicates is correctly merged,
        subsequent chunks should continue accumulating into the same entry."""
        acc: dict[object, object] = {}

        # First chunk with duplicate index 0
        chunk1 = {
            "tool_calls": [
                {
                    "index": 0,
                    "id": "functions.list_files:0",
                    "function": {"name": "list_files"},
                    "type": "function",
                },
                {
                    "index": 0,
                    "function": {"arguments": ' {"'},
                },
            ]
        }
        acc = accumulate_delta(acc, chunk1)

        # Second chunk: more arguments for the same tool_call
        chunk2 = {
            "tool_calls": [
                {
                    "index": 0,
                    "function": {"arguments": 'path": "."}'},
                },
            ]
        }
        acc = accumulate_delta(acc, chunk2)

        tool_calls = acc["tool_calls"]  # type: ignore[index]
        assert isinstance(tool_calls, list)
        assert len(tool_calls) == 1

        tc = tool_calls[0]  # type: ignore[index]
        assert tc["id"] == "functions.list_files:0"
        assert tc["function"]["name"] == "list_files"
        assert tc["function"]["arguments"] == ' {"path": "."}'

    def test_multiple_tool_calls_different_indexes(self) -> None:
        """Normal case: two different tool calls at index 0 and 1."""
        acc: dict[object, object] = {}

        chunk1 = {
            "tool_calls": [
                {
                    "index": 0,
                    "id": "call_1",
                    "function": {"name": "get_weather", "arguments": ""},
                    "type": "function",
                },
                {
                    "index": 1,
                    "id": "call_2",
                    "function": {"name": "get_time", "arguments": ""},
                    "type": "function",
                },
            ]
        }
        acc = accumulate_delta(acc, chunk1)

        tool_calls = acc["tool_calls"]  # type: ignore[index]
        assert isinstance(tool_calls, list)
        assert len(tool_calls) == 2
        assert tool_calls[0]["id"] == "call_1"  # type: ignore[index]
        assert tool_calls[1]["id"] == "call_2"  # type: ignore[index]

        # Later chunks accumulate correctly
        chunk2 = {
            "tool_calls": [
                {"index": 0, "function": {"arguments": '{"city": "SF"}'}},
                {"index": 1, "function": {"arguments": '{"tz": "PST"}'}},
            ]
        }
        acc = accumulate_delta(acc, chunk2)

        tool_calls = acc["tool_calls"]  # type: ignore[index]
        assert len(tool_calls) == 2
        assert tool_calls[0]["function"]["arguments"] == '{"city": "SF"}'  # type: ignore[index]
        assert tool_calls[1]["function"]["arguments"] == '{"tz": "PST"}'  # type: ignore[index]

    def test_non_indexed_lists_still_work(self) -> None:
        """Ensure non-indexed lists (e.g. text content arrays) still work
        by simple extension."""
        acc: dict[object, object] = {}
        acc = accumulate_delta(acc, {"tags": ["a", "b"]})
        acc = accumulate_delta(acc, {"tags": ["c"]})
        assert acc["tags"] == ["a", "b", "c"]

    def test_basic_string_accumulation(self) -> None:
        """Ensure basic string accumulation still works."""
        acc: dict[object, object] = {}
        acc = accumulate_delta(acc, {"content": "Hello"})
        acc = accumulate_delta(acc, {"content": " world"})
        assert acc["content"] == "Hello world"

    def test_first_chunk_with_single_indexed_entry(self) -> None:
        """A single tool_call in the first chunk (no duplicates) should work
        the same as before."""
        acc: dict[object, object] = {}

        chunk1 = {
            "tool_calls": [
                {
                    "index": 0,
                    "id": "call_1",
                    "function": {"name": "foo"},
                    "type": "function",
                },
            ]
        }
        acc = accumulate_delta(acc, chunk1)

        tool_calls = acc["tool_calls"]  # type: ignore[index]
        assert isinstance(tool_calls, list)
        assert len(tool_calls) == 1
        assert tool_calls[0]["id"] == "call_1"  # type: ignore[index]

    def test_multiple_duplicate_indexes_in_first_chunk(self) -> None:
        """Edge case: three entries at the same index in the first chunk."""
        acc: dict[object, object] = {}

        chunk1 = {
            "tool_calls": [
                {
                    "index": 0,
                    "id": "call_1",
                    "type": "function",
                },
                {
                    "index": 0,
                    "function": {"name": "get_weather"},
                },
                {
                    "index": 0,
                    "function": {"arguments": '{"'},
                },
            ]
        }
        acc = accumulate_delta(acc, chunk1)

        tool_calls = acc["tool_calls"]  # type: ignore[index]
        assert isinstance(tool_calls, list)
        assert len(tool_calls) == 1

        tc = tool_calls[0]  # type: ignore[index]
        assert tc["id"] == "call_1"
        assert tc["type"] == "function"
        assert tc["function"]["name"] == "get_weather"
        assert tc["function"]["arguments"] == '{"'
