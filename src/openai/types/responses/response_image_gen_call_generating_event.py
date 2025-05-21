# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseImageGenCallGeneratingEvent"]


class ResponseImageGenCallGeneratingEvent(BaseModel):
    item_id: str
    """The unique identifier of the image generation item being processed."""

    output_index: int
    """The index of the output item in the response's output array."""

    type: Literal["response.image_generation_call.generating"]
    """The type of the event. Always 'response.image_generation_call.generating'."""

    sequence_number: Optional[int] = None
    """The sequence number of the image generation item being processed."""
