from __future__ import annotations

from ..._utils import is_dict, is_list


def _merge_indexed_list(items: list[object]) -> list[object]:
    """Merge list entries that share the same ``index`` value.

    Streaming chunks may contain multiple entries with the same logical
    ``index`` (e.g. a tool-call name and its first argument fragment in one
    SSE event).  When such a list is stored for the first time it must be
    collapsed by logical index so that later chunks merge correctly.
    """
    if not items or not is_dict(items[0]) or "index" not in items[0]:  # type: ignore[arg-type]
        return items

    merged: dict[int, object] = {}
    order: list[int] = []
    for item in items:
        if not is_dict(item):
            continue
        idx = item.get("index")  # type: ignore[union-attr]
        if not isinstance(idx, int):
            continue
        if idx in merged:
            existing = merged[idx]
            if is_dict(existing):
                merged[idx] = accumulate_delta(existing, item)  # type: ignore[arg-type]
        else:
            order.append(idx)
            merged[idx] = item

    return [merged[i] for i in order]


def accumulate_delta(acc: dict[object, object], delta: dict[object, object]) -> dict[object, object]:
    for key, delta_value in delta.items():
        if key not in acc:
            if is_list(delta_value):
                delta_value = _merge_indexed_list(delta_value)
            acc[key] = delta_value
            continue

        acc_value = acc[key]
        if acc_value is None:
            if is_list(delta_value):
                delta_value = _merge_indexed_list(delta_value)
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
