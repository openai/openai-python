# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .beta_custom_tool_param import BetaCustomToolParam

__all__ = ["BetaNamespaceToolParam", "Tool", "ToolFunction"]


class ToolFunction(TypedDict, total=False):
    name: Required[str]

    type: Required[Literal["function"]]

    allowed_callers: Optional[List[Literal["direct", "programmatic"]]]
    """The tool invocation context(s)."""

    defer_loading: bool
    """Whether this function should be deferred and discovered via tool search."""

    description: Optional[str]

    output_schema: Optional[Dict[str, object]]
    """
    A JSON Schema describing the JSON value encoded in string outputs for this
    function tool. This does not describe content-array outputs.
    """

    parameters: Optional[object]

    strict: Optional[bool]
    """Whether to enforce strict parameter validation.

    If omitted, Responses attempts to use strict validation when the schema is
    compatible, and falls back to non-strict validation otherwise.
    """


Tool: TypeAlias = Union[ToolFunction, BetaCustomToolParam]


class BetaNamespaceToolParam(TypedDict, total=False):
    """Groups function/custom tools under a shared namespace."""

    description: Required[str]
    """A description of the namespace shown to the model."""

    name: Required[str]
    """The namespace name used in tool calls (for example, `crm`)."""

    tools: Required[Iterable[Tool]]
    """The function/custom tools available inside this namespace."""

    type: Required[Literal["namespace"]]
    """The type of the tool. Always `namespace`."""
