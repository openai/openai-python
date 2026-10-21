# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["GroupCreateParams"]


class GroupCreateParams(TypedDict, total=False):
    name: Required[str]
    """Human readable name for the group."""
