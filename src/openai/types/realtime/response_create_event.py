# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .realtime_response_create_params import RealtimeResponseCreateParams

__all__ = ["ResponseCreateEvent"]


class ResponseCreateEvent(BaseModel):
    type: Literal["response.create"]
    """The event type, must be `response.create`."""

    event_id: Optional[str] = None
    """Optional client-generated ID used to identify this event."""

    response: Optional[RealtimeResponseCreateParams] = None
    """Create a new Realtime response with these parameters"""
