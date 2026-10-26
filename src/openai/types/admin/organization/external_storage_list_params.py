# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, TypedDict

__all__ = ["ExternalStorageListParams"]


class ExternalStorageListParams(TypedDict, total=False):
    after: Optional[str]
    """Return external storage configurations after this ID."""

    limit: int

    order: Literal["asc", "desc"]

    project_id: Optional[str]
