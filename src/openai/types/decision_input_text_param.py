# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

from .decision_prompt_cache_breakpoint_param import DecisionPromptCacheBreakpointParam

__all__ = ["DecisionInputTextParam", "PromptCacheBreakpoint"]


class PromptCacheBreakpoint(TypedDict, total=False):
    """Marks the exact end of a reusable prompt prefix."""

    mode: Required[Literal["explicit"]]
    """The prompt cache mode."""


class DecisionInputTextParam(TypedDict, total=False):
    text: Required[str]

    type: Required[Literal["input_text"]]

    prompt_cache_breakpoint: Optional[DecisionPromptCacheBreakpointParam]
    """Marks the exact end of a reusable prompt prefix.

    The breakpoint inherits its TTL from the request's `prompt_cache_options.ttl`;
    the boundary is not rounded to a token block.
    """
