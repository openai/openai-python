# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel
from .response_output_item import ResponseOutputItem

__all__ = ["ResponseOutputItemAddedEvent"]


class ResponseOutputItemAddedEvent(BaseModel):
    """Emitted when a new output item is added."""

    item: ResponseOutputItem
    """The output item that was added.

    For reasoning items, `encrypted_content` may be incomplete while the item is in
    progress. Use the reasoning item from the corresponding
    `response.output_item.done` event when passing it as input to a subsequent
    request.
    """

    output_index: int
    """The index of the output item that was added."""

    sequence_number: int
    """The sequence number of this event."""

    type: Literal["response.output_item.added"]
    """The type of the event. Always `response.output_item.added`."""
