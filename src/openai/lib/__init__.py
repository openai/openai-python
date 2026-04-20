from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ._tools import pydantic_function_tool as pydantic_function_tool
    from ._parsing import ResponseFormatT as ResponseFormatT


def __getattr__(name: str) -> Any:
    if name == "pydantic_function_tool":
        from ._tools import pydantic_function_tool

        globals()[name] = pydantic_function_tool
        return pydantic_function_tool

    if name == "ResponseFormatT":
        from ._parsing import ResponseFormatT

        globals()[name] = ResponseFormatT
        return ResponseFormatT

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
