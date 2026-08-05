from __future__ import annotations

from ..._utils import is_dict, is_list


def accumulate_delta(acc: dict[object, object], delta: dict[object, object]) -> dict[object, object]:
    for key, delta_value in delta.items():
        if key not in acc:
            # Normalize lists of dicts with index fields before storing
            # to handle cases like tool_calls with duplicate indexes
            # in the first chunk (see issue #3201)
            if is_list(delta_value) and all(is_dict(x) for x in delta_value):
                normalized: list[object] = []
                index_map: dict[int, int] = {}
                for entry in delta_value:
                    idx = entry.get("index")
                    if idx is not None and isinstance(idx, int) and idx in index_map:
                        existing_pos = index_map[idx]
                        normalized[existing_pos] = accumulate_delta(normalized[existing_pos], entry)
                    else:
                        if idx is not None and isinstance(idx, int):
                            index_map[idx] = len(normalized)
                        normalized.append(entry)
                acc[key] = normalized
            else:
                acc[key] = delta_value
            continue

        acc_value = acc[key]
        if acc_value is None:
            # Normalize lists of dicts with index fields before storing
            if is_list(delta_value) and all(is_dict(x) for x in delta_value):
                normalized = []
                index_map = {}
                for entry in delta_value:
                    idx = entry.get("index")
                    if idx is not None and isinstance(idx, int) and idx in index_map:
                        existing_pos = index_map[idx]
                        normalized[existing_pos] = accumulate_delta(normalized[existing_pos], entry)
                    else:
                        if idx is not None and isinstance(idx, int):
                            index_map[idx] = len(normalized)
                        normalized.append(entry)
                acc[key] = normalized
            else:
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

            # Normalize delta entries by index before merging.
            # When multiple entries share the same index (e.g., tool_calls
            # with duplicate indexes in the first chunk), they must be merged
            # together first so that subsequent chunks merge into the correct
            # logical position rather than stranding entries at duplicate indexes.
            normalized_delta: list[object] = []
            index_map: dict[int, int] = {}
            for entry in delta_value:
                if not is_dict(entry):
                    raise TypeError(f"Unexpected list delta entry is not a dictionary: {entry}")

                try:
                    idx = entry["index"]
                except KeyError as exc:
                    raise RuntimeError(f"Expected list delta entry to have an `index` key; {entry}") from exc

                if not isinstance(idx, int):
                    raise TypeError(f"Unexpected, list delta entry `index` value is not an integer; {idx}")

                if idx in index_map:
                    existing_pos = index_map[idx]
                    normalized_delta[existing_pos] = accumulate_delta(normalized_delta[existing_pos], entry)
                else:
                    index_map[idx] = len(normalized_delta)
                    normalized_delta.append(entry)

            for delta_entry in normalized_delta:
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
