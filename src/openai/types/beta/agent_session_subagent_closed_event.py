# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .subagent import Subagent
from ..._models import BaseModel

__all__ = ["AgentSessionSubagentClosedEvent"]


class AgentSessionSubagentClosedEvent(BaseModel):
    """Emitted when a subagent is closed."""

    event_id: str
    """The unique ID of the event."""

    subagent: Subagent
    """The subagent that was closed."""

    type: Literal["agent.session.subagent.closed"]
    """The type of the object. Always `agent.session.subagent.closed`."""
