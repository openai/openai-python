# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["AgentSessionEnvironmentResetEvent"]


class AgentSessionEnvironmentResetEvent(BaseModel):
    """Emitted after a hosted sandbox is replaced.

    Conversation history survives; changes to the previous sandbox's files and processes do not.
    """

    environment_id: str
    """The stable environment ID, retained across sandbox replacements."""

    event_id: str
    """The unique ID of the event."""

    reset_count: int
    """Monotonically increasing reset number.

    Repeated notifications share this number.
    """

    session_id: str
    """The ID of the session associated with the event."""

    turn_id: Optional[str] = None
    """The associated turn, when applicable."""

    type: Literal["agent.session.environment.reset"]
    """The type of the object. Always `agent.session.environment.reset`."""
