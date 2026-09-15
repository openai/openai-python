# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

from ......_types import SequenceNotStr

__all__ = ["APIKeyCreateParams"]


class APIKeyCreateParams(TypedDict, total=False):
    project_id: Required[str]
    """The ID of the project."""

    expires_in_seconds: Optional[int]
    """Number of seconds until the API key expires."""

    name: str
    """API key name."""

    scopes: SequenceNotStr[str]
    """API key scopes."""
