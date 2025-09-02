# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["RealtimeClientSecretConfig", "ExpiresAfter"]


class ExpiresAfter(BaseModel):
    anchor: Literal["created_at"]
    """The anchor point for the ephemeral token expiration.

    Only `created_at` is currently supported.
    """

    seconds: Optional[int] = None
    """The number of seconds from the anchor point to the expiration.

    Select a value between `10` and `7200`.
    """


class RealtimeClientSecretConfig(BaseModel):
    expires_after: Optional[ExpiresAfter] = None
    """Configuration for the ephemeral token expiration."""
