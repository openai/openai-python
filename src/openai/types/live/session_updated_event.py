# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .session_resource import SessionResource

__all__ = ["SessionUpdatedEvent"]


class SessionUpdatedEvent(BaseModel):
    """Returned when a Live session update is accepted.

    Contains the resolved session configuration after the update.
    """

    event_id: str
    """The unique ID of the Live server event."""

    session: SessionResource
    """The resolved Live session configuration and server-assigned session metadata."""

    type: Literal["session.updated"]
    """The event type, always `session.updated`."""

    client_event_id: Optional[str] = None
    """
    The event_id of the client command associated with this server event, when
    supplied.
    """
