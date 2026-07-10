# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["ResponseInputImageParam", "PromptCacheBreakpoint"]


class PromptCacheBreakpoint(TypedDict, total=False):
    """Marks the exact end of a reusable prompt prefix.

    The breakpoint inherits its TTL from the request's `prompt_cache_options.ttl`; the boundary is not rounded to a token block.
    """

    mode: Required[Literal["explicit"]]
    """The breakpoint mode. Always `explicit`."""


class ResponseInputImageParam(TypedDict, total=False):
    """An image input to the model.

    Learn about [image inputs](https://platform.openai.com/docs/guides/vision).
    """

    detail: Required[Literal["low", "high", "auto", "original"]]
    """The detail level of the image to be sent to the model.

    One of `high`, `low`, `auto`, or `original`. Defaults to `auto`.
    """

    type: Required[Literal["input_image"]]
    """The type of the input item. Always `input_image`."""

    file_id: Optional[str]
    """The ID of the file to be sent to the model."""

    image_url: Optional[str]
    """The URL of the image to be sent to the model.

    A fully qualified URL or base64 encoded image in a data URL.
    """

    prompt_cache_breakpoint: PromptCacheBreakpoint
    """Marks the exact end of a reusable prompt prefix.

    The breakpoint inherits its TTL from the request's `prompt_cache_options.ttl`;
    the boundary is not rounded to a token block.
    """
