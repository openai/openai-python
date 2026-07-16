# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ResponseInputTextParam", "PromptCacheBreakpoint"]


class PromptCacheBreakpoint(TypedDict, total=False):
    """Marks the exact end of a reusable prompt prefix.

    The breakpoint inherits its TTL from the request's `prompt_cache_options.ttl`; the boundary is not rounded to a token block.
    """

    mode: Required[Literal["explicit"]]
    """The breakpoint mode. Always `explicit`."""


class ResponseInputTextParam(TypedDict, total=False):
    """A text input to the model."""

    text: Required[str]
    """The text input to the model."""

    type: Required[Literal["input_text"]]
    """The type of the input item. Always `input_text`."""

    prompt_cache_breakpoint: PromptCacheBreakpoint
    """Marks the exact end of a reusable prompt prefix.

    The breakpoint inherits its TTL from the request's `prompt_cache_options.ttl`;
    the boundary is not rounded to a token block.
    """
