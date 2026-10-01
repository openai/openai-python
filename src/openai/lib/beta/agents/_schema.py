from __future__ import annotations

from copy import deepcopy
from typing import Any, cast

import pydantic

from ...._compat import PYDANTIC_V1, model_json_schema
from ..._pydantic import _ensure_strict_json_schema


def model_schema(
    model: type[pydantic.BaseModel] | pydantic.TypeAdapter[Any], *, strict: bool = False
) -> dict[str, Any]:
    # Pydantic v1 caches schema dictionaries. Input and output policies must not
    # mutate each other's schemas or the model's cache.
    schema = deepcopy(
        model.json_schema()
        if not PYDANTIC_V1 and isinstance(model, pydantic.TypeAdapter)
        else model_json_schema(cast(type[pydantic.BaseModel], model))
    )
    return _ensure_strict_json_schema(schema, path=(), root=schema) if strict else schema
