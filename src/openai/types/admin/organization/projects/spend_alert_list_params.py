# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["SpendAlertListParams"]


class SpendAlertListParams(TypedDict, total=False):
    after: str
    """Cursor for pagination.

    Provide the ID of the last spend alert from the previous response to fetch the
    next page.
    """

    before: str
    """Cursor for pagination.

    Provide the ID of the first spend alert from the previous response to fetch the
    previous page.
    """

    limit: int
    """A limit on the number of spend alerts to return. Defaults to 20."""

    order: Literal["asc", "desc"]
    """Sort order for the returned spend alerts."""
