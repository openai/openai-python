# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ChatCompletionContentPartImage", "ImageURL", "PromptCacheBreakpoint"]


class ImageURL(BaseModel):
    url: str
    """Either a URL of the image or the base64 encoded image data."""

    detail: Optional[Literal["auto", "low", "high"]] = None
    """Specifies the detail level of the image.

    Learn more in the
    [Vision guide](https://platform.openai.com/docs/guides/vision#low-or-high-fidelity-image-understanding).
    """


class PromptCacheBreakpoint(BaseModel):
    """Marks the exact end of a reusable prompt prefix.

    The breakpoint inherits its TTL from the request's `prompt_cache_options.ttl`; the boundary is not rounded to a token block.
    """

    mode: Literal["explicit"]
    """The breakpoint mode. Always `explicit`."""


class ChatCompletionContentPartImage(BaseModel):
    """Learn about [image inputs](https://platform.openai.com/docs/guides/vision)."""

    image_url: ImageURL

    type: Literal["image_url"]
    """The type of the content part."""

    prompt_cache_breakpoint: Optional[PromptCacheBreakpoint] = None
    """Marks the exact end of a reusable prompt prefix.

    The breakpoint inherits its TTL from the request's `prompt_cache_options.ttl`;
    the boundary is not rounded to a token block.
    """
