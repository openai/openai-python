# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["ResponseInputFileParam", "PromptCacheBreakpoint"]


class PromptCacheBreakpoint(TypedDict, total=False):
    """Marks the exact end of a reusable prompt prefix.

    The breakpoint inherits its TTL from the request's `prompt_cache_options.ttl`; the boundary is not rounded to a token block.
    """

    mode: Required[Literal["explicit"]]
    """The breakpoint mode. Always `explicit`."""


class ResponseInputFileParam(TypedDict, total=False):
    """A file input to the model."""

    type: Required[Literal["input_file"]]
    """The type of the input item. Always `input_file`."""

    detail: Literal["auto", "low", "high"]
    """The detail level of the file to be sent to the model.

    Use `auto` to let the system select the detail level; for GPT-5.6 and later
    models, `auto` uses high-quality rendering, which may increase input token
    usage. Use `low` for lower-cost rendering, or `high` to render the file at
    higher quality. Defaults to `auto`.
    """

    file_data: str
    """The content of the file to be sent to the model."""

    file_id: Optional[str]
    """The ID of the file to be sent to the model."""

    file_url: str
    """The URL of the file to be sent to the model."""

    filename: str
    """The name of the file to be sent to the model."""

    prompt_cache_breakpoint: PromptCacheBreakpoint
    """Marks the exact end of a reusable prompt prefix.

    The breakpoint inherits its TTL from the request's `prompt_cache_options.ttl`;
    the boundary is not rounded to a token block.
    """
