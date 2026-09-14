# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["SessionCloseEvent"]


class SessionCloseEvent(BaseModel):
    """Request that the Live session close.

    The terminal `session.closed` event contains the close reason and final usage.
    """

    type: Literal["session.close"]
    """The Live client event type. Always `session.close`."""

    event_id: Optional[str] = None
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """
