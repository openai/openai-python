# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["UserUpdateParams"]


class UserUpdateParams(TypedDict, total=False):
    developer_persona: Optional[str]
    """Developer persona metadata."""

    role: Optional[str]
    """`owner` or `reader`"""

    role_id: Optional[str]
    """Role ID to assign to the user."""

    technical_level: Optional[str]
    """Technical level metadata."""
