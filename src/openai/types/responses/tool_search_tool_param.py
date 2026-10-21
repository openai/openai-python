# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["ToolSearchToolParam"]


class ToolSearchToolParam(TypedDict, total=False):
    """Hosted or BYOT tool search configuration for deferred tools."""

    type: Required[Literal["tool_search"]]
    """The type of the tool. Always `tool_search`."""

    description: Optional[str]
    """Description shown to the model for a client-executed tool search tool."""

    execution: Literal["server", "client"]
    """Whether tool search is executed by the server or by the client."""

    parameters: Optional[object]
    """Parameter schema for a client-executed tool search tool."""
