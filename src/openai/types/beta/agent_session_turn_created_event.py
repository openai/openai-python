# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel
from .agents.sessions.turn import Turn

__all__ = ["AgentSessionTurnCreatedEvent"]


class AgentSessionTurnCreatedEvent(BaseModel):
    """Emitted when a turn is created."""

    event_id: str
    """The unique ID of the event."""

    session_id: str
    """The ID of the session associated with the event."""

    turn: Turn
    """The turn at the time it was created."""

    turn_id: str
    """The ID of the turn associated with the event."""

    type: Literal["agent.session.turn.created"]
    """The type of the object. Always `agent.session.turn.created`."""
