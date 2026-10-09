# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["EnvironmentListParams"]


class EnvironmentListParams(TypedDict, total=False):
    after: str
    """Return environments after this environment ID in the selected order."""

    limit: int
    """The maximum number of environments to return, between 1 and 100.

    Defaults to 20.
    """

    order: Literal["asc", "desc"]
    """The order in which environments are returned. Defaults to `desc`.

    - `asc` - Returns resources in ascending order.
    - `desc` - Returns resources in descending order.
    """

    type: Literal["openai_hosted"]
    """The hosting type to list. Defaults to `openai_hosted`."""
