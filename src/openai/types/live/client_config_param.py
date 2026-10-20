# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .data_channel_config_param import DataChannelConfigParam

__all__ = ["ClientConfigParam"]


class ClientConfigParam(TypedDict, total=False):
    """
    Startup-only capabilities for an untrusted frontend attached to a unified WebRTC session. Trusted sideband connections are unaffected.
    """

    data_channel: Required[DataChannelConfigParam]
    """Client and server event permissions for the WebRTC frontend data channel."""
