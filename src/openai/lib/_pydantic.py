from __future__ import annotations

from typing import Any
from typing_extensions import TypeGuard

import pydantic

from .._utils import is_dict as _is_dict, is_list
from .._compat import model_json_schema


def to_strict_json_schema(model: type[pydantic.BaseModel]) -> dict[str, Any]:
    return _ensure_strict_json_schema(model_json_schema(model), path=())


def _ensure_strict_json_schema(
    json_schema: object,
    path: tuple[str, ...],
) -> dict[str, Any]:
    """Mutates the given JSON schema to ensure it conforms to the `strict` standard
    that the API expects.
    """
    if not is_dict(json_schema):
        raise TypeError(f"Expected {json_schema} to be a dictionary; path={path}")

    typ = json_schema.get("type")
    if typ == "object" and "additionalProperties" not in json_schema:
        json_schema["additionalProperties"] = False

    # object types
    # { 'type': 'object', 'properties': { 'a':  {...} } }
    properties = json_schema.get("properties")
    if is_dict(properties):
        json_schema["required"] = [prop for prop in properties.keys()]
        json_schema["properties"] = {
            key: _ensure_strict_json_schema(prop_schema, path=(*path, "properties", key))
            for key, prop_schema in properties.items()
        }

    # arrays
    # { 'type': 'array', 'items': {...} }
    items = json_schema.get("items")
    if is_dict(items):
        json_schema["items"] = _ensure_strict_json_schema(items, path=(*path, "items"))

    # unions
    any_of = json_schema.get("anyOf")
    if is_list(any_of):
        json_schema["anyOf"] = [
            _ensure_strict_json_schema(variant, path=(*path, "anyOf", str(i))) for i, variant in enumerate(any_of)
        ]

    # intersections
    all_of = json_schema.get("allOf")
    if is_list(all_of):
        json_schema["allOf"] = [
            _ensure_strict_json_schema(entry, path=(*path, "anyOf", str(i))) for i, entry in enumerate(all_of)
        ]

    defs = json_schema.get("$defs")
    if is_dict(defs):
        for def_name, def_schema in defs.items():
            _ensure_strict_json_schema(def_schema, path=(*path, "$defs", def_name))

    return json_schema


def is_dict(obj: object) -> TypeGuard[dict[str, object]]:
    # just pretend that we know there are only `str` keys
    # as that check is not worth the performance cost
    return _is_dict(obj)
