# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["AdminAPIKeyCreateParams"]


class AdminAPIKeyCreateParams(TypedDict, total=False):
    name: Required[str]

    expires_in_seconds: int
    """The number of seconds until the API key expires.

    Omit this field for a key that does not expire.
    """
