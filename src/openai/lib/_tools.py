from __future__ import annotations

from typing import Any, Dict, cast

import pydantic

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
    """Dictionary wrapper that carries a Pydantic model for Responses API function tools."""

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
    """Create a :class:`ChatCompletionFunctionToolParam` from a Pydantic model.

    The tool ``name`` defaults to the model class name and ``description``
    defaults to the model's docstring.  A strict JSON schema is generated
    automatically from the model.
    """
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
