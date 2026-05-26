# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["UserCreateParams"]


class UserCreateParams(TypedDict, total=False):
    role: Required[str]
    """`owner` or `member`"""

    email: Optional[str]
    """Email of the user to add."""

    user_id: Optional[str]
    """The ID of the user."""
