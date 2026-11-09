# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Literal, TypedDict

__all__ = ["SessionListParams"]


class SessionListParams(TypedDict, total=False):
    after: str
    """Return resources after this resource ID in the selected order."""

    agent_id: str
    """Only return sessions whose root agent has this ID.

    Omit to return sessions for all agents.
    """

    limit: int
    """The maximum number of resources to return, between 1 and 100. Defaults to 20."""

    metadata: Dict[str, str]
    """Exact string matches supplied as `metadata[key]=value`.

    All supplied pairs must match. Up to 16 pairs, with keys from 1 to 64 characters
    and values up to 512 characters. New sessions and metadata updates may take time
    to appear in filtered results.
    """

    order: Literal["asc", "desc"]
    """The order in which resources are returned. Defaults to `desc`.

    - `asc` - Returns resources in ascending order.
    - `desc` - Returns resources in descending order.
    """
