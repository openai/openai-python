from __future__ import annotations

from typing import Any, Dict, cast

import pydantic

from .._types import Omit, omit
from .._utils import is_given
from ._pydantic import to_strict_json_schema
from ..types.chat import ChatCompletionFunctionToolParam
from ..types.shared_params import FunctionDefinition
from ..types.responses.function_tool_param import FunctionToolParam as ResponsesFunctionToolParam


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


def pydantic_responses_function_tool(
    model: type[pydantic.BaseModel],
    *,
    name: str | None = None,
    description: str | None = None,
    defer_loading: bool | Omit = omit,
) -> ResponsesFunctionToolParam:
    """Build a Responses function tool with automatic Pydantic argument parsing.

    Use with ``responses.parse`` or ``responses.stream``. Set ``defer_loading``
    alongside a tool-search tool to make the function discoverable on demand.
    """
    function = pydantic_function_tool(model, name=name, description=description)["function"]
    tool = ResponsesPydanticFunctionTool(cast(ResponsesFunctionToolParam, {"type": "function", **function}), model)
    if is_given(defer_loading):
        tool["defer_loading"] = defer_loading
    return tool.cast()
