# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel
from .agent_session import AgentSession

__all__ = ["AgentSessionInProgressEvent"]


class AgentSessionInProgressEvent(BaseModel):
    """Emitted when a session starts processing a turn."""

    event_id: str
    """The unique ID of the event."""

    session: AgentSession
    """The session that started processing."""

    type: Literal["agent.session.in_progress"]
    """The type of the object. Always `agent.session.in_progress`."""
