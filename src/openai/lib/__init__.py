from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ._tools import pydantic_function_tool as pydantic_function_tool
    from ._parsing import ResponseFormatT as ResponseFormatT

__all__ = ["ResponseFormatT", "pydantic_function_tool"]

_LAZY_IMPORTS = {
    "ResponseFormatT": ("._parsing", "ResponseFormatT"),
    "pydantic_function_tool": ("._tools", "pydantic_function_tool"),
}


def __getattr__(name: str) -> Any:
    lazy_import = _LAZY_IMPORTS.get(name)
    if lazy_import is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name, attribute_name = lazy_import
    value = getattr(importlib.import_module(module_name, __name__), attribute_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_LAZY_IMPORTS))
