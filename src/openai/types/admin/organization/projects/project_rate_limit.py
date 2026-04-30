# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["ProjectRateLimit"]


class ProjectRateLimit(BaseModel):
    """Represents a project rate limit config."""

    id: str
    """The identifier, which can be referenced in API endpoints."""

    max_requests_per_1_minute: int
    """The maximum requests per minute."""

    max_tokens_per_1_minute: int
    """The maximum tokens per minute."""

    model: str
    """The model this rate limit applies to."""

    object: Literal["project.rate_limit"]
    """The object type, which is always `project.rate_limit`"""

    batch_1_day_max_input_tokens: Optional[int] = None
    """The maximum batch input tokens per day. Only present for relevant models."""

    max_audio_megabytes_per_1_minute: Optional[int] = None
    """The maximum audio megabytes per minute. Only present for relevant models."""

    max_images_per_1_minute: Optional[int] = None
    """The maximum images per minute. Only present for relevant models."""

    max_requests_per_1_day: Optional[int] = None
    """The maximum requests per day. Only present for relevant models."""
