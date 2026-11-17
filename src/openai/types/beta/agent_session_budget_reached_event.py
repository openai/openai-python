# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .agent_session import AgentSession

__all__ = ["AgentSessionBudgetReachedEvent"]


class AgentSessionBudgetReachedEvent(BaseModel):
    """Emitted when a session pauses because its spending limit was reached."""

    event_id: str
    """The unique ID of the event."""

    session: AgentSession
    """The paused session."""

    type: Literal["agent.session.budget_reached"]
    """The type of the object. Always `agent.session.budget_reached`."""

    obfuscation: Optional[str] = None
    """Random alphanumeric padding. Present when stream obfuscation is enabled."""
