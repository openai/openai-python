# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseInputImageContent", "PromptCacheBreakpoint"]


class PromptCacheBreakpoint(BaseModel):
    """Marks the exact end of a reusable prompt prefix.

    The breakpoint inherits its TTL from the request's `prompt_cache_options.ttl`; the boundary is not rounded to a token block.
    """

    mode: Literal["explicit"]
    """The breakpoint mode. Always `explicit`."""


class ResponseInputImageContent(BaseModel):
    """An image input to the model.

    Learn about [image inputs](https://platform.openai.com/docs/guides/vision)
    """

    type: Literal["input_image"]
    """The type of the input item. Always `input_image`."""

    detail: Optional[Literal["low", "high", "auto", "original"]] = None
    """The detail level of the image to be sent to the model.

    One of `high`, `low`, `auto`, or `original`. Defaults to `auto`.
    """

    file_id: Optional[str] = None
    """The ID of the file to be sent to the model."""

    image_url: Optional[str] = None
    """The URL of the image to be sent to the model.

    A fully qualified URL or base64 encoded image in a data URL.
    """

    prompt_cache_breakpoint: Optional[PromptCacheBreakpoint] = None
    """Marks the exact end of a reusable prompt prefix.

    The breakpoint inherits its TTL from the request's `prompt_cache_options.ttl`;
    the boundary is not rounded to a token block.
    """
