# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["AgentReasoning"]


class AgentReasoning(BaseModel):
    """The reasoning configuration used by an agent."""

    effort: Optional[Literal["none", "minimal", "low", "medium", "high", "xhigh", "max"]] = None
    """
    The requested reasoning effort, or `null` when the model selects its own
    default.
    """

    summary: Optional[Literal["concise", "detailed", "auto"]] = None
    """The requested reasoning summary format, or `null` when summaries are disabled.

    - `concise` - Returns a concise reasoning summary when supported.
    - `detailed` - Returns a detailed reasoning summary when supported.
    - `auto` - Automatically selects the most detailed summary supported by the
      model.
    """
