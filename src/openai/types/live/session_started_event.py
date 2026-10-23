# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .session_resource import SessionResource

__all__ = ["SessionStartedEvent"]


class SessionStartedEvent(BaseModel):
    """Returned when a Live session has started.

    Contains the resolved session configuration, including server defaults.
    """

    event_id: str
    """The unique ID of the Live server event."""

    session: SessionResource
    """The resolved Live session configuration and server-assigned session metadata."""

    type: Literal["session.started"]
    """The event type, always `session.started`."""

    client_event_id: Optional[str] = None
    """
    The event_id of the client command associated with this server event, when
    supplied.
    """
