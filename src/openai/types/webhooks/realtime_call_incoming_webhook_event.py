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

    The same value appears as `session_id` in `live.call.incoming`.
    """

    sip_headers: List[DataSipHeader]
    """Headers from the SIP Invite."""


class RealtimeCallIncomingWebhookEvent(BaseModel):
    """
    Sent when an incoming API SIP session is available for Realtime acceptance.
    The same pending session can also emit `live.call.incoming`; the first
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
