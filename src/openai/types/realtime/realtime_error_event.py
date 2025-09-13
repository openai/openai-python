# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel
from .realtime_error import RealtimeError

__all__ = ["RealtimeErrorEvent"]


class RealtimeErrorEvent(BaseModel):
    error: RealtimeError
    """Details of the error."""

    event_id: str
    """The unique ID of the server event."""

    type: Literal["error"]
    """The event type, must be `error`."""
