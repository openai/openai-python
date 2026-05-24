# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ToolSearchTool"]


class ToolSearchTool(BaseModel):
    """Hosted or BYOT tool search configuration for deferred tools."""

    type: Literal["tool_search"]
    """The type of the tool. Always `tool_search`."""

    description: Optional[str] = None
    """Description shown to the model for a client-executed tool search tool."""

    execution: Optional[Literal["server", "client"]] = None
    """Whether tool search is executed by the server or by the client."""

    parameters: Optional[object] = None
    """Parameter schema for a client-executed tool search tool."""
