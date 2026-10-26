# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal, Required, TypedDict

from ...._types import SequenceNotStr

__all__ = ["UsageDecisionsParams"]


class UsageDecisionsParams(TypedDict, total=False):
    start_time: Required[int]
    """Start time (Unix seconds) of the query time range, inclusive."""

    api_key_ids: Optional[SequenceNotStr[str]]
    """Return only usage for these API keys."""

    batch: Optional[bool]
    """If `true`, return batch jobs only.

    If `false`, return non-batch jobs only. By default, return both.
    """

    bucket_width: Optional[Literal["1m", "1h", "1d"]]
    """Width of each time bucket in response.

    Currently `1m`, `1h` and `1d` are supported, default to `1d`.
    """

    end_time: Optional[int]
    """End time (Unix seconds) of the query time range, exclusive."""

    group_by: Optional[
        List[Literal["project_id", "user_id", "api_key_id", "model", "batch", "service_tier", "api_source"]]
    ]
    """Group the usage data by the specified fields.

    Support fields include `project_id`, `user_id`, `api_key_id`, `model`, `batch`,
    `service_tier`, `api_source` or any combination of them. When grouped by
    `api_source`, results use `agents_api` for attributed Agents API activity and
    `unlabeled` for all other activity. Without source grouping, `api_source` is
    null.
    """

    limit: Optional[int]
    """Specifies the number of buckets to return.

    - `bucket_width=1d`: default: 7, max: 31
    - `bucket_width=1h`: default: 24, max: 168
    - `bucket_width=1m`: default: 60, max: 1440
    """

    models: Optional[SequenceNotStr[str]]
    """Return only usage for these models."""

    page: Optional[str]
    """A cursor for use in pagination.

    Corresponding to the `next_page` field from the previous response.
    """

    project_ids: Optional[SequenceNotStr[str]]
    """Return only usage for these projects."""

    user_ids: Optional[SequenceNotStr[str]]
    """Return only usage for these users."""
