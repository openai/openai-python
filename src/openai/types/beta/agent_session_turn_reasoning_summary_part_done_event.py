# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .summary_text import SummaryText

__all__ = ["AgentSessionTurnReasoningSummaryPartDoneEvent"]


class AgentSessionTurnReasoningSummaryPartDoneEvent(BaseModel):
    """Emitted when a reasoning summary part is complete."""

    event_id: str
    """The unique ID of the event."""

    item_id: str
    """The ID of the reasoning item."""

    output_index: int
    """The index of the item in the turn output."""

    part: SummaryText
    """The completed summary part."""

    session_id: str
    """The ID of the session associated with the event."""

    status: Optional[Literal["incomplete"]] = None
    """Present as `incomplete` when summary generation was interrupted."""

    summary_index: int
    """The index of the summary part."""

    turn_id: Optional[str] = None
    """The ID of the turn associated with the event, when applicable."""

    type: Literal["agent.session.turn.reasoning_summary_part.done"]
    """The type of the object.

    Always `agent.session.turn.reasoning_summary_part.done`.
    """
