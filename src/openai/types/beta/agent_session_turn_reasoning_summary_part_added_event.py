# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .summary_text import SummaryText

__all__ = ["AgentSessionTurnReasoningSummaryPartAddedEvent"]


class AgentSessionTurnReasoningSummaryPartAddedEvent(BaseModel):
    """Emitted when a reasoning summary content part is added."""

    event_id: str
    """The unique ID of the event."""

    item_id: str
    """The ID of the reasoning item."""

    output_index: int
    """The index of the item in the turn output."""

    part: SummaryText
    """The initial summary part."""

    session_id: str
    """The ID of the session associated with the event."""

    summary_index: int
    """The index of the summary content part."""

    turn_id: Optional[str] = None
    """The ID of the turn associated with the event, when applicable."""

    type: Literal["agent.session.turn.reasoning_summary_part.added"]
    """The type of the object.

    Always `agent.session.turn.reasoning_summary_part.added`.
    """
