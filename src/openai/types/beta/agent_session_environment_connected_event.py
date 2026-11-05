# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .agent_session_environment_state import AgentSessionEnvironmentState

__all__ = ["AgentSessionEnvironmentConnectedEvent"]


class AgentSessionEnvironmentConnectedEvent(BaseModel):
    """Emitted when a session environment connects."""

    environment: AgentSessionEnvironmentState
    """The current environment state."""

    event_id: str
    """The unique ID of the event."""

    session_id: str
    """The ID of the session associated with the event."""

    turn_id: Optional[str] = None
    """The ID of the turn associated with the event, when applicable."""

    type: Literal["agent.session.environment.connected"]
    """The type of the object. Always `agent.session.environment.connected`."""
