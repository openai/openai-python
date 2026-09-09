from __future__ import annotations

from ..._utils import is_dict, is_list

#: Maximum gap padded between logical tool-call indexes.  A stream with a
#: huge sparse index (e.g. index 1,000,000) must not allocate storage
#: proportional to the numeric index; entries beyond this bound are appended
#: at the end and still found by the index-based merge.
_MAX_INDEX_PADDING = 1024


def _is_placeholder(entry: object) -> bool:
    """Detect a gap-filler placeholder that should be replaced in-place.

    When a sparse tool-call stream emits index 0 then 2, the gap at index 1
    is padded with an empty ``{}``.  After the snapshot is round-tripped
    through ``model_dump`` (which happens on the next chunk), that placeholder
    is no longer empty — it becomes a dict of unset tool-call fields such as
    ``{"id": None, "function": None, "type": None}``.  Both forms must be
    detected so a later-arriving entry at the same index *replaces* the
    placeholder instead of being inserted before it (which would shift
    higher-index entries and break ``tool_calls[index]`` lookups).
    """
    if not is_dict(entry):
        return False
    # Empty placeholder from the padding path.
    if not entry:
        return True
    # Dumped placeholder: every value is None (or the dict is empty).
    return all(v is None for v in entry.values())


def accumulate_delta(acc: dict[object, object], delta: dict[object, object]) -> dict[object, object]:
    for key, delta_value in delta.items():
        if key not in acc:
            # Coalesce duplicate-index entries before storing so the snapshot
            # starts in a clean state, and normalize single entries to their
            # logical slot. (#3201)
            if is_list(delta_value) and any(is_dict(x) for x in delta_value):
                delta_value = _coalesce_list_by_index(delta_value)
            acc[key] = delta_value
            continue

        acc_value = acc[key]
        if acc_value is None:
            # Coalesce duplicate-index entries here too — a prior chunk may
            # have set acc[key] to None via a delta that only contained the
            # key without a value, and now the actual list arrives. (#3201)
            if is_list(delta_value) and any(is_dict(x) for x in delta_value):
                delta_value = _coalesce_list_by_index(delta_value)
            acc[key] = delta_value
            continue

        # the `index` property is used in arrays of objects so it should
        # not be accumulated like other values e.g.
        # [{'foo': 'bar', 'index': 0}]
        #
        # the same applies to `type` properties as they're used for
        # discriminated unions
        if key == "index" or key == "type":
            acc[key] = delta_value
            continue

        if isinstance(acc_value, str) and isinstance(delta_value, str):
            # Only streamed fields accumulate.  Repeated metadata (e.g. a
            # duplicate-index entry repeating `id` or `function.name` from a
            # speculative decoder) must be replaced, not concatenated —
            # otherwise the value becomes `call_abccall_abc`. (#3201)
            if key in ("content", "refusal", "arguments"):
                acc_value += delta_value
            else:
                acc_value = delta_value
        elif isinstance(acc_value, (int, float)) and isinstance(delta_value, (int, float)):
            acc_value += delta_value
        elif is_dict(acc_value) and is_dict(delta_value):
            acc_value = accumulate_delta(acc_value, delta_value)
        elif is_list(acc_value) and is_list(delta_value):
            # for lists of non-dictionary items we'll only ever get new entries
            # in the array, existing entries will never be changed
            if acc_value and all(isinstance(x, (str, int, float)) for x in acc_value):
                acc_value.extend(delta_value)
                continue

            # Coalesce the incoming list so duplicate-index entries are merged
            # before placement — covers the empty-acc fast path (an explicit
            # `tool_calls: []` from a prior chunk) and any un-coalesced first
            # chunk. (#3201)
            if any(is_dict(x) for x in delta_value):
                delta_value = _coalesce_list_by_index(delta_value)

            # Build an index map once so merging is O(n) instead of O(n²).
            index_map: dict[int, list[int]] = {}
            for i, existing in enumerate(acc_value):
                if is_dict(existing) and isinstance(existing.get("index"), int):
                    index_map.setdefault(existing["index"], []).append(i)

            for delta_entry in delta_value:
                if not is_dict(delta_entry):
                    raise TypeError(f"Unexpected list delta entry is not a dictionary: {delta_entry}")
                if _is_placeholder(delta_entry):
                    # Gap-filler from coalescing — nothing to merge.
                    continue

                try:
                    index = delta_entry["index"]
                except KeyError as exc:
                    raise RuntimeError(f"Expected list delta entry to have an `index` key; {delta_entry}") from exc

                if not isinstance(index, int):
                    raise TypeError(f"Unexpected, list delta entry `index` value is not an integer; {index}")

                # Merge by logical index, not physical position. (#3201)
                # When the first chunk contains multiple entries with the same
                # index (e.g. from speculative decoding), the physical position
                # does not match the logical index. Find the existing entry by
                # its index field and merge into it.
                #
                # If acc_value already contains duplicate-index entries
                # (e.g. from a prior chunk that wasn't coalesced), merge into
                # all of them so none are stranded.
                positions = index_map.get(index)
                if positions:
                    for pos in positions:
                        acc_value[pos] = accumulate_delta(acc_value[pos], delta_entry)
                    continue

                # Add the new entry.  Don't assume the logical index is a
                # safe physical slot — if acc_value already has entries at
                # higher indexes (e.g. [{"index": 1, ...}] and index 0
                # arrives), acc_value[index] would overwrite the existing
                # entry.  Place the entry at the position matching the
                # logical index so downstream code that does
                # tool_calls[index] (treating logical index as physical
                # position) reads the right entry.  Bound the padding so a
                # huge sparse index cannot allocate storage proportional to
                # its value.
                if len(acc_value) <= index:
                    if index - len(acc_value) <= _MAX_INDEX_PADDING:
                        while len(acc_value) < index:
                            acc_value.append({})
                        acc_value.append(delta_entry)
                    else:
                        acc_value.append(delta_entry)
                else:
                    # The list is large enough but no entry has this
                    # index.  If the slot at `index` is a placeholder
                    # (empty {} or a dumped placeholder with only None
                    # values from a model_dump round-trip), replace it
                    # in-place.  Otherwise insert at the correct
                    # position to keep the list addressable by logical
                    # index.
                    existing = acc_value[index]
                    if _is_placeholder(existing):
                        acc_value[index] = delta_entry
                    else:
                        acc_value.insert(index, delta_entry)
                index_map.setdefault(index, []).append(len(acc_value) - 1)

        acc[key] = acc_value

    return acc


