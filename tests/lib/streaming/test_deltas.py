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

    def test_empty_accumulated_list_still_coalesces(self) -> None:
        """Regression for Codex P2: when a prior chunk explicitly sets
        tool_calls: [], the next chunk with duplicate-index entries must still
        be coalesced instead of being extended verbatim."""
        acc: dict[object, object] = {"tool_calls": []}
        delta: dict[object, object] = {
            "tool_calls": [
                {"index": 0, "id": "call_abc", "function": {"name": "list_files"}, "type": "function"},
                {"index": 0, "function": {"arguments": ' {"'}},
            ]
        }
        result = accumulate_delta(acc, delta)
        calls = cast(list[dict[str, Any]], result["tool_calls"])
        assert len(calls) == 1
        assert calls[0]["id"] == "call_abc"
        assert calls[0]["function"]["arguments"] == ' {"'

    def test_single_entry_normalized_to_logical_slot(self) -> None:
        """Regression for Codex P2: a single tool-call entry whose logical
        index is not 0 must be padded to its logical slot, not stored at
        physical slot 0."""
        acc: dict[object, object] = {}
        delta: dict[object, object] = {
            "tool_calls": [
                {"index": 1, "id": "call_b", "function": {"name": "tool_b"}, "type": "function"},
            ]
        }
        result = accumulate_delta(acc, delta)
        calls = cast(list[dict[str, Any]], result["tool_calls"])
        assert len(calls) == 2
        assert calls[0] == {}
        assert calls[1]["index"] == 1
        assert calls[1]["id"] == "call_b"

    def test_repeated_metadata_replaced_not_concatenated(self) -> None:
        """Regression for Codex P2: duplicate-index entries repeating metadata
        (id, function.name) must replace, not concatenate — otherwise the value
        becomes call_abccall_abc."""
        acc: dict[object, object] = {
            "tool_calls": [
                {"index": 0, "id": "call_abc", "function": {"name": "list_files"}, "type": "function"},
            ]
        }
        delta: dict[object, object] = {
            "tool_calls": [
                {"index": 0, "id": "call_abc", "function": {"name": "list_files"}, "type": "function"},
            ]
        }
        result = accumulate_delta(acc, delta)
        calls = cast(list[dict[str, Any]], result["tool_calls"])
        assert len(calls) == 1
        assert calls[0]["id"] == "call_abc"
        assert calls[0]["function"]["name"] == "list_files"

    def test_huge_sparse_index_does_not_materialize_gaps(self) -> None:
        """Regression for Codex P2: a delta with a huge sparse index must not
        allocate storage proportional to the numeric index."""
        from openai.lib.streaming._deltas import _MAX_INDEX_PADDING

        acc: dict[object, object] = {}
        delta: dict[object, object] = {
            "tool_calls": [
                {"index": 1_000_000, "id": "call_z", "function": {"name": "tool_z"}, "type": "function"},
            ]
        }
        result = accumulate_delta(acc, delta)
        calls = cast(list[dict[str, Any]], result["tool_calls"])
        # Bounded allocation: no million-entry placeholder list.
        assert len(calls) <= _MAX_INDEX_PADDING + 2
        assert calls[-1]["index"] == 1_000_000
        assert calls[-1]["id"] == "call_z"


