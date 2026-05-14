# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["UserUpdateParams"]


class UserUpdateParams(TypedDict, total=False):
    project_id: Required[str]

    role: Optional[str]
    """`owner` or `member`"""
