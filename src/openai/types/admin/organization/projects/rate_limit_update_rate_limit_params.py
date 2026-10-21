# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["RateLimitUpdateRateLimitParams"]


class RateLimitUpdateRateLimitParams(TypedDict, total=False):
    project_id: Required[str]

    batch_1_day_max_input_tokens: int
    """The maximum batch input tokens per day. Only relevant for certain models."""

    max_audio_megabytes_per_1_minute: int
    """The maximum audio megabytes per minute. Only relevant for certain models."""

    max_images_per_1_minute: int
    """The maximum images per minute. Only relevant for certain models."""

    max_requests_per_1_day: int
    """The maximum requests per day. Only relevant for certain models."""

    max_requests_per_1_minute: int
    """The maximum requests per minute."""

    max_tokens_per_1_minute: int
    """The maximum tokens per minute."""
