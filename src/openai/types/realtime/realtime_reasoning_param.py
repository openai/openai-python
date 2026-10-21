# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .realtime_reasoning_effort import RealtimeReasoningEffort

__all__ = ["RealtimeReasoningParam"]


class RealtimeReasoningParam(TypedDict, total=False):
    """Configuration for reasoning-capable Realtime models such as `gpt-realtime-2`."""

    effort: RealtimeReasoningEffort
    """
    Constrains effort on reasoning for reasoning-capable Realtime models such as
    `gpt-realtime-2`.
    """
