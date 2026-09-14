# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, TypedDict

__all__ = ["AgentReasoningParam"]


class AgentReasoningParam(TypedDict, total=False):
    """Reasoning configuration for the agent."""

    effort: Optional[Literal["none", "minimal", "low", "medium", "high", "xhigh", "max"]]
    """The amount of reasoning effort the model should use."""

    summary: Optional[Literal["concise", "detailed", "auto"]]
    """The reasoning summary format requested from the model.

    - `concise` - Returns a concise reasoning summary when supported.
    - `detailed` - Returns a detailed reasoning summary when supported.
    - `auto` - Automatically selects the most detailed summary supported by the
      model.
    """
