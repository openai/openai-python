# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["UserListParams"]


class UserListParams(TypedDict, total=False):
    after: str
    """A cursor for use in pagination.

    Provide the ID of the last user from the previous list response to retrieve the
    next page.
    """

    limit: int
    """A limit on the number of users to be returned.

    Limit can range between 0 and 1000, and the default is 100.
    """

    order: Literal["asc", "desc"]
    """Specifies the sort order of users in the list."""
