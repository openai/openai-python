# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["GroupCreateParams"]


class GroupCreateParams(TypedDict, total=False):
    group_id: Required[str]
    """Identifier of the group to add to the project."""

    role: Required[str]
    """Identifier of the project role to grant to the group."""
