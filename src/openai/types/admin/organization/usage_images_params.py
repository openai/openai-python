# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, TypedDict

from ...._types import SequenceNotStr

__all__ = ["UsageImagesParams"]


class UsageImagesParams(TypedDict, total=False):
    start_time: Required[int]
    """Start time (Unix seconds) of the query time range, inclusive."""

    api_key_ids: SequenceNotStr[str]
    """Return only usage for these API keys."""

    bucket_width: Literal["1m", "1h", "1d"]
    """Width of each time bucket in response.

    Currently `1m`, `1h` and `1d` are supported, default to `1d`.
    """

    end_time: int
    """End time (Unix seconds) of the query time range, exclusive."""

    group_by: List[Literal["project_id", "user_id", "api_key_id", "model", "size", "source"]]
    """Group the usage data by the specified fields.

    Support fields include `project_id`, `user_id`, `api_key_id`, `model`, `size`,
    `source` or any combination of them.
    """

    limit: int
    """Specifies the number of buckets to return.

    - `bucket_width=1d`: default: 7, max: 31
    - `bucket_width=1h`: default: 24, max: 168
    - `bucket_width=1m`: default: 60, max: 1440
    """

    models: SequenceNotStr[str]
    """Return only usage for these models."""

    page: str
    """A cursor for use in pagination.

    Corresponding to the `next_page` field from the previous response.
    """

    project_ids: SequenceNotStr[str]
    """Return only usage for these projects."""

    sizes: List[Literal["256x256", "512x512", "1024x1024", "1792x1792", "1024x1792"]]
    """Return only usages for these image sizes.

    Possible values are `256x256`, `512x512`, `1024x1024`, `1792x1792`, `1024x1792`
    or any combination of them.
    """

    sources: List[Literal["image.generation", "image.edit", "image.variation"]]
    """Return only usages for these sources.

    Possible values are `image.generation`, `image.edit`, `image.variation` or any
    combination of them.
    """

    user_ids: SequenceNotStr[str]
    """Return only usage for these users."""
