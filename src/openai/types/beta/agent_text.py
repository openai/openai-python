# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel
from .text_format import TextFormat

__all__ = ["AgentText"]


class AgentText(BaseModel):
    """The text configuration used by an agent."""

    format: TextFormat
    """The effective output format. Defaults to ordinary text."""

    verbosity: Literal["low", "medium", "high"]
    """The amount of text produced by the agent. Defaults to `medium`."""
