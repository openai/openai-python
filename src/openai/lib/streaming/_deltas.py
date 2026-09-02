from __future__ import annotations

from ..._utils import is_dict, is_list


def _normalize_indexed_list(items: list[object]) -> list[object]:
    """Merge list entries that share the same `index` key.

    Some providers send multiple delta entries with the same index in a single
    chunk (e.g. first tool_call chunk contains both the id/name AND the start
    of arguments, both at index 0).  Without merging, the second entry is
    stranded and never accumulated into.
    """
    by_index: dict[int, dict[object, object]] = {}
    order: list[int] = []
    for item in items:
        if not is_dict(item):
            return items  # non-dict list → nothing to normalise
        idx = item.get("index")  # type: ignore[union-attr]
        if not isinstance(idx, int):
            return items  # no integer index → nothing to normalise
        if idx not in by_index:
            by_index[idx] = item  # type: ignore[assignment]
            order.append(idx)
        else:
            by_index[idx] = accumulate_delta(by_index[idx], item)  # type: ignore[arg-type]
    return [by_index[i] for i in order]  # type: ignore[misc]


def accumulate_delta(acc: dict[object, object], delta: dict[object, object]) -> dict[object, object]:
    for key, delta_value in delta.items():
        if key not in acc:
            if is_list(delta_value) and delta_value:
                acc[key] = _normalize_indexed_list(delta_value)
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
