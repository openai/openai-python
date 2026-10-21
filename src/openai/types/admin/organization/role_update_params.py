# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

from ...._types import SequenceNotStr

__all__ = ["RoleUpdateParams"]


class RoleUpdateParams(TypedDict, total=False):
    description: Optional[str]
    """New description for the role."""

    permissions: Optional[SequenceNotStr[str]]
    """Updated set of permissions for the role."""

    role_name: Optional[str]
    """New name for the role."""
