from typing import Any

import orjson
import pydantic

from .._compat import model_dump


def openapi_dumps(obj: Any) -> bytes:
    """
    Serialize an object to UTF-8 encoded JSON bytes.

    Extends orjson.dumps with support for additional types
    commonly used in the SDK, such as `datetime`, `pydantic.BaseModel`, etc.
    """
    return orjson.dumps(obj, default=_orjson_default, option=orjson.OPT_NON_STR_KEYS)


def _orjson_default(obj: Any) -> Any:
    if isinstance(obj, pydantic.BaseModel):
        return model_dump(obj, exclude_unset=True, mode="json", by_alias=True)
    raise TypeError
