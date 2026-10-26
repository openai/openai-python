# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

from .decision_prompt_cache_breakpoint_param import DecisionPromptCacheBreakpointParam

__all__ = ["DecisionInputImageParam", "PromptCacheBreakpoint"]


class PromptCacheBreakpoint(TypedDict, total=False):
    """Marks the exact end of a reusable prompt prefix."""

    mode: Required[Literal["explicit"]]
    """The prompt cache mode."""


class DecisionInputImageParam(TypedDict, total=False):
    """An image provided as a base64 data URL or a publicly accessible HTTP(S) URL.

    File IDs are not supported.
    """

    image_url: Required[str]
    """
    A base64-encoded image in a data URL or a publicly accessible HTTP(S) image URL.
    """

    type: Required[Literal["input_image"]]

    detail: Optional[Literal["low", "high", "auto", "original"]]
    """The image detail level, using the selected model's image profile.

    Defaults to auto.
    """

    prompt_cache_breakpoint: Optional[DecisionPromptCacheBreakpointParam]
    """Marks the exact end of a reusable prompt prefix.

    The breakpoint inherits its TTL from the request's `prompt_cache_options.ttl`;
    the boundary is not rounded to a token block.
    """
