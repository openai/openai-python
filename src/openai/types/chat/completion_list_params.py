# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, TypedDict

from ..shared_params.metadata import Metadata

__all__ = ["CompletionListParams"]


class CompletionListParams(TypedDict, total=False):
    after: str
    """Identifier for the last chat completion from the previous pagination request."""

    limit: int
    """Number of chat completions to retrieve."""

    metadata: Optional[Metadata]
    """A list of metadata keys to filter the chat completions by. Example:

    `metadata[key1]=value1&metadata[key2]=value2`
    """

    model: str
    """The model used to generate the chat completions."""

    order: Literal["asc", "desc"]
    """Sort order for chat completions by timestamp.

    Use `asc` for ascending order or `desc` for descending order. Defaults to `asc`.
    """
