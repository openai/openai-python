# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["BetaResponseInputTextParam", "PromptCacheBreakpoint"]


class PromptCacheBreakpoint(TypedDict, total=False):
    """Marks the exact end of a reusable prompt prefix.

    When `ttl` is omitted, the breakpoint inherits the request's `prompt_cache_options.ttl`; the boundary is not rounded to a token block.
    """

    mode: Required[Literal["explicit"]]
    """The breakpoint mode. Always `explicit`."""

    ttl: Literal["30m", "12h"]
    """The minimum lifetime of this cache breakpoint. Defaults to the request TTL."""


class BetaResponseInputTextParam(TypedDict, total=False):
    """A text input to the model."""

    text: Required[str]
    """The text input to the model."""

    type: Required[Literal["input_text"]]
    """The type of the input item. Always `input_text`."""

    prompt_cache_breakpoint: PromptCacheBreakpoint
    """Marks the exact end of a reusable prompt prefix.

    When `ttl` is omitted, the breakpoint inherits the request's
    `prompt_cache_options.ttl`; the boundary is not rounded to a token block.
    """
