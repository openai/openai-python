# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["RoleListParams"]


class RoleListParams(TypedDict, total=False):
    project_id: Required[str]

    after: str
    """Cursor for pagination.

    Provide the value from the previous response's `next` field to continue listing
    project roles.
    """

    limit: int
    """A limit on the number of project role assignments to return."""

    order: Literal["asc", "desc"]
    """Sort order for the returned project roles."""
