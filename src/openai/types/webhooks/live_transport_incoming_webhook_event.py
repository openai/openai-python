# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["LiveTransportIncomingWebhookEvent", "Data", "DataSipHeader"]


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

    Forward this value unchanged when accepting or rejecting the call through the
    Live API.
    """

    sip_headers: List[DataSipHeader]
    """
    Headers from the SIP INVITE, excluding SIP authorization headers. Retained
    names, values, repeated entries, and order are preserved. Treat these values as
    untrusted call metadata.
    """

    type: Literal["sip"]
    """The incoming transport type. Always `sip`."""

    sip_media_security: Union[Literal["rtp", "srtp"], str, None] = None
    """Media protection selected on the SIP leg during SDP negotiation.

    `srtp` indicates SRTP; `rtp` indicates unencrypted RTP. Omitted when unknown.
    This does not describe SIP signaling security or confirm that media has flowed.
    Clients should handle unrecognized values as unknown.
    """


class LiveTransportIncomingWebhookEvent(BaseModel):
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

    type: Literal["live.transport.incoming"]
    """The type of the event. Always `live.transport.incoming`."""

    object: Optional[Literal["event"]] = None
    """The object of the event. Always `event`."""
