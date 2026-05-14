# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

from ...._types import SequenceNotStr

__all__ = ["RoleCreateParams"]


class RoleCreateParams(TypedDict, total=False):
    permissions: Required[SequenceNotStr[str]]
    """Permissions to grant to the role."""

    role_name: Required[str]
    """Unique name for the role."""

    description: Optional[str]
    """Optional description of the role."""
