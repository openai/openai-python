# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ...._models import BaseModel

__all__ = ["ChatSessionRateLimits"]


class ChatSessionRateLimits(BaseModel):
    max_requests_per_1_minute: int
    """Maximum allowed requests per one-minute window."""
