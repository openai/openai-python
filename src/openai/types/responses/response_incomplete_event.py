# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .response import Response
from ..._models import BaseModel

__all__ = ["ResponseIncompleteEvent"]


class ResponseIncompleteEvent(BaseModel):
    """An event that is emitted when a response finishes as incomplete.

    Over WebSocket, steering can finish a response with
    `response.incomplete_details.reason` set to `steered`, followed automatically
    by a successor `response.created` that commits the queued steering input.
    """

    response: Response
    """The response that was incomplete."""

    sequence_number: int
    """The sequence number of this event."""

    type: Literal["response.incomplete"]
    """The type of the event. Always `response.incomplete`."""
