# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .session_usage import SessionUsage
from .session_resource import SessionResource

__all__ = ["SessionClosedEvent"]


class SessionClosedEvent(BaseModel):
    """
    Returned after the Live session finishes finalizing, with the close reason, final session snapshot, and cumulative audio usage. A connection closing without this event does not confirm successful finalization.
    """

    event_id: str
    """The unique ID of the Live server event."""

    reason: Literal["close_requested", "expired", "content", "remote_hangup", "connection_lost"]
    """
    Why the Live session ended: `close_requested` for an application close or hangup
    request, `expired` for the session duration limit, `content` for a safety
    filter, `remote_hangup` for a graceful remote disconnect, or `connection_lost`
    for an unexpected primary or upstream disconnection.
    """

    session: SessionResource
    """The resolved Live session configuration and server-assigned session metadata."""

    type: Literal["session.closed"]
    """The event type, always `session.closed`."""

    usage: SessionUsage
    """The final cumulative Live audio usage after session finalization."""

    client_event_id: Optional[str] = None
    """
    The event_id of the client command associated with this server event, when
    supplied.
    """
