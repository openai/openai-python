# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from .media_session_config_param import MediaSessionConfigParam

__all__ = ["LiveCreateParams", "Transport"]


class LiveCreateParams(TypedDict, total=False):
    session: Required[MediaSessionConfigParam]
    """Startup configuration for the Live session."""

    transport: Required[Transport]
    """WebRTC transport with the browser's SDP offer."""


class Transport(TypedDict, total=False):
    """WebRTC transport with the browser's SDP offer."""

    sdp: Required[str]
    """Session Description Protocol message for the WebRTC connection."""

    type: Required[Literal["webrtc"]]
    """The transport used for the Live session. Always `webrtc`."""
