# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .output_text import OutputText

__all__ = ["AgentSessionTurnContentPartAddedEvent"]


class AgentSessionTurnContentPartAddedEvent(BaseModel):
    """Emitted when an output text content part is added."""

    content_index: int
    """The index of the content part in the message."""

    event_id: str
    """The unique ID of the event."""

    item_id: str
    """The ID of the message item."""

    output_index: int
    """The index of the item in the turn output."""

    part: OutputText
    """The initial content part."""

    session_id: str
    """The ID of the session associated with the event."""

    turn_id: Optional[str] = None
    """The ID of the turn associated with the event, when applicable."""

    type: Literal["agent.session.turn.content_part.added"]
    """The type of the object. Always `agent.session.turn.content_part.added`."""
