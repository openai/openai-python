# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ComputerScreenshotContent", "PromptCacheBreakpoint"]


class PromptCacheBreakpoint(BaseModel):
    """Marks the exact end of a reusable prompt prefix.

    The breakpoint inherits its TTL from the request's `prompt_cache_options.ttl`; the boundary is not rounded to a token block.
    """

    mode: Literal["explicit"]
    """The breakpoint mode. Always `explicit`."""


class ComputerScreenshotContent(BaseModel):
    """A screenshot of a computer."""

    detail: Literal["low", "high", "auto", "original"]
    """The detail level of the screenshot image to be sent to the model.

    One of `high`, `low`, `auto`, or `original`. Defaults to `auto`.
    """

    file_id: Optional[str] = None
    """The identifier of an uploaded file that contains the screenshot."""

    image_url: Optional[str] = None
    """The URL of the screenshot image."""

    type: Literal["computer_screenshot"]
    """Specifies the event type.

    For a computer screenshot, this property is always set to `computer_screenshot`.
    """

    prompt_cache_breakpoint: Optional[PromptCacheBreakpoint] = None
    """Marks the exact end of a reusable prompt prefix.

    The breakpoint inherits its TTL from the request's `prompt_cache_options.ttl`;
    the boundary is not rounded to a token block.
    """
