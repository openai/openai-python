# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseReasoningSummaryDeltaEvent"]


class ResponseReasoningSummaryDeltaEvent(BaseModel):
    delta: object
    """The partial update to the reasoning summary content."""

    item_id: str
    """
    The unique identifier of the item for which the reasoning summary is being
    updated.
    """

    output_index: int
    """The index of the output item in the response's output array."""

    sequence_number: int
    """The sequence number of this event."""

    summary_index: int
    """The index of the summary part within the output item."""

    type: Literal["response.reasoning_summary.delta"]
    """The type of the event. Always 'response.reasoning_summary.delta'."""
