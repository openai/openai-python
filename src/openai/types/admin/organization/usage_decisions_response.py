# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["UsageDecisionsResponse", "Data", "DataResult"]


class DataResult(BaseModel):
    """The aggregated Decisions API usage details of the specific time bucket."""

    input_tokens: int
    """
    The aggregated number of input tokens used, including cached and cache-write
    tokens. This includes text, audio, and image tokens. For customers subscribed to
    Scale Tier, this includes Scale Tier tokens.
    """

    num_model_requests: int
    """The count of requests made to the model."""

    object: Literal["organization.usage.decisions.result"]

    output_tokens: int
    """
    The aggregated number of output tokens used across text, audio, and image
    outputs. For customers subscribed to Scale Tier, this includes Scale Tier
    tokens.
    """

    api_key_id: Optional[str] = None
    """
    When `group_by=api_key_id`, this field provides the API key ID of the grouped
    usage result.
    """

    api_source: Optional[Literal["agents_api", "unlabeled"]] = None
    """
    When grouped by `api_source`, `agents_api` identifies attributed Agents API
    activity and `unlabeled` includes all records without published source
    attribution, including historical and unknown origins. Unlabeled does not imply
    direct API usage. Without source grouping, this field is null.
    """

    batch: Optional[bool] = None
    """
    When `group_by=batch`, this field tells whether the grouped usage result is
    batch or not.
    """

    input_audio_tokens: Optional[int] = None
    """The aggregated number of uncached audio input tokens used."""

    input_cache_write_12h_tokens: Optional[int] = None
    """
    The aggregated number of input tokens written to the cache with a 12-hour
    retention period.
    """

    input_cache_write_30m_tokens: Optional[int] = None
    """
    The aggregated number of input tokens written to the cache with a 30-minute
    retention period.
    """

    input_cache_write_tokens: Optional[int] = None
    """
    The aggregated number of input tokens written to the cache across 30-minute and
    12-hour retention periods.
    """

    input_cached_audio_tokens: Optional[int] = None
    """The aggregated number of cached audio input tokens used."""

    input_cached_image_tokens: Optional[int] = None
    """The aggregated number of cached image input tokens used."""

    input_cached_text_tokens: Optional[int] = None
    """The aggregated number of cached text input tokens used."""

    input_cached_tokens: Optional[int] = None
    """
    The aggregated number of cached input tokens used across text, audio, and image
    inputs. For customers subscribed to Scale Tier, this includes Scale Tier tokens.
    """

    input_image_tokens: Optional[int] = None
    """The aggregated number of uncached image input tokens used."""

    input_text_tokens: Optional[int] = None
    """
    The aggregated number of uncached text input tokens used, excluding cache-write
    tokens.
    """

    input_uncached_tokens: Optional[int] = None
    """
    The aggregated number of uncached input tokens used across text, audio, and
    image inputs, excluding cache-write tokens.
    """

    model: Optional[str] = None
    """
    When `group_by=model`, this field provides the model name of the grouped usage
    result.
    """

    output_audio_tokens: Optional[int] = None
    """The aggregated number of audio output tokens used."""

    output_image_tokens: Optional[int] = None
    """The aggregated number of image output tokens used."""

    output_text_tokens: Optional[int] = None
    """The aggregated number of text output tokens used."""

    project_id: Optional[str] = None
    """
    When `group_by=project_id`, this field provides the project ID of the grouped
    usage result.
    """

    service_tier: Optional[str] = None
    """
    When `group_by=service_tier`, this field provides the service tier of the
    grouped usage result.
    """

    user_id: Optional[str] = None
    """
    When `group_by=user_id`, this field provides the user ID of the grouped usage
    result.
    """


class Data(BaseModel):
    end_time: int

    object: Literal["bucket"]

    results: List[DataResult]

    start_time: int


class UsageDecisionsResponse(BaseModel):
    data: List[Data]

    has_more: bool

    next_page: Optional[str] = None

    object: Literal["page"]
