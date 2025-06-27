# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseReasoningDeltaEvent"]


class ResponseReasoningDeltaEvent(BaseModel):
    content_index: int
    """The index of the reasoning content part within the output item."""

    delta: object
    """The partial update to the reasoning content."""

    item_id: str
    """The unique identifier of the item for which reasoning is being updated."""

    output_index: int
    """The index of the output item in the response's output array."""

    sequence_number: int
    """The sequence number of this event."""

    type: Literal["response.reasoning.delta"]
    """The type of the event. Always 'response.reasoning.delta'."""
