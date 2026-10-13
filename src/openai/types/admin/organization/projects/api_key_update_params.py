# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["APIKeyUpdateParams"]


class APIKeyUpdateParams(TypedDict, total=False):
    project_id: Required[str]

    expires_in_seconds: Required[int]
    """Number of seconds from this request until the API key expires.

    Must comply with the organization and project expiry policies. Expired keys
    cannot be updated. Retrying resets the expiry relative to the new request.
    """
