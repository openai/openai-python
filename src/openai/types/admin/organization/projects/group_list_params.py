# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["GroupListParams"]


class GroupListParams(TypedDict, total=False):
    after: str
    """Cursor for pagination.

    Provide the ID of the last group from the previous response to fetch the next
    page.
    """

    limit: int
    """A limit on the number of project groups to return. Defaults to 20."""

    order: Literal["asc", "desc"]
    """Sort order for the returned groups."""
