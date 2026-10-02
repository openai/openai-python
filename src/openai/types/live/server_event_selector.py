# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["ServerEventSelector"]


class ServerEventSelector(BaseModel):
    """A Live server event selector for the WebRTC frontend data channel."""

    type: str
    """The outer Live server event type. Use 'response.event' for Responses events."""

    response_event: Optional[str] = None
    """The nested Responses event type.

    Required when type is 'response.event'; forbidden for other event types.
    """