def _coalesce_list_by_index(lst: list[object]) -> list[object]:
    """Merge list entries that share the same ``index`` field into a single entry.

    When the first streamed chunk contains multiple entries with the same
    ``index`` (e.g. from speculative decoding), storing the list directly would
    leave duplicate entries. This function coalesces them by merging entries
    with the same index using :func:`accumulate_delta`, so the snapshot starts
    in a clean state. (#3201)

    The result is sorted by the ``index`` field so the list stays addressable
    by logical index — downstream code does ``tool_calls[index]`` treating
    logical index as physical position.  A single entry whose index does not
    match its position is normalized to its logical slot as well.
    """
    merged: dict[int, object] = {}
    tail: list[object] = []
    for entry in lst:
        if not is_dict(entry):
            tail.append(entry)
            continue
        index = entry.get("index")
        if not isinstance(index, int):
            if _is_placeholder(entry):
                # Gap-filler from a previous padding pass — replaced by the
                # real entry at the same logical index.
                continue
            tail.append(entry)
            continue
        if index in merged:
            merged[index] = accumulate_delta(merged[index], entry)
        else:
            merged[index] = entry

    if not merged:
        return list(lst)

    max_index = max(merged)
    if max_index <= _MAX_INDEX_PADDING:
        result = [merged.get(i, {}) for i in range(max_index + 1)]
    else:
        # Huge sparse index: materialize only up to the bound, then append
        # the remaining entries in index order so allocation stays bounded.
        result = [merged.get(i, {}) for i in range(_MAX_INDEX_PADDING + 1)]
        result.extend(merged[i] for i in sorted(merged) if i > _MAX_INDEX_PADDING)
    return result + tail
