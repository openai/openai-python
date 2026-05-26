from __future__ import annotations

from ..._utils import is_dict, is_list


def _accumulate_list(
    acc_list: list[object],
    delta_list: list[object],
    acc: dict[object, object],
    delta: dict[object, object],
) -> list[object]:
    """Merge *delta_list* into *acc_list* using the logical ``index`` field.

    Each entry in a tool-call (or similar) list carries an ``"index"`` key that
    identifies which *logical* object it belongs to.  Physical list position must
    **not** be used as the key because a single streaming chunk may contain
    multiple entries that share the same logical index (e.g. the first chunk may
    emit both the tool-call header *and* the first argument fragment for
    ``index=0`` in the same delta).  Using the logical index prevents those
    entries from being stored as separate physical slots and later causing
    argument accumulation to target the wrong slot.
    """
    for delta_entry in delta_list:
        if not is_dict(delta_entry):
            raise TypeError(f"Unexpected list delta entry is not a dictionary: {delta_entry}")

        try:
            index = delta_entry["index"]  # type: ignore[index]
        except KeyError as exc:
            raise RuntimeError(f"Expected list delta entry to have an `index` key; {delta_entry}") from exc

        if not isinstance(index, int):
            raise TypeError(f"Unexpected, list delta entry `index` value is not an integer; {index}")

        # Search for an existing entry with this logical index.
        found = False
        for i, existing in enumerate(acc_list):
            if is_dict(existing) and existing.get("index") == index:  # type: ignore[union-attr]
                acc_list[i] = accumulate_delta(existing, delta_entry)  # type: ignore[arg-type]
                found = True
                break

        if not found:
            acc_list.append(delta_entry)

    return acc_list


def accumulate_delta(acc: dict[object, object], delta: dict[object, object]) -> dict[object, object]:
    for key, delta_value in delta.items():
        if key not in acc:
            # When a list is encountered for the first time, run it through the
            # same index-based merge so that duplicate logical indexes within a
            # single first chunk are collapsed immediately rather than being
            # stored as distinct physical slots.
            if is_list(delta_value) and delta_value and all(is_dict(x) and "index" in x for x in delta_value):  # type: ignore[union-attr]
                acc[key] = _accumulate_list([], delta_value, acc, delta)  # type: ignore[arg-type]
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

            acc_value = _accumulate_list(acc_value, delta_value, acc, delta)  # type: ignore[arg-type]

        acc[key] = acc_value

    return acc
