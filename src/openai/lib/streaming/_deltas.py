from __future__ import annotations

from ..._utils import is_dict, is_list


def accumulate_delta(acc: dict[object, object], delta: dict[object, object]) -> dict[object, object]:
    for key, delta_value in delta.items():
        if key not in acc:
            # For lists of indexed dicts (e.g. tool_calls), initialize an empty
            # list and fall through to the merge logic so that entries with
            # duplicate indexes in the first chunk are correctly merged.
            if (
                is_list(delta_value)
                and delta_value
                and is_dict(delta_value[0])
                and "index" in delta_value[0]
            ):
                acc[key] = []
            else:
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
            if acc_value and all(isinstance(x, (str, int, float)) for x in acc_value):
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

                # Find existing entry by its index field value rather
                # than by list position, since list position may diverge
                # from the index field (e.g. duplicate or out-of-order indexes).
                existing_entry = None
                existing_entry_idx = None
                for i, entry in enumerate(acc_value):
                    if is_dict(entry) and entry.get("index") == index:
                        existing_entry = entry
                        existing_entry_idx = i
                        break

                if existing_entry is not None:
                    acc_value[existing_entry_idx] = accumulate_delta(existing_entry, delta_entry)
                else:
                    acc_value.append(delta_entry)

        acc[key] = acc_value

    return acc
