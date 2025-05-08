# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .image import Image
from .._models import BaseModel

__all__ = ["ImagesResponse", "Usage", "UsageInputTokensDetails"]


class UsageInputTokensDetails(BaseModel):
    image_tokens: int
    """The number of image tokens in the input prompt."""

    text_tokens: int
    """The number of text tokens in the input prompt."""


class Usage(BaseModel):
    input_tokens: int
    """The number of tokens (images and text) in the input prompt."""

    input_tokens_details: UsageInputTokensDetails
    """The input tokens detailed information for the image generation."""

    output_tokens: int
    """The number of image tokens in the output image."""

    total_tokens: int
    """The total number of tokens (images and text) used for the image generation."""


class ImagesResponse(BaseModel):
    created: int
    """The Unix timestamp (in seconds) of when the image was created."""

    data: Optional[List[Image]] = None
    """The list of generated images."""

    usage: Optional[Usage] = None
    """For `gpt-image-1` only, the token usage information for the image generation."""
