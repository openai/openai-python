# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["BetaResponseInjectCreatedEvent"]


class BetaResponseInjectCreatedEvent(BaseModel):
    """
    Emitted when all injected input items were validated and committed to the
    active response.
    """

    response_id: str
    """The ID of the response that accepted the input."""

    sequence_number: int
    """The sequence number for this event."""

    type: Literal["response.inject.created"]
    """The event discriminator. Always `response.inject.created`."""

    stream_id: Optional[str] = None
    """The multiplexed WebSocket stream that emitted the event.

    This field is present only when WebSocket multiplexing is enabled separately.
    """
