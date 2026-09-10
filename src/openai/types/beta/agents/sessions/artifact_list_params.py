# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, TypedDict

__all__ = ["ArtifactListParams"]


class ArtifactListParams(TypedDict, total=False):
    after: Optional[str]
    """Return artifacts after this immutable artifact ID."""

    environment_id: Optional[str]
    """Restrict the listing to artifacts produced by this environment."""

    limit: Optional[int]
    """The maximum number of artifacts to return, between 1 and 100."""

    order: Literal["asc", "desc"]
    """Sort by creation time and ID. Defaults to descending.

    - `asc` - Returns resources in ascending order.
    - `desc` - Returns resources in descending order.
    """
