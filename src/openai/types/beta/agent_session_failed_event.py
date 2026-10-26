# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel
from .agent_session import AgentSession

__all__ = ["AgentSessionFailedEvent"]


class AgentSessionFailedEvent(BaseModel):
    """Emitted when a session fails."""

    event_id: str
    """The unique ID of the event."""

    session: AgentSession
    """The failed session."""

    type: Literal["agent.session.failed"]
    """The type of the object. Always `agent.session.failed`."""
