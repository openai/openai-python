# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .agent_output_item import AgentOutputItem

__all__ = ["AgentSessionTurnItemDoneEvent"]


class AgentSessionTurnItemDoneEvent(BaseModel):
    """Emitted when an output item is complete."""

    event_id: str
    """The unique ID of the event."""

    item: AgentOutputItem
    """The completed output item."""

    output_index: int
    """The index of the output item in the turn output."""

    session_id: str
    """The ID of the session associated with the event."""

    turn_id: Optional[str] = None
    """The ID of the turn associated with the event, when applicable."""

    type: Literal["agent.session.turn.item.done"]
    """The type of the object. Always `agent.session.turn.item.done`."""
