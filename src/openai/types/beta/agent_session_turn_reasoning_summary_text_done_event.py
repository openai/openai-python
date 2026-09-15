# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["AgentSessionTurnReasoningSummaryTextDoneEvent"]


class AgentSessionTurnReasoningSummaryTextDoneEvent(BaseModel):
    """Emitted when a reasoning summary content part is complete."""

    event_id: str
    """The unique ID of the event."""

    item_id: str
    """The ID of the reasoning item."""

    output_index: int
    """The index of the item in the turn output."""

    session_id: str
    """The ID of the session associated with the event."""

    summary_index: int
    """The index of the summary content part."""

    text: str
    """The complete reasoning summary text."""

    turn_id: Optional[str] = None
    """The ID of the turn associated with the event, when applicable."""

    type: Literal["agent.session.turn.reasoning_summary_text.done"]
    """The type of the object.

    Always `agent.session.turn.reasoning_summary_text.done`.
    """
