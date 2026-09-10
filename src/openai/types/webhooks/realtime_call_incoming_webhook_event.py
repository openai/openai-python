# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["RealtimeCallIncomingWebhookEvent", "Data", "DataSipHeader"]


class DataSipHeader(BaseModel):
    """A header from the SIP Invite."""

    name: str
    """Name of the SIP Header."""

    value: str
    """Value of the SIP Header."""


class Data(BaseModel):
    """Event data payload."""

    call_id: str
    """The Transceiver `rtc_...` ID of the pending SIP session.

    The paired `live.transport.incoming` event derives its `session_id` by replacing
    the `rtc_` prefix with `live_`. Use the ID returned by the event with the
    corresponding Realtime or Live API.
    """

    sip_headers: List[DataSipHeader]
    """
    Headers from the SIP INVITE, excluding SIP authorization headers. Retained
    names, values, repeated entries, and order are preserved. Treat these values as
    untrusted call metadata.
    """


class RealtimeCallIncomingWebhookEvent(BaseModel):
    """
    Sent when an incoming API SIP session is available for Realtime acceptance.
    The same pending session can also emit `live.transport.incoming`; the first
    successful Realtime or Live accept endpoint selects the runtime surface.
    """

    id: str
    """The unique ID of the event."""

    created_at: int
    """The Unix timestamp (in seconds) of when the model response was completed."""

    data: Data
    """Event data payload."""

    type: Literal["realtime.call.incoming"]
    """The type of the event. Always `realtime.call.incoming`."""

    object: Optional[Literal["event"]] = None
    """The object of the event. Always `event`."""
