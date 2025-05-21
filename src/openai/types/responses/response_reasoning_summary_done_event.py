# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseReasoningSummaryDoneEvent"]


class ResponseReasoningSummaryDoneEvent(BaseModel):
    item_id: str
    """The unique identifier of the item for which the reasoning summary is finalized."""

    output_index: int
    """The index of the output item in the response's output array."""

    summary_index: int
    """The index of the summary part within the output item."""

    text: str
    """The finalized reasoning summary text."""

    type: Literal["response.reasoning_summary.done"]
    """The type of the event. Always 'response.reasoning_summary.done'."""
