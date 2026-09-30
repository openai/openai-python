# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .subagent import Subagent
from ..._models import BaseModel

__all__ = ["AgentSessionSubagentCreatedEvent"]


class AgentSessionSubagentCreatedEvent(BaseModel):
    """Emitted when a subagent is created."""

    event_id: str
    """The unique ID of the event."""

    subagent: Subagent
    """The subagent that was created."""

    type: Literal["agent.session.subagent.created"]
    """The type of the object. Always `agent.session.subagent.created`."""
