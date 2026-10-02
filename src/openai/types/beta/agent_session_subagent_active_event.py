# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .subagent import Subagent
from ..._models import BaseModel

__all__ = ["AgentSessionSubagentActiveEvent"]


class AgentSessionSubagentActiveEvent(BaseModel):
    """Emitted when a closed subagent successfully resumes."""

    event_id: str
    """The unique ID of the event."""

    subagent: Subagent
    """The subagent that resumed."""

    type: Literal["agent.session.subagent.active"]
    """The type of the object. Always `agent.session.subagent.active`."""
