from __future__ import annotations

from ..._utils import is_dict, is_list


def accumulate_delta(acc: dict[object, object], delta: dict[object, object]) -> dict[object, object]:
    for key, delta_value in delta.items():
        if key not in acc:
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

            # Build a map from logical index -> position in acc_value so we can
            # look up existing entries by their "index" field rather than by
            # physical list position.  Using physical position breaks when a
            # single chunk contains multiple entries that share the same logical
            # index (e.g. speculative-decoding servers that split the first
            # tool_call entry across two objects both carrying index=0).
            acc_index_map: dict[int, int] = {}
            for pos, entry in enumerate(acc_value):
                if is_dict(entry) and isinstance(entry.get("index"), int):
                    logical_idx = entry["index"]
                    # keep the first occurrence if there are duplicates already
                    if logical_idx not in acc_index_map:
                        acc_index_map[logical_idx] = pos

            for delta_entry in delta_value:
                if not is_dict(delta_entry):
                    raise TypeError(f"Unexpected list delta entry is not a dictionary: {delta_entry}")

                try:
                    index = delta_entry["index"]
                except KeyError as exc:
                    raise RuntimeError(f"Expected list delta entry to have an `index` key; {delta_entry}") from exc

                if not isinstance(index, int):
                    raise TypeError(f"Unexpected, list delta entry `index` value is not an integer; {index}")

                if index in acc_index_map:
                    # merge into the existing entry at the stored physical position
                    pos = acc_index_map[index]
                    acc_entry = acc_value[pos]
                    if not is_dict(acc_entry):
                        raise TypeError("not handled yet")
                    acc_value[pos] = accumulate_delta(acc_entry, delta_entry)
                else:
                    # new logical index: append and record its physical position
                    acc_index_map[index] = len(acc_value)
                    acc_value.append(delta_entry)

        acc[key] = acc_value

    return acc
