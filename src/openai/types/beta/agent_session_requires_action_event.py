# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel
from .agent_session import AgentSession

__all__ = ["AgentSessionRequiresActionEvent"]


class AgentSessionRequiresActionEvent(BaseModel):
    """Emitted when a session is waiting for one or more required actions."""

    event_id: str
    """The unique ID of the event."""

    session: AgentSession
    """The session and its current required actions."""

    type: Literal["agent.session.requires_action"]
    """The type of the object. Always `agent.session.requires_action`."""
