# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseInputFileContent", "PromptCacheBreakpoint"]


class PromptCacheBreakpoint(BaseModel):
    """Marks the exact end of a reusable prompt prefix.

    The breakpoint inherits its TTL from the request's `prompt_cache_options.ttl`; the boundary is not rounded to a token block.
    """

    mode: Literal["explicit"]
    """The breakpoint mode. Always `explicit`."""


class ResponseInputFileContent(BaseModel):
    """A file input to the model."""

    type: Literal["input_file"]
    """The type of the input item. Always `input_file`."""

    detail: Optional[Literal["auto", "low", "high"]] = None
    """The detail level of the file to be sent to the model.

    Use `auto` to let the system select the detail level; for GPT-5.6 and later
    models, `auto` uses high-quality rendering, which may increase input token
    usage. Use `low` for lower-cost rendering, or `high` to render the file at
    higher quality. Defaults to `auto`.
    """

    file_data: Optional[str] = None
    """The base64-encoded data of the file to be sent to the model."""

    file_id: Optional[str] = None
    """The ID of the file to be sent to the model."""

    file_url: Optional[str] = None
    """The URL of the file to be sent to the model."""

    filename: Optional[str] = None
    """The name of the file to be sent to the model."""

    prompt_cache_breakpoint: Optional[PromptCacheBreakpoint] = None
    """Marks the exact end of a reusable prompt prefix.

    The breakpoint inherits its TTL from the request's `prompt_cache_options.ttl`;
    the boundary is not rounded to a token block.
    """
