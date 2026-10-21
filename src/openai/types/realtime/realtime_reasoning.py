# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .realtime_reasoning_effort import RealtimeReasoningEffort

__all__ = ["RealtimeReasoning"]


class RealtimeReasoning(BaseModel):
    """Configuration for reasoning-capable Realtime models such as `gpt-realtime-2`."""

    effort: Optional[RealtimeReasoningEffort] = None
    """
    Constrains effort on reasoning for reasoning-capable Realtime models such as
    `gpt-realtime-2`.
    """
