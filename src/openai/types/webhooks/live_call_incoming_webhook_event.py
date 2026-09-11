# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal, deprecated

from ..._models import BaseModel

__all__ = ["LiveCallIncomingWebhookEvent", "Data", "DataSipHeader"]


class DataSipHeader(BaseModel):
    """A header from the SIP Invite."""

    name: str
    """Name of the SIP Header."""

    value: str
    """Value of the SIP Header."""


class Data(BaseModel):
    """Event data payload."""

    session_id: str
    """The `live_...` ID of the pending SIP session.

    Pass this value unchanged to Live call controls and sideband connections. The
    corresponding `realtime.call.incoming` event uses a separate `rtc_...` call ID.
    """

    sip_headers: List[DataSipHeader]
    """
    Headers from the SIP INVITE, excluding SIP authorization headers. Retained
    names, values, repeated entries, and order are preserved. Treat these values as
    untrusted call metadata.
    """


@deprecated("Use LiveTransportIncomingWebhookEvent (live.transport.incoming) instead.", category=None)
class LiveCallIncomingWebhookEvent(BaseModel):
    """Deprecated: use `live.transport.incoming`.

    Retained for existing subscriptions
    during migration; new subscriptions to this event are not allowed.
    Sent when an incoming API SIP session is available for Live acceptance. The
    same pending session can also emit `realtime.call.incoming`; the first
    successful Realtime or Live accept endpoint selects the runtime surface.
    """

    id: str
    """The unique ID of the event."""

    created_at: int
    """The Unix timestamp (in seconds) of when the event was created."""

    data: Data
    """Event data payload."""

    type: Literal["live.call.incoming"]
    """The type of the event. Always `live.call.incoming`."""

    object: Optional[Literal["event"]] = None
    """The object of the event. Always `event`."""
