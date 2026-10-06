# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ItemListParams"]


class ItemListParams(TypedDict, total=False):
    session_id: Required[str]

    after: str
    """Return items after this cursor in the selected order.

    Pass the previous response's last_id, which can differ from the last item's ID.
    """

    limit: int
    """The maximum number of resources to return, between 1 and 100. Defaults to 20."""

    order: Literal["asc", "desc"]
    """The order in which resources are returned. Defaults to `desc`.

    - `asc` - Returns resources in ascending order.
    - `desc` - Returns resources in descending order.
    """
