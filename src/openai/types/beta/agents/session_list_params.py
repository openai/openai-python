# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, TypedDict

__all__ = ["SessionListParams"]


class SessionListParams(TypedDict, total=False):
    after: str
    """Return resources after this resource ID in the selected order."""

    agent_id: str
    """Only return sessions whose root agent has this ID.

    Omit to return sessions for all agents.
    """

    limit: Optional[int]
    """The maximum number of resources to return."""

    order: Literal["asc", "desc"]
    """Sort order by the `created_at` timestamp.

    Use `asc` for ascending order or `desc` for descending order. Defaults to
    `desc`.

    - `asc` - Returns resources in ascending order.
    - `desc` - Returns resources in descending order.
    """
