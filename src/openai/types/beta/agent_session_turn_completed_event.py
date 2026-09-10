# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .token_usage import TokenUsage
from .agents.sessions.turn import Turn

__all__ = ["AgentSessionTurnCompletedEvent"]


class AgentSessionTurnCompletedEvent(BaseModel):
    """Emitted when a turn completes."""

    event_id: str
    """The unique ID of the event."""

    session_id: str
    """The ID of the session associated with the event."""

    turn: Turn
    """The completed turn."""

    turn_id: str
    """The ID of the turn associated with the event."""

    type: Literal["agent.session.turn.completed"]
    """The type of the object. Always `agent.session.turn.completed`."""

    usage: Optional[TokenUsage] = None
    """Recorded token usage for a session or turn.

    Usage is best effort and may change.
    """
