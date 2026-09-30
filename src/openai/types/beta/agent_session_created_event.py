# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel
from .agent_session import AgentSession

__all__ = ["AgentSessionCreatedEvent"]


class AgentSessionCreatedEvent(BaseModel):
    """Emitted when a session is created."""

    event_id: str
    """The unique ID of the event."""

    session: AgentSession
    """The session that was created."""

    type: Literal["agent.session.created"]
    """The type of the object. Always `agent.session.created`."""
