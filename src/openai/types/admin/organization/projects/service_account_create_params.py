# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["ServiceAccountCreateParams"]


class ServiceAccountCreateParams(TypedDict, total=False):
    name: Required[str]
    """The name of the service account being created."""

    create_service_account_only: Optional[bool]
    """Create the service account without default roles or an API key."""
