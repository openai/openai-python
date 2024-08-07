# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias

from ....._utils import PropertyInfo
from ....._compat import PYDANTIC_V2
from ....._models import BaseModel
from .function_tool_call import FunctionToolCall
from .file_search_tool_call import FileSearchToolCall
from .code_interpreter_tool_call import CodeInterpreterToolCall

if PYDANTIC_V2:
    from pydantic import field_serializer


__all__ = ["ToolCall", "BaseToolCall"]


class BaseToolCall(BaseModel):
    id: str
    """The ID of the tool call."""

    type: Literal["unknown"]
    """The type of tool call.
    """

    if PYDANTIC_V2:

        @field_serializer("type", when_used="always")  # type: ignore
        def serialize_unknown_type(self, type_: str) -> str:
            return type_


ToolCall: TypeAlias = Annotated[
    Union[BaseToolCall, CodeInterpreterToolCall, FileSearchToolCall, FunctionToolCall],
    PropertyInfo(discriminator="type"),
]
