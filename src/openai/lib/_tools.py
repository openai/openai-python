from __future__ import annotations

from typing import Any, Dict, Iterable, List, cast

import pydantic

from ._pydantic import to_strict_json_schema
from .._types import Omit
from .._utils import is_given
from ..types.chat import ChatCompletionFunctionToolParam
from ..types.shared_params import FunctionDefinition
from ..types.responses.function_tool_param import FunctionToolParam as ResponsesFunctionToolParam

_WEB_SEARCH_TOOL_TYPES = frozenset(
    {"web_search", "web_search_2025_08_26", "web_search_preview", "web_search_preview_2025_03_11"}
)


def _apply_web_search_default_location_tools(
    tools: Iterable[Any] | Omit,
) -> Iterable[Any] | Omit:
    """For web_search tools that lack user_location, inject user_location with type='approximate'.

    This prevents the server from defaulting to a US-based location when no
    user_location is specified, which is unexpected behavior for developers
    outside the US.
    """
    if not is_given(tools):
        return tools

    result: List[Any] = []
    changed = False
    for tool in tools:
        if isinstance(tool, dict) and tool.get("type") in _WEB_SEARCH_TOOL_TYPES and "user_location" not in tool:
            tool = {**tool, "user_location": {"type": "approximate"}}
            changed = True
        result.append(tool)

    return result if changed else tools


class PydanticFunctionTool(Dict[str, Any]):
    """Dictionary wrapper so we can pass the given base model
    throughout the entire request stack without having to special
    case it.
    """

    model: type[pydantic.BaseModel]

    def __init__(self, defn: FunctionDefinition, model: type[pydantic.BaseModel]) -> None:
        super().__init__(defn)
        self.model = model

    def cast(self) -> FunctionDefinition:
        return cast(FunctionDefinition, self)


class ResponsesPydanticFunctionTool(Dict[str, Any]):
    model: type[pydantic.BaseModel]

    def __init__(self, tool: ResponsesFunctionToolParam, model: type[pydantic.BaseModel]) -> None:
        super().__init__(tool)
        self.model = model

    def cast(self) -> ResponsesFunctionToolParam:
        return cast(ResponsesFunctionToolParam, self)


def pydantic_function_tool(
    model: type[pydantic.BaseModel],
    *,
    name: str | None = None,  # inferred from class name by default
    description: str | None = None,  # inferred from class docstring by default
) -> ChatCompletionFunctionToolParam:
    if description is None:
        # note: we intentionally don't use `.getdoc()` to avoid
        # including pydantic's docstrings
        description = model.__doc__

    function = PydanticFunctionTool(
        {
            "name": name or model.__name__,
            "strict": True,
            "parameters": to_strict_json_schema(model),
        },
        model,
    ).cast()

    if description is not None:
        function["description"] = description

    return {
        "type": "function",
        "function": function,
    }
