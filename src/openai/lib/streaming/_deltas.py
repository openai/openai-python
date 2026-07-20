from __future__ import annotations

from ..._utils import is_dict, is_list


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
                found = False
                for i, existing in enumerate(acc_value):
                    if is_dict(existing) and existing.get("index") == index:
                        acc_value[i] = accumulate_delta(existing, delta_entry)
                        found = True
                        break

                if not found:
                    # Ensure the list is large enough
                    while len(acc_value) <= index:
                        acc_value.append({})
                    acc_value[index] = delta_entry

        acc[key] = acc_value

    return acc


def _coalesce_list_by_index(lst: list[object]) -> list[object]:
    """Merge list entries that share the same ``index`` field into a single entry.

    When the first streamed chunk contains multiple entries with the same
    ``index`` (e.g. from speculative decoding), storing the list directly would
    leave duplicate entries. This function coalesces them by merging entries
    with the same index using :func:`accumulate_delta`, so the snapshot starts
    in a clean state. (#3201)
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
            result.append(entry)
    return result
