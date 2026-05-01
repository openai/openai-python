# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["ProjectUpdateParams"]


class ProjectUpdateParams(TypedDict, total=False):
    external_key_id: Optional[str]
    """External key ID to associate with the project."""

    geography: Optional[str]
    """Geography for the project."""

    name: Optional[str]
    """The updated name of the project, this name appears in reports."""
