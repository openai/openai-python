"""Tests for the streaming delta accumulator."""

from __future__ import annotations

from typing import Any, cast

from openai.lib.streaming._deltas import accumulate_delta


class TestAccumulateDelta:
    """Tests for accumulate_delta — regression for #3201."""

    def test_duplicate_index_first_chunk_merges(self) -> None:
        """First chunk with two entries at the same index should merge into one."""
        acc: dict[object, object] = {}
        delta: dict[object, object] = {
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
        calls = cast(list[dict[str, Any]], result["tool_calls"])
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
        delta: dict[object, object] = {
            "tool_calls": [
                {
                    "index": 0,
                    "function": {"arguments": 'path": "."}'},
                }
            ]
        }
        result = accumulate_delta(acc, delta)
        calls = cast(list[dict[str, Any]], result["tool_calls"])
        assert len(calls) == 1
        assert calls[0]["function"]["arguments"] == ' {"path": "."}'

    def test_different_indexes_accumulate_separately(self) -> None:
        """Entries with different indexes should accumulate separately."""
        acc: dict[object, object] = {}
        delta1: dict[object, object] = {
            "tool_calls": [
                {"index": 0, "id": "call_a", "function": {"name": "tool_a"}, "type": "function"},
            ]
        }
        delta2: dict[object, object] = {
            "tool_calls": [
                {"index": 1, "id": "call_b", "function": {"name": "tool_b"}, "type": "function"},
            ]
        }
        result = accumulate_delta(acc, delta1)
        result = accumulate_delta(result, delta2)
        calls = cast(list[dict[str, Any]], result["tool_calls"])
        assert len(calls) == 2
        assert calls[0]["index"] == 0
        assert calls[1]["index"] == 1

    def test_string_accumulation_unchanged(self) -> None:
        """Basic string accumulation should still work."""
        acc: dict[object, object] = {"content": "hello"}
        delta: dict[object, object] = {"content": " world"}
        result = accumulate_delta(acc, delta)
        assert result["content"] == "hello world"

    def test_duplicate_index_first_chunk_then_subsequent_merge(self) -> None:
        """Full round-trip: first chunk with duplicate indexes, then subsequent chunk merges correctly."""
        acc: dict[object, object] = {}
        # First chunk: two entries at index 0
        delta1: dict[object, object] = {
            "tool_calls": [
                {"index": 0, "id": "call_abc", "function": {"name": "list_files"}, "type": "function"},
                {"index": 0, "function": {"arguments": ' {"'}},
            ]
        }
        result = accumulate_delta(acc, delta1)
        calls = cast(list[dict[str, Any]], result["tool_calls"])
        assert len(calls) == 1, f"Expected 1 entry after coalescing, got {len(calls)}"
        assert calls[0]["function"]["arguments"] == ' {"'

        # Second chunk: more arguments for index 0
        delta2: dict[object, object] = {
            "tool_calls": [
                {"index": 0, "function": {"arguments": 'path": "."}'}},
            ]
        }
        result = accumulate_delta(result, delta2)
        calls = cast(list[dict[str, Any]], result["tool_calls"])
        assert len(calls) == 1
        assert calls[0]["function"]["arguments"] == ' {"path": "."}'
        assert calls[0]["id"] == "call_abc"
        assert calls[0]["function"]["name"] == "list_files"

    def test_sparse_out_of_order_indexes_no_data_loss(self) -> None:
        """Regression for the data-loss bug: if acc_value has [{"index": 1, ...}]
        and index 0 arrives later, the index-1 entry must not be overwritten."""
        acc: dict[object, object] = {
            "tool_calls": [
                {"index": 1, "id": "call_b", "function": {"name": "tool_b"}, "type": "function"},
            ]
        }
        delta: dict[object, object] = {
            "tool_calls": [
                {"index": 0, "id": "call_a", "function": {"name": "tool_a"}, "type": "function"},
            ]
        }
        result = accumulate_delta(acc, delta)
        calls = cast(list[dict[str, Any]], result["tool_calls"])
        # Both entries should survive
        assert len(calls) == 2
        # The index-1 entry should not be overwritten
        ids = [c["id"] for c in calls]
        assert "call_a" in ids
        assert "call_b" in ids

    def test_out_of_order_index_stays_addressable_by_logical_index(self) -> None:
        """Regression for Codex P2: when index 1 arrives before index 0, the
        list must stay addressable by logical index — downstream code does
        ``tool_calls[tool_call_delta.index]`` treating logical index as
        physical position.  If the list is ``[{"index": 1}, {"index": 0}]``
        then ``tool_calls[0]`` returns the wrong entry."""
        acc: dict[object, object] = {
            "tool_calls": [
                {"index": 1, "id": "call_b", "function": {"name": "tool_b"}, "type": "function"},
            ]
        }
        delta: dict[object, object] = {
            "tool_calls": [
                {"index": 0, "id": "call_a", "function": {"name": "tool_a"}, "type": "function"},
            ]
        }
        result = accumulate_delta(acc, delta)
        calls = cast(list[dict[str, Any]], result["tool_calls"])
        # The list must be addressable by logical index: calls[0] should have
        # index 0, calls[1] should have index 1.
        assert calls[0]["index"] == 0
        assert calls[0]["id"] == "call_a"
        assert calls[1]["index"] == 1
        assert calls[1]["id"] == "call_b"

    def test_gap_placeholder_replaced_not_shifted(self) -> None:
        """Regression for Codex P2: when indexes 0 then 2 arrive, slot 1 is
        padded with {}.  If index 1 arrives later, it must replace the
        placeholder in-place, not insert before it (which would shift the
        placeholder ahead of index 2, breaking tool_calls[2] lookups)."""
        acc: dict[object, object] = {
            "tool_calls": [
                {"index": 0, "id": "call_a", "function": {"name": "tool_a"}, "type": "function"},
                {},
                {"index": 2, "id": "call_c", "function": {"name": "tool_c"}, "type": "function"},
            ]
        }
        delta: dict[object, object] = {
            "tool_calls": [
                {"index": 1, "id": "call_b", "function": {"name": "tool_b"}, "type": "function"},
            ]
        }
        result = accumulate_delta(acc, delta)
        calls = cast(list[dict[str, Any]], result["tool_calls"])
        # The placeholder at index 1 should be replaced, not shifted
        assert len(calls) == 3
        assert calls[0]["index"] == 0
        assert calls[0]["id"] == "call_a"
        assert calls[1]["index"] == 1
        assert calls[1]["id"] == "call_b"
        assert calls[2]["index"] == 2
        assert calls[2]["id"] == "call_c"

    def test_coalesce_list_by_index_sorts_by_logical_index(self) -> None:
        """Regression for Codex P2: _coalesce_list_by_index must sort entries
        by logical index so the list is addressable by tool_calls[index]."""
        from openai.lib.streaming._deltas import _coalesce_list_by_index

        lst: list[object] = [
            {"index": 1, "id": "call_b", "function": {"name": "tool_b"}, "type": "function"},
            {"index": 0, "id": "call_a", "function": {"name": "tool_a"}, "type": "function"},
        ]
        result = _coalesce_list_by_index(lst)
        calls = cast(list[dict[str, Any]], result)
        assert calls[0]["index"] == 0
        assert calls[0]["id"] == "call_a"
        assert calls[1]["index"] == 1
        assert calls[1]["id"] == "call_b"

    def test_dumped_placeholder_replaced_not_shifted(self) -> None:
        """Regression for Codex P2: after the snapshot is round-tripped through
        model_dump, a gap-filler {} placeholder becomes a dict of unset
        tool-call fields (e.g. {"id": None, "function": None, "type": None}).
        If index 1 arrives later, it must replace that dumped placeholder
        in-place, not insert before it (which would shift the index-2 entry
        to slot 3 and break tool_calls[2] lookups)."""
        acc: dict[object, object] = {
            "tool_calls": [
                {"index": 0, "id": "call_a", "function": {"name": "tool_a"}, "type": "function"},
                # Simulates a {} placeholder after model_dump round-trip
                {"id": None, "function": None, "type": None},
                {"index": 2, "id": "call_c", "function": {"name": "tool_c"}, "type": "function"},
            ]
        }
        delta: dict[object, object] = {
            "tool_calls": [
                {"index": 1, "id": "call_b", "function": {"name": "tool_b"}, "type": "function"},
            ]
        }
        result = accumulate_delta(acc, delta)
        calls = cast(list[dict[str, Any]], result["tool_calls"])
        # The dumped placeholder at index 1 should be replaced, not shifted
        assert len(calls) == 3
        assert calls[0]["index"] == 0
        assert calls[0]["id"] == "call_a"
        assert calls[1]["index"] == 1
        assert calls[1]["id"] == "call_b"
        assert calls[2]["index"] == 2
        assert calls[2]["id"] == "call_c"

    def test_coalesce_dumped_placeholder_replaced(self) -> None:
        """Regression for Codex P2: _coalesce_list_by_index must also detect
        dumped placeholders (all-None values from model_dump) and replace them
        in-place instead of inserting before them."""
        from openai.lib.streaming._deltas import _coalesce_list_by_index

        lst: list[object] = [
            {"index": 0, "id": "call_a", "function": {"name": "tool_a"}, "type": "function"},
            # Dumped placeholder at index 1 (all values None)
            {"id": None, "function": None, "type": None},
            {"index": 2, "id": "call_c", "function": {"name": "tool_c"}, "type": "function"},
            # Index 1 arriving later — should replace the placeholder
            {"index": 1, "id": "call_b", "function": {"name": "tool_b"}, "type": "function"},
        ]
        result = _coalesce_list_by_index(lst)
        calls = cast(list[dict[str, Any]], result)
        assert len(calls) == 3
        assert calls[0]["index"] == 0
        assert calls[0]["id"] == "call_a"
        assert calls[1]["index"] == 1
        assert calls[1]["id"] == "call_b"
        assert calls[2]["index"] == 2
        assert calls[2]["id"] == "call_c"
