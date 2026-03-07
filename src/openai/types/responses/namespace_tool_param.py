# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .custom_tool_param import CustomToolParam

__all__ = ["NamespaceToolParam", "Tool", "ToolFunction"]


class ToolFunction(TypedDict, total=False):
    name: Required[str]

    type: Required[Literal["function"]]

    description: Optional[str]

    parameters: Optional[object]

    strict: Optional[bool]


Tool: TypeAlias = Union[ToolFunction, CustomToolParam]


class NamespaceToolParam(TypedDict, total=False):
    """Groups function/custom tools under a shared namespace."""

    description: Required[str]
    """A description of the namespace shown to the model."""

    name: Required[str]
    """The namespace name used in tool calls (for example, `crm`)."""

    tools: Required[Iterable[Tool]]
    """The function/custom tools available inside this namespace."""

    type: Required[Literal["namespace"]]
    """The type of the tool. Always `namespace`."""
