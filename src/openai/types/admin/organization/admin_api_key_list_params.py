# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, TypedDict

__all__ = ["AdminAPIKeyListParams"]


class AdminAPIKeyListParams(TypedDict, total=False):
    after: Optional[str]
    """Return keys with IDs that come after this ID in the pagination order."""

    limit: int
    """Maximum number of keys to return."""

    order: Literal["asc", "desc"]
    """Order results by creation time, ascending or descending."""
