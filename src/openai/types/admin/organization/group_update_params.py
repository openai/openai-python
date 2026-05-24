# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["GroupUpdateParams"]


class GroupUpdateParams(TypedDict, total=False):
    name: Required[str]
    """New display name for the group."""
