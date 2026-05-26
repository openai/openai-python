# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .custom_tool import CustomTool

__all__ = ["NamespaceTool", "Tool", "ToolFunction"]


class ToolFunction(BaseModel):
    name: str

    type: Literal["function"]

    defer_loading: Optional[bool] = None
    """Whether this function should be deferred and discovered via tool search."""

    description: Optional[str] = None

    parameters: Optional[object] = None

    strict: Optional[bool] = None


Tool: TypeAlias = Annotated[Union[ToolFunction, CustomTool], PropertyInfo(discriminator="type")]


class NamespaceTool(BaseModel):
    """Groups function/custom tools under a shared namespace."""

    description: str
    """A description of the namespace shown to the model."""

    name: str
    """The namespace name used in tool calls (for example, `crm`)."""

    tools: List[Tool]
    """The function/custom tools available inside this namespace."""

    type: Literal["namespace"]
    """The type of the tool. Always `namespace`."""
