# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel
from .realtime_session import RealtimeSession

__all__ = ["SessionUpdatedEvent"]


class SessionUpdatedEvent(BaseModel):
    event_id: str
    """The unique ID of the server event."""

    session: RealtimeSession
    """Realtime session object."""

    type: Literal["session.updated"]
    """The event type, must be `session.updated`."""
