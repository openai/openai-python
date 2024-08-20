# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._compat import PYDANTIC_V2
from ..._models import BaseModel
from .function_tool import FunctionTool
from .file_search_tool import FileSearchTool
from .code_interpreter_tool import CodeInterpreterTool

if PYDANTIC_V2:
    from pydantic import field_serializer


__all__ = ["AssistantTool", "BaseTool"]


class BaseTool(BaseModel):
    type: Literal["unknown"]
    """A tool type"""

    if PYDANTIC_V2:

        @field_serializer("type", when_used="always")  # type: ignore
        def serialize_unknown_type(self, type_: str) -> str:
            return type_


AssistantTool: TypeAlias = Annotated[
    Union[BaseTool, CodeInterpreterTool, FileSearchTool, FunctionTool], PropertyInfo(discriminator="type")
]
