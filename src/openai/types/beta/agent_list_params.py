# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, TypedDict

__all__ = ["AgentListParams"]


class AgentListParams(TypedDict, total=False):
    after: str
    """Return resources after this resource ID in the selected order."""

    limit: Optional[int]
    """The maximum number of resources to return."""

    order: Literal["asc", "desc"]
    """The order in which resources are returned. Defaults to `desc`.

    - `asc` - Returns resources in ascending order.
    - `desc` - Returns resources in descending order.
    """
