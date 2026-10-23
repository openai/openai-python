# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Literal, TypedDict

from .vault_status_filter_param import VaultStatusFilterParam

__all__ = ["VaultListParams"]


class VaultListParams(TypedDict, total=False):
    after: str
    """Return resources after this resource ID in the selected order."""

    limit: int
    """The maximum number of resources to return, between 1 and 100. Defaults to 20."""

    metadata: Dict[str, str]
    """Exact string matches supplied as `metadata[key]=value`.

    All supplied pairs must match. Up to 16 pairs, with keys from 1 to 64 characters
    and values up to 512 characters. Filtering is eventually consistent; metadata
    changes may take time to appear.
    """

    order: Literal["asc", "desc"]
    """The order in which resources are returned. Defaults to `desc`.

    - `asc` - Returns resources in ascending order.
    - `desc` - Returns resources in descending order.
    """

    status: VaultStatusFilterParam
    """
    Filter by one status or a list, such as `status=active` or
    `status[]=active&status[]=archived`. Both statuses are included by default.
    """
