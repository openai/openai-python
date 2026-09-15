# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, TypedDict

__all__ = ["FileListParams"]


class FileListParams(TypedDict, total=False):
    limit: Optional[int]
    """The maximum number of files to return, between 1 and 100."""

    order: Literal["asc", "desc"]
    """Sort by case-sensitive path components. Defaults to descending.

    - `asc` - Returns resources in ascending order.
    - `desc` - Returns resources in descending order.
    """

    page: str
    """The opaque token from the previous page. Keep the same path, order, and limit."""

    path: Optional[str]
    """Restrict the listing to this absolute workspace directory."""
