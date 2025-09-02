# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .realtime_session_create_request import RealtimeSessionCreateRequest

__all__ = ["SessionUpdateEvent"]


class SessionUpdateEvent(BaseModel):
    session: RealtimeSessionCreateRequest
    """Realtime session object configuration."""

    type: Literal["session.update"]
    """The event type, must be `session.update`."""

    event_id: Optional[str] = None
    """Optional client-generated ID used to identify this event."""
