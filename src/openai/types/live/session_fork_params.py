# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from .media_session_fork_config_param import MediaSessionForkConfigParam

__all__ = ["SessionForkParams", "Transport"]


class SessionForkParams(TypedDict, total=False):
    transport: Required[Transport]
    """
    WebRTC transport with an SDP offer for the new connection to the forked session.
    """

    session: MediaSessionForkConfigParam
    """Optional configuration overrides for the new Live session.

    Omit this object or send an empty object to inherit the stored session's
    settings.
    """


class Transport(TypedDict, total=False):
    """
    WebRTC transport with an SDP offer for the new connection to the forked session.
    """

    sdp: Required[str]
    """Session Description Protocol message for the WebRTC connection."""

    type: Required[Literal["webrtc"]]
    """The transport used for the Live session. Always `webrtc`."""
