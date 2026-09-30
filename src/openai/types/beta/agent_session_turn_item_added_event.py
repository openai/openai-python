# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .agent_session_item import AgentSessionItem

__all__ = ["AgentSessionTurnItemAddedEvent"]


class AgentSessionTurnItemAddedEvent(BaseModel):
    """Emitted when an item is added to a turn."""

    event_id: str
    """The unique ID of the event."""

    item: AgentSessionItem
    """The item that was added."""

    output_index: Optional[int] = None
    """The index of the item in the turn output, when the item is agent output."""

    session_id: str
    """The ID of the session associated with the event."""

    turn_id: Optional[str] = None
    """The ID of the turn associated with the event, when applicable."""

    type: Literal["agent.session.turn.item.added"]
    """The type of the object. Always `agent.session.turn.item.added`."""
