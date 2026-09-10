# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["ServiceAccountCreateParams"]


class ServiceAccountCreateParams(TypedDict, total=False):
    name: Required[str]
    """The name of the service account being created."""

    create_service_account_only: Optional[bool]
    """Create the service account without default roles or an API key."""

    expires_in_seconds: Optional[int]
    """Number of seconds until the initial API key expires.

    If omitted or null, the key does not expire unless the effective organization or
    project policy requires an expiration. When a policy sets a maximum lifetime,
    this value must be provided and must not exceed that limit. A non-null value
    cannot be used when `create_service_account_only` is true.
    """
