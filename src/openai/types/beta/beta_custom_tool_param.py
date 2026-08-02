# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = ["BetaCustomToolParam", "Format", "FormatText", "FormatGrammar"]


class FormatText(TypedDict, total=False):
    """Unconstrained free-form text."""

    type: Required[Literal["text"]]
    """Unconstrained text format. Always `text`."""


class FormatGrammar(TypedDict, total=False):
    """A grammar defined by the user."""

    definition: Required[str]
    """The grammar definition."""

    syntax: Required[Literal["lark", "regex"]]
    """The syntax of the grammar definition. One of `lark` or `regex`."""

    type: Required[Literal["grammar"]]
    """Grammar format. Always `grammar`."""


Format: TypeAlias = Union[FormatText, FormatGrammar]


class BetaCustomToolParam(TypedDict, total=False):
    """A custom tool that processes input using a specified format.

    Learn more about   [custom tools](https://platform.openai.com/docs/guides/function-calling#custom-tools)
    """

    name: Required[str]
    """The name of the custom tool, used to identify it in tool calls."""

    type: Required[Literal["custom"]]
    """The type of the custom tool. Always `custom`."""

    allowed_callers: Optional[List[Literal["direct", "programmatic"]]]
    """The tool invocation context(s)."""

    defer_loading: bool
    """Whether this tool should be deferred and discovered via tool search."""

    description: str
    """Optional description of the custom tool, used to provide more context."""

    format: Format
    """The input format for the custom tool. Default is unconstrained text."""
