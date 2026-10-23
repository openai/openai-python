# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from ....._types import SequenceNotStr

__all__ = ["APIKeyUpdateParams"]


class APIKeyUpdateParams(TypedDict, total=False):
    project_id: Required[str]

    expires_in_seconds: int
    """Number of seconds from this request until the API key expires.

    Must comply with the organization and project expiry policies. Expired keys
    cannot be updated. Retrying resets the expiry relative to the new request. Omit
    to keep the current expiration.
    """

    scopes: SequenceNotStr[str]
    """Replace the API key scope restrictions.

    Omit to leave scopes unchanged. An empty array removes key restrictions (All
    permissions), subject to the owner's effective permissions. Use ["api.all.read"]
    for read-only access. Scopes do not change the owner's roles or grant
    administrative permissions.
    """
