# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["RealtimeClientSecretConfigParam", "ExpiresAfter"]


class ExpiresAfter(TypedDict, total=False):
    anchor: Required[Literal["created_at"]]
    """The anchor point for the ephemeral token expiration.

    Only `created_at` is currently supported.
    """

    seconds: int
    """The number of seconds from the anchor point to the expiration.

    Select a value between `10` and `7200`.
    """


class RealtimeClientSecretConfigParam(TypedDict, total=False):
    expires_after: ExpiresAfter
    """Configuration for the ephemeral token expiration."""
