# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseReasoningDoneEvent"]


class ResponseReasoningDoneEvent(BaseModel):
    content_index: int
    """The index of the reasoning content part within the output item."""

    item_id: str
    """The unique identifier of the item for which reasoning is finalized."""

    output_index: int
    """The index of the output item in the response's output array."""

    sequence_number: int
    """The sequence number of this event."""

    text: str
    """The finalized reasoning text."""

    type: Literal["response.reasoning.done"]
    """The type of the event. Always 'response.reasoning.done'."""
