"""Tests for the streaming delta accumulator."""

from __future__ import annotations

from openai.lib.streaming._deltas import accumulate_delta


class TestAccumulateDelta:
    """Tests for accumulate_delta — regression for #3201."""

    def test_duplicate_index_first_chunk_merges(self) -> None:
        """First chunk with two entries at the same index should merge into one."""
        acc: dict[object, object] = {}
        delta = {
            "tool_calls": [
                {
                    "index": 0,
                    "id": "call_abc",
                    "function": {"name": "list_files"},
                    "type": "function",
                },
                {
                    "index": 0,
                    "function": {"arguments": ' {"'},
                },
            ]
        }
        result = accumulate_delta(acc, delta)
        calls = result["tool_calls"]
        assert isinstance(calls, list)
        # Should be a single entry at index 0, not two
        assert len(calls) == 1
        assert calls[0]["index"] == 0
        assert calls[0]["id"] == "call_abc"
        assert calls[0]["function"]["name"] == "list_files"
        assert calls[0]["function"]["arguments"] == ' {"'

    def test_duplicate_index_subsequent_chunk_merges(self) -> None:
        """Subsequent chunk with same index should merge into existing entry."""
        acc: dict[object, object] = {
            "tool_calls": [
                {
                    "index": 0,
                    "id": "call_abc",
                    "function": {"name": "list_files", "arguments": ' {"'},
                    "type": "function",
                }
            ]
        }
        delta = {
            "tool_calls": [
                {
                    "index": 0,
                    "function": {"arguments": 'path": "."}'},
                }
            ]
        }
        result = accumulate_delta(acc, delta)
        calls = result["tool_calls"]
        assert len(calls) == 1
        assert calls[0]["function"]["arguments"] == ' {"path": "."}'

    def test_different_indexes_accumulate_separately(self) -> None:
        """Entries with different indexes should accumulate separately."""
        acc: dict[object, object] = {}
        delta1 = {
            "tool_calls": [
                {"index": 0, "id": "call_a", "function": {"name": "tool_a"}, "type": "function"},
            ]
        }
        delta2 = {
            "tool_calls": [
                {"index": 1, "id": "call_b", "function": {"name": "tool_b"}, "type": "function"},
            ]
        }
        result = accumulate_delta(acc, delta1)
        result = accumulate_delta(result, delta2)
        calls = result["tool_calls"]
        assert len(calls) == 2
        assert calls[0]["index"] == 0
        assert calls[1]["index"] == 1

    def test_string_accumulation_unchanged(self) -> None:
        """Basic string accumulation should still work."""
        acc: dict[object, object] = {"content": "hello"}
        delta = {"content": " world"}
        result = accumulate_delta(acc, delta)
        assert result["content"] == "hello world"

    def test_duplicate_index_first_chunk_then_subsequent_merge(self) -> None:
        """Full round-trip: first chunk with duplicate indexes, then subsequent chunk merges correctly."""
        acc: dict[object, object] = {}
        # First chunk: two entries at index 0
        delta1 = {
            "tool_calls": [
                {"index": 0, "id": "call_abc", "function": {"name": "list_files"}, "type": "function"},
                {"index": 0, "function": {"arguments": ' {"'}},
            ]
        }
        result = accumulate_delta(acc, delta1)
        calls = result["tool_calls"]
        assert len(calls) == 1, f"Expected 1 entry after coalescing, got {len(calls)}"
        assert calls[0]["function"]["arguments"] == ' {"'

        # Second chunk: more arguments for index 0
        delta2 = {
            "tool_calls": [
                {"index": 0, "function": {"arguments": 'path": "."}'}},
            ]
        }
        result = accumulate_delta(result, delta2)
        calls = result["tool_calls"]
        assert len(calls) == 1
        assert calls[0]["function"]["arguments"] == ' {"path": "."}'
        assert calls[0]["id"] == "call_abc"
        assert calls[0]["function"]["name"] == "list_files"