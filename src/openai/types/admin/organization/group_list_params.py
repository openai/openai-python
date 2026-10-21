# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["GroupListParams"]


class GroupListParams(TypedDict, total=False):
    after: str
    """A cursor for use in pagination.

    `after` is a group ID that defines your place in the list. For instance, if you
    make a list request and receive 100 objects, ending with group_abc, your
    subsequent call can include `after=group_abc` in order to fetch the next page of
    the list.
    """

    limit: int
    """A limit on the number of groups to be returned.

    Limit can range between 0 and 1000, and the default is 100.
    """

    order: Literal["asc", "desc"]
    """Specifies the sort order of the returned groups."""
