# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ServiceAccountUpdateParams"]


class ServiceAccountUpdateParams(TypedDict, total=False):
    project_id: Required[str]

    name: str
    """The updated service account name."""

    role: Literal["member", "owner"]
    """The updated service account role."""
