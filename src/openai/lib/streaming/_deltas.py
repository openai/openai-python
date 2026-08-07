from __future__ import annotations

from ..._utils import is_dict, is_list


def _find_list_entry(acc_value: list[object], index: int) -> int | None:
    for acc_index, acc_entry in enumerate(acc_value):
        if is_dict(acc_entry) and acc_entry.get("index") == index:
            return acc_index

    return None


def _has_indexed_entries(delta_value: list[object]) -> bool:
    return any(is_dict(delta_entry) and "index" in delta_entry for delta_entry in delta_value)


def _accumulate_list(acc_value: list[object], delta_value: list[object]) -> list[object]:
    # for lists of non-dictionary items we'll only ever get new entries
    # in the array, existing entries will never be changed
    if all(isinstance(x, (str, int, float)) for x in acc_value) and all(
        isinstance(x, (str, int, float)) for x in delta_value
    ):
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

        acc_index = _find_list_entry(acc_value, index)
        if acc_index is None:
            acc_value.insert(min(index, len(acc_value)), delta_entry)
            continue

        acc_entry = acc_value[acc_index]
        if not is_dict(acc_entry):
            raise TypeError("not handled yet")

        acc_value[acc_index] = accumulate_delta(acc_entry, delta_entry)

    return acc_value


def accumulate_delta(acc: dict[object, object], delta: dict[object, object]) -> dict[object, object]:
    for key, delta_value in delta.items():
        if key not in acc:
            acc[key] = (
                _accumulate_list([], delta_value)
                if is_list(delta_value) and _has_indexed_entries(delta_value)
                else delta_value
            )
            continue

        acc_value = acc[key]
        if acc_value is None:
            acc[key] = (
                _accumulate_list([], delta_value)
                if is_list(delta_value) and _has_indexed_entries(delta_value)
                else delta_value
            )
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
            acc_value = _accumulate_list(acc_value, delta_value)

        acc[key] = acc_value

    return acc
