# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["RealtimeResponseUsageInputTokenDetails"]


class RealtimeResponseUsageInputTokenDetails(BaseModel):
    audio_tokens: Optional[int] = None
    """The number of audio tokens used in the Response."""

    cached_tokens: Optional[int] = None
    """The number of cached tokens used in the Response."""

    text_tokens: Optional[int] = None
    """The number of text tokens used in the Response."""
