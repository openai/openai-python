# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias

from ....._utils import PropertyInfo
from ....._compat import PYDANTIC_V2
from ....._models import BaseModel
from .function_tool_call_delta import FunctionToolCallDelta
from .file_search_tool_call_delta import FileSearchToolCallDelta
from .code_interpreter_tool_call_delta import CodeInterpreterToolCallDelta

if PYDANTIC_V2:
    from pydantic import field_serializer


__all__ = ["ToolCallDelta", "BaseToolCallDelta"]


class BaseToolCallDelta(BaseModel):
    index: int
    """The index of the tool call in the tool calls array."""

    type: Literal["unknown"]
    """The type of tool call.
    """

    if PYDANTIC_V2:

        @field_serializer("type", when_used="always")  # type: ignore
        def serialize_unknown_type(self, type_: str) -> str:
            return type_


ToolCallDelta: TypeAlias = Annotated[
    Union[BaseToolCallDelta, CodeInterpreterToolCallDelta, FileSearchToolCallDelta, FunctionToolCallDelta],
    PropertyInfo(discriminator="type"),
]
