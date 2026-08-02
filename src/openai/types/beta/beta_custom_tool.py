# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel

__all__ = ["BetaCustomTool", "Format", "FormatText", "FormatGrammar"]


class FormatText(BaseModel):
    """Unconstrained free-form text."""

    type: Literal["text"]
    """Unconstrained text format. Always `text`."""


class FormatGrammar(BaseModel):
    """A grammar defined by the user."""

    definition: str
    """The grammar definition."""

    syntax: Literal["lark", "regex"]
    """The syntax of the grammar definition. One of `lark` or `regex`."""

    type: Literal["grammar"]
    """Grammar format. Always `grammar`."""


Format: TypeAlias = Annotated[Union[FormatText, FormatGrammar], PropertyInfo(discriminator="type")]


class BetaCustomTool(BaseModel):
    """A custom tool that processes input using a specified format.

    Learn more about   [custom tools](https://platform.openai.com/docs/guides/function-calling#custom-tools)
    """

    name: str
    """The name of the custom tool, used to identify it in tool calls."""

    type: Literal["custom"]
    """The type of the custom tool. Always `custom`."""

    allowed_callers: Optional[List[Literal["direct", "programmatic"]]] = None
    """The tool invocation context(s)."""

    defer_loading: Optional[bool] = None
    """Whether this tool should be deferred and discovered via tool search."""

    description: Optional[str] = None
    """Optional description of the custom tool, used to provide more context."""

    format: Optional[Format] = None
    """The input format for the custom tool. Default is unconstrained text."""
