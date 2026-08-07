from __future__ import annotations

from ..._utils import is_dict, is_list


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
            # When the first chunk contains a list with multiple entries at the
            # same index (e.g. from speculative decoding), storing it directly
            # would leave duplicate entries that later merges can't fix. (#3201)
            # Coalesce duplicate-index entries before storing.
            if is_list(delta_value) and len(delta_value) > 1:
                delta_value = _coalesce_list_by_index(delta_value)
            acc[key] = delta_value
            continue

        acc_value = acc[key]
        if acc_value is None:
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
            acc_value += delta_value
        elif isinstance(acc_value, (int, float)) and isinstance(delta_value, (int, float)):
            acc_value += delta_value
        elif is_dict(acc_value) and is_dict(delta_value):
            acc_value = accumulate_delta(acc_value, delta_value)
        elif is_list(acc_value) and is_list(delta_value):
            # for lists of non-dictionary items we'll only ever get new entries
            # in the array, existing entries will never be changed
            if all(isinstance(x, (str, int, float)) for x in acc_value):
                acc_value.extend(delta_value)
                continue

            for delta_entry in delta_value:
                if not is_dict(delta_entry):
                    raise TypeError(f"Unexpected list delta entry is not a dictionary: {delta_entry}")

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
                found = False
                for i, existing in enumerate(acc_value):
                    if is_dict(existing) and existing.get("index") == index:
                        acc_value[i] = accumulate_delta(existing, delta_entry)
                        found = True

                if not found:
                    # Add the new entry.  Don't assume the logical index is a
                    # safe physical slot — if acc_value already has entries at
                    # higher indexes (e.g. [{"index": 1, ...}] and index 0
                    # arrives), acc_value[index] would overwrite the existing
                    # entry.  Place the entry at the position matching the
                    # logical index so downstream code that does
                    # tool_calls[index] (treating logical index as physical
                    # position) reads the right entry.
                    if len(acc_value) <= index:
                        while len(acc_value) < index:
                            acc_value.append({})
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
    logical index as physical position.
    """
    result: list[object] = []
    for entry in lst:
        if not is_dict(entry):
            result.append(entry)
            continue
        index = entry.get("index")
        if not isinstance(index, int):
            result.append(entry)
            continue
        # Find an existing entry with the same index
        found = False
        for i, existing in enumerate(result):
            if is_dict(existing) and existing.get("index") == index:
                result[i] = accumulate_delta(existing, entry)
                found = True
                break
        if not found:
            # Place at the position matching the logical index, padding
            # with empty dicts if needed, so the list is addressable by
            # logical index.
            while len(result) <= index:
                result.append({})
            # Replace the placeholder at `index` (empty {} or a dumped
            # placeholder with only None values from a model_dump round-trip)
            # or shift if occupied by a real entry.
            existing = result[index]
            if _is_placeholder(existing):
                result[index] = entry
            else:
                result.insert(index, entry)
    return result
