# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .agent_session_environment_state import AgentSessionEnvironmentState

__all__ = ["AgentSessionEnvironmentReadyEvent"]


class AgentSessionEnvironmentReadyEvent(BaseModel):
    """Emitted when a hosted session environment is ready to connect."""

    environment: AgentSessionEnvironmentState
    """The current environment state."""

    event_id: str
    """The unique ID of the event."""

    session_id: str
    """The ID of the session associated with the event."""

    turn_id: Optional[str] = None
    """The ID of the turn associated with the event, when applicable."""

    type: Literal["agent.session.environment.ready"]
    """The type of the object. Always `agent.session.environment.ready`."""
