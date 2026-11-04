# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel
from .agent_session import AgentSession

__all__ = ["AgentSessionIdleEvent"]


class AgentSessionIdleEvent(BaseModel):
    """Emitted when a session becomes idle."""

    event_id: str
    """The unique ID of the event."""

    session: AgentSession
    """The session that became idle."""

    type: Literal["agent.session.idle"]
    """The type of the object. Always `agent.session.idle`."""