class TestChatCompletionStreamStateIntegration:
    """Integration-level regression for #3201: feed the two problematic chunks
    through ChatCompletionStreamState and verify the final snapshot has exactly
    one tool call per index with merged fields."""

    def test_duplicate_index_through_stream_state(self) -> None:
        """Replay the exact issue shape from #3201 through the full stream state.

        The first chunk contains two tool_calls at index 0 (one with id/name,
        one with arguments).  The second chunk adds a delta to index 0.
        The final snapshot must contain a single index-0 call with all fields.
        """
        from openai.types.chat import ChatCompletionChunk
        from openai.lib.streaming.chat import ChatCompletionStreamState
        from openai.types.chat.chat_completion_chunk import Choice as ChoiceChunk

        chunk1 = ChatCompletionChunk.construct(
            id="chatcmpl-1",
            created=0,
            model="gpt-4",
            choices=[
                ChoiceChunk.construct(
                    index=0,
                    delta={
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
                    },
                ),
            ],
        )

        chunk2 = ChatCompletionChunk.construct(
            id="chatcmpl-1",
            created=0,
            model="gpt-4",
            choices=[
                ChoiceChunk.construct(
                    index=0,
                    delta={
                        "tool_calls": [
                            {
                                "index": 0,
                                "function": {"arguments": "path"},
                            },
                        ]
                    },
                ),
            ],
        )

        state = ChatCompletionStreamState()
        list(state.handle_chunk(chunk1))
        list(state.handle_chunk(chunk2))

        snapshot = cast(Any, state.current_completion_snapshot)
        assert len(snapshot.choices) == 1
        message = snapshot.choices[0].message
        tool_calls = message.tool_calls
        assert tool_calls is not None
        assert len(tool_calls) == 1, f"Expected 1 tool call, got {len(tool_calls)}"
        call = tool_calls[0]
        assert call.id == "call_abc"
        func = call.function
        assert func is not None
        assert func.name == "list_files"
        assert func.arguments == ' {"path'

    def test_sparse_out_of_order_through_stream_state(self) -> None:
        """Index 1 arrives before index 0 — no data loss, list stays addressable."""
        from openai.types.chat import ChatCompletionChunk
        from openai.lib.streaming.chat import ChatCompletionStreamState
        from openai.types.chat.chat_completion_chunk import Choice as ChoiceChunk

        chunk1 = ChatCompletionChunk.construct(
            id="chatcmpl-2",
            created=0,
            model="gpt-4",
            choices=[
                ChoiceChunk.construct(
                    index=0,
                    delta={
                        "tool_calls": [
                            {
                                "index": 1,
                                "id": "call_b",
                                "function": {"name": "tool_b"},
                                "type": "function",
                            },
                        ]
                    },
                ),
            ],
        )

        chunk2 = ChatCompletionChunk.construct(
            id="chatcmpl-2",
            created=0,
            model="gpt-4",
            choices=[
                ChoiceChunk.construct(
                    index=0,
                    delta={
                        "tool_calls": [
                            {
                                "index": 0,
                                "id": "call_a",
                                "function": {"name": "tool_a"},
                                "type": "function",
                            },
                        ]
                    },
                ),
            ],
        )

        state = ChatCompletionStreamState()
        list(state.handle_chunk(chunk1))
        list(state.handle_chunk(chunk2))

        snapshot = cast(Any, state.current_completion_snapshot)
        message = snapshot.choices[0].message
        tool_calls = message.tool_calls
        assert tool_calls is not None
        assert len(tool_calls) == 2, f"Expected 2 tool calls, got {len(tool_calls)}"
        assert tool_calls[0].id == "call_a"
        assert tool_calls[1].id == "call_b"

    def test_backward_index_transition_does_not_finalize_tool(self) -> None:
        """Regression for Codex P2: when a higher-index tool call starts before
        a lower one (1 -> 0), the backward transition must not mark tool call 1
        as done — its arguments may still be streaming, and finalizing it
        early would suppress the corrected done event."""
        from openai.types.chat import ChatCompletionChunk
        from openai.lib.streaming.chat import ChatCompletionStreamState
        from openai.types.chat.chat_completion_chunk import Choice as ChoiceChunk

        chunk1 = ChatCompletionChunk.construct(
            id="chatcmpl-3",
            created=0,
            model="gpt-4",
            choices=[
                ChoiceChunk.construct(
                    index=0,
                    delta={
                        "tool_calls": [
                            {
                                "index": 1,
                                "id": "call_b",
                                "function": {"name": "tool_b", "arguments": ""},
                                "type": "function",
                            },
                        ]
                    },
                ),
            ],
        )

        chunk2 = ChatCompletionChunk.construct(
            id="chatcmpl-3",
            created=0,
            model="gpt-4",
            choices=[
                ChoiceChunk.construct(
                    index=0,
                    delta={
                        "tool_calls": [
                            {
                                "index": 0,
                                "id": "call_a",
                                "function": {"name": "tool_a", "arguments": ""},
                                "type": "function",
                            },
                        ]
                    },
                ),
            ],
        )

        chunk3 = ChatCompletionChunk.construct(
            id="chatcmpl-3",
            created=0,
            model="gpt-4",
            choices=[
                ChoiceChunk.construct(
                    index=0,
                    delta={
                        "tool_calls": [
                            {
                                "index": 1,
                                "function": {"arguments": '{"x": 1}'},
                            },
                        ]
                    },
                ),
            ],
        )

        state = ChatCompletionStreamState()
        events1 = list(state.handle_chunk(chunk1))
        events2 = list(state.handle_chunk(chunk2))
        events3 = list(state.handle_chunk(chunk3))

        # The backward transition (1 -> 0) must not finalize tool call 1 —
        # its arguments are still streaming.  A done event for index 1 with
        # empty arguments would be premature.
        done_events = [
            e
            for e in events1 + events2 + events3
            if getattr(e, "type", "") == "tool_calls.function.arguments.done"
        ]
        assert all(e.index != 1 for e in done_events), f"Premature done event for tool call 1: {done_events}"

        # The final snapshot must still hold both calls with merged arguments.
        snapshot = cast(Any, state.current_completion_snapshot)
        tool_calls = snapshot.choices[0].message.tool_calls
        assert tool_calls is not None
        assert len(tool_calls) == 2
        assert tool_calls[0].id == "call_a"
        assert tool_calls[1].id == "call_b"
        assert tool_calls[1].function.arguments == '{"x": 1}'
