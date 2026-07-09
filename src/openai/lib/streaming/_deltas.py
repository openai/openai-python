from __future__ import annotations

from ..._utils import is_dict, is_list


def _accumulate_list_delta(acc_value: list[object], delta_value: list[object]) -> list[object]:
    # for lists of non-dictionary items we'll only ever get new entries
    # in the array, existing entries will never be changed
    if all(isinstance(x, (str, int, float)) for x in acc_value + delta_value):
        acc_value.extend(delta_value)
        return acc_value

    for delta_entry in delta_value:
        if not is_dict(delta_entry):
            raise TypeError(f"Unexpected list delta entry is not a dictionary: {delta_entry}")

        try:
            index = delta_entry["index"]
        except KeyError as exc:
            raise RuntimeError(f"Expected list delta entry to have an `index` key; {delta_entry}") from exc

        if not isinstance(index, int):
            raise TypeError(f"Unexpected, list delta entry `index` value is not an integer; {index}")

        existing_index = next(
            (idx for idx, entry in enumerate(acc_value) if is_dict(entry) and entry.get("index") == index),
            None,
        )

        if existing_index is None:
            acc_value.insert(index, delta_entry)
            continue

        acc_entry = acc_value[existing_index]
        if not is_dict(acc_entry):
            raise TypeError("not handled yet")

        acc_value[existing_index] = accumulate_delta(acc_entry, delta_entry)

    return acc_value


def accumulate_delta(acc: dict[object, object], delta: dict[object, object]) -> dict[object, object]:
    for key, delta_value in delta.items():
        if key not in acc:
            if is_list(delta_value):
                delta_value = _accumulate_list_delta([], delta_value)
            acc[key] = delta_value
            continue

        acc_value = acc[key]
        if acc_value is None:
            if is_list(delta_value):
                delta_value = _accumulate_list_delta([], delta_value)
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
            acc_value = _accumulate_list_delta(acc_value, delta_value)

        acc[key] = acc_value

    return acc
