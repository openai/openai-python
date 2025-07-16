# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["ImageGenCompletedEvent", "Usage", "UsageInputTokensDetails"]


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


class ImageGenCompletedEvent(BaseModel):
    b64_json: str
    """Base64-encoded image data, suitable for rendering as an image."""

    background: Literal["transparent", "opaque", "auto"]
    """The background setting for the generated image."""

    created_at: int
    """The Unix timestamp when the event was created."""

    output_format: Literal["png", "webp", "jpeg"]
    """The output format for the generated image."""

    quality: Literal["low", "medium", "high", "auto"]
    """The quality setting for the generated image."""

    size: Literal["1024x1024", "1024x1536", "1536x1024", "auto"]
    """The size of the generated image."""

    type: Literal["image_generation.completed"]
    """The type of the event. Always `image_generation.completed`."""

    usage: Usage
    """For `gpt-image-1` only, the token usage information for the image generation."""
