# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

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
    """The Transceiver `rtc_...` ID of the pending SIP session.

    The same value appears as `call_id` in `realtime.call.incoming`.
    """

    sip_headers: List[DataSipHeader]
    """Headers from the SIP Invite."""


class LiveCallIncomingWebhookEvent(BaseModel):
    """Sent when an incoming API SIP session is available for Live acceptance.

    The
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
