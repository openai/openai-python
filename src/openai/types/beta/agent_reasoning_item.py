# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .summary_text import SummaryText
from .agent_output_item_status import AgentOutputItemStatus

__all__ = ["AgentReasoningItem"]


class AgentReasoningItem(BaseModel):
    """A reasoning item produced by the agent."""

    id: str
    """The ID of the reasoning item."""

    status: Optional[AgentOutputItemStatus] = None
    """The status of an agent output item."""

    summary: List[SummaryText]
    """The reasoning summaries produced by the agent."""

    turn_id: str
    """The ID of the turn that contains this item."""

    type: Literal["reasoning"]
    """The item type. Always `reasoning`."""
