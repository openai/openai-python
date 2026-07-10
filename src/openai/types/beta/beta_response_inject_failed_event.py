# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .beta_response_input_item import BetaResponseInputItem

__all__ = ["BetaResponseInjectFailedEvent", "Error"]


class Error(BaseModel):
    """Information about why the input was not committed."""

    code: Literal["response_already_completed", "response_not_found"]
    """A machine-readable error code."""

    message: str
    """A human-readable description of the error."""


class BetaResponseInjectFailedEvent(BaseModel):
    """Emitted when injected input could not be committed to a response.

    The event
    returns the uncommitted raw input so the client can retry it in another
    response when appropriate.
    """

    error: Error
    """Information about why the input was not committed."""

    input: List[BetaResponseInputItem]
    """The raw input items that were not committed."""

    response_id: str
    """The ID of the response that rejected the input."""

    sequence_number: int
    """The sequence number for this event."""

    type: Literal["response.inject.failed"]
    """The event discriminator. Always `response.inject.failed`."""

    stream_id: Optional[str] = None
    """The multiplexed WebSocket stream that emitted the event.

    This field is present only when WebSocket multiplexing is enabled separately.
    """
