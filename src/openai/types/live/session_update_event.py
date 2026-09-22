# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .session_update_config import SessionUpdateConfig

__all__ = ["SessionUpdateEvent"]


class SessionUpdateEvent(BaseModel):
    """Update the delegation settings of an active Live session.

    The server acknowledges accepted changes with `session.updated`.
    """

    session: SessionUpdateConfig
    """Sparse delegation updates.

    Omitted settings retain their values. The delegation type cannot change,
    including resetting Responses delegation to null or client. Model, frontend
    instructions, audio, and startup input are immutable.
    """

    type: Literal["session.update"]
    """The Live client event type. Always `session.update`."""

    event_id: Optional[str] = None
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """
