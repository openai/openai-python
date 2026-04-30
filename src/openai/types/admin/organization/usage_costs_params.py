# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

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

    group_by: List[Literal["project_id", "line_item", "api_key_id"]]
    """Group the costs by the specified fields.

    Support fields include `project_id`, `line_item`, `api_key_id` and any
    combination of them.
    """

    limit: int
    """A limit on the number of buckets to be returned.

    Limit can range between 1 and 180, and the default is 7.
    """

    page: str
    """A cursor for use in pagination.

    Corresponding to the `next_page` field from the previous response.
    """

    project_ids: SequenceNotStr[str]
    """Return only costs for these projects."""
