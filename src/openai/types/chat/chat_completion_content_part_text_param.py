# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ChatCompletionContentPartTextParam", "PromptCacheBreakpoint"]


class PromptCacheBreakpoint(TypedDict, total=False):
    """Marks the exact end of a reusable prompt prefix.

    The breakpoint inherits its TTL from the request's `prompt_cache_options.ttl`; the boundary is not rounded to a token block.
    """

    mode: Required[Literal["explicit"]]
    """The breakpoint mode. Always `explicit`."""


class ChatCompletionContentPartTextParam(TypedDict, total=False):
    """
    Learn about [text inputs](https://platform.openai.com/docs/guides/text-generation).
    """

    text: Required[str]
    """The text content."""

    type: Required[Literal["text"]]
    """The type of the content part."""

    prompt_cache_breakpoint: PromptCacheBreakpoint
    """Marks the exact end of a reusable prompt prefix.

    The breakpoint inherits its TTL from the request's `prompt_cache_options.ttl`;
    the boundary is not rounded to a token block.
    """
