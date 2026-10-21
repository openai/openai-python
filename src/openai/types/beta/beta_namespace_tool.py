# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .beta_custom_tool import BetaCustomTool

__all__ = ["BetaNamespaceTool", "Tool", "ToolFunction"]


class ToolFunction(BaseModel):
    name: str

    type: Literal["function"]

    allowed_callers: Optional[List[Literal["direct", "programmatic"]]] = None
    """The tool invocation context(s)."""

    defer_loading: Optional[bool] = None
    """Whether this function should be deferred and discovered via tool search."""

    description: Optional[str] = None

    output_schema: Optional[Dict[str, object]] = None
    """
    A JSON Schema describing the JSON value encoded in string outputs for this
    function tool. This does not describe content-array outputs.
    """

    parameters: Optional[object] = None

    strict: Optional[bool] = None
    """Whether to enforce strict parameter validation.

    If omitted, Responses attempts to use strict validation when the schema is
    compatible, and falls back to non-strict validation otherwise.
    """


Tool: TypeAlias = Annotated[Union[ToolFunction, BetaCustomTool], PropertyInfo(discriminator="type")]


class BetaNamespaceTool(BaseModel):
    """Groups function/custom tools under a shared namespace."""

    description: str
    """A description of the namespace shown to the model."""

    name: str
    """The namespace name used in tool calls (for example, `crm`)."""

    tools: List[Tool]
    """The function/custom tools available inside this namespace."""

    type: Literal["namespace"]
    """The type of the tool. Always `namespace`."""
