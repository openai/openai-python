# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from ......_types import SequenceNotStr

__all__ = ["APIKeyCreateParams"]


class APIKeyCreateParams(TypedDict, total=False):
    project_id: Required[str]
    """The ID of the project."""

    name: str
    """API key name."""

    scopes: SequenceNotStr[str]
    """API key scopes."""
