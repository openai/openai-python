# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["LiveTransportConnectedWebhookEvent", "Data"]


class Data(BaseModel):
    session_id: str
    """The Live session ID to use with the sideband attach endpoint."""

    type: Literal["webrtc"]
    """The session transport."""


class LiveTransportConnectedWebhookEvent(BaseModel):
    """
    Sent when a direct Live WebRTC session is created or an Instant Connect session activates. Use its session ID to attach a sideband observer.
    """

    id: str
    """The webhook event ID."""

    created_at: int
    """Unix time in seconds when the event was created."""

    data: Data

    object: Literal["event"]

    type: Literal["live.transport.connected"]
