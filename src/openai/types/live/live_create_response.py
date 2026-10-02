# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["LiveCreateResponse", "Session", "Transport"]


class Session(BaseModel):
    """The newly created Live session.

    Use its ID for session controls and sideband connections.
    """

    id: str
    """Opaque session identifier.

    Preserve the returned value unchanged, including its prefix.
    """


class Transport(BaseModel):
    """WebRTC transport with the SDP answer."""

    sdp: str
    """Session Description Protocol message for the WebRTC connection."""

    type: Literal["webrtc"]
    """The transport used for the Live session. Always `webrtc`."""


class LiveCreateResponse(BaseModel):
    """The created Live session identifier and WebRTC answer.

    Apply transport.sdp as the peer's remote answer and wait for session.started on the data channel before sending commands.
    """

    session: Session
    """The newly created Live session.

    Use its ID for session controls and sideband connections.
    """

    transport: Transport
    """WebRTC transport with the SDP answer."""
