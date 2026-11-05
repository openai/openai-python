# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from ..._models import BaseModel
from .data_channel_config import DataChannelConfig

__all__ = ["ClientConfig"]


class ClientConfig(BaseModel):
    """
    Startup-only capabilities for an untrusted frontend attached to a unified WebRTC session. Trusted sideband connections are unaffected.
    """

    data_channel: DataChannelConfig
    """Client and server event permissions for the WebRTC frontend data channel."""
