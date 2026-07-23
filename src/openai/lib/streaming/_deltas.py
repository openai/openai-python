from __future__ import annotations

from ..._utils import is_dict, is_list


def _normalize_indexed_list(items: list[object]) -> list[object]:
    """Merge list entries that share the same integer ``index`` key.

    When the first delta chunk for a key carries multiple entries with the
    same ``index`` (e.g. tool name **and** the start of arguments both at
    index 0), those entries *must* be merged into a single logical entry.
    Without this step the accumulator stores them as separate physical list
    entries; the second entry is then orphaned because every subsequent delta
    merges into ``acc_value[index]`` (the first one), leaving argument
    fragments stranded and producing invalid final JSON.
    """
    if not items:
        return items
    if not all(is_dict(item) for item in items):
        return items

    # Count occurrences of each integer index.
    index_counts: dict[int, int] = {}
    for item in items:
        idx = item.get("index")
        if isinstance(idx, int):
            index_counts[idx] = index_counts.get(idx, 0) + 1

    # No duplicate indices -> nothing to normalise.
    if not index_counts or max(index_counts.values()) <= 1:
        return items

    # Merge entries that share the same index.
    merged: dict[int, dict[object, object]] = {}
    for item in items:
        idx = item.get("index")
        if isinstance(idx, int):
            if idx in merged:
                merged[idx] = accumulate_delta(merged[idx], dict(item))
            else:
                merged[idx] = dict(item)

    # Rebuild the list ordered by index.
    return [
        {**entry, "index": idx}
        for idx, entry in sorted(merged.items())
    ]


def accumulate_delta(acc: dict[object, object], delta: dict[object, object]) -> dict[object, object]:
    for key, delta_value in delta.items():
        if key not in acc:
            acc[key] = _normalize_indexed_list(delta_value) if is_list(delta_value) else delta_value
            continue

        acc_value = acc[key]
        if acc_value is None:
            acc[key] = _normalize_indexed_list(delta_value) if is_list(delta_value) else delta_value
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

                try:
                    acc_entry = acc_value[index]
                except IndexError:
                    acc_value.insert(index, delta_entry)
                else:
                    if not is_dict(acc_entry):
                        raise TypeError("not handled yet")

                    acc_value[index] = accumulate_delta(acc_entry, delta_entry)

        acc[key] = acc_value

    return acc
