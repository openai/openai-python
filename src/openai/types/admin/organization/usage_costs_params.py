# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, TypedDict

from ...._types import SequenceNotStr

__all__ = ["UsageCostsParams"]


class UsageCostsParams(TypedDict, total=False):
    start_time: Required[int]
    """Start time (Unix seconds) of the query time range, inclusive."""

    api_key_ids: SequenceNotStr[str]
    """Return only costs for these API keys."""

    bucket_width: Literal["1d"]
    """Width of each time bucket in response.

    Currently only `1d` is supported, default to `1d`.
    """

    end_time: int
    """End time (Unix seconds) of the query time range, exclusive."""

    group_by: List[Literal["project_id", "user_id", "line_item", "api_key_id", "api_source"]]
    """Group the costs by the specified fields.

    Supported fields include `project_id`, `user_id`, `line_item`, `api_key_id`, and
    `api_source`. Support for combining `user_id` with `project_id` grouping or the
    `project_ids` filter depends on the organization and requested time range.
    Unsupported combinations return HTTP 400. When grouped by `api_source`, results
    use `agents_api` for attributed Agents API activity and `unlabeled` for all
    other activity. Without source grouping, `api_source` is null.
    """

    limit: int
    """A limit on the number of buckets to be returned.

    Limit can range between 1 and 180, and the default is 7.
    """

    line_items: SequenceNotStr[str]
    """Return only costs for these exact line item names.

    Each value must match the complete `line_item` value, for example
    `gpt-6-astra, input_tokens`.
    """

    page: str
    """A cursor for use in pagination.

    Corresponding to the `next_page` field from the previous response.
    """

    project_ids: SequenceNotStr[str]
    """Return only costs for these projects."""
