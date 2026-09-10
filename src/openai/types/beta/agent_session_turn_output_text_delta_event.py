# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["AgentSessionTurnOutputTextDeltaEvent"]


class AgentSessionTurnOutputTextDeltaEvent(BaseModel):
    """Emitted when text is appended to an output text content part."""

    content_index: int
    """The index of the content part in the message."""

    delta: str
    """The text that was appended."""

    event_id: str
    """The unique ID of the event."""

    item_id: str
    """The ID of the message item."""

    output_index: int
    """The index of the item in the turn output."""

    session_id: str
    """The ID of the session associated with the event."""

    turn_id: Optional[str] = None
    """The ID of the turn associated with the event, when applicable."""

    type: Literal["agent.session.turn.output_text.delta"]
    """The type of the object. Always `agent.session.turn.output_text.delta`."""
