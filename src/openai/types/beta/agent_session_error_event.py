# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel
from .session_error import SessionError

__all__ = ["AgentSessionErrorEvent"]


class AgentSessionErrorEvent(BaseModel):
    """Emitted when a turn or session fails."""

    error: SessionError
    """The error that occurred."""

    event_id: str
    """The unique ID of the event."""

    session_id: str
    """The ID of the session associated with the event."""

    type: Literal["error"]
    """The type of the object. Always `error`."""
