# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .... import _legacy_response
from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ....pagination import SyncCursorPage, AsyncCursorPage
from ...._base_client import (
    AsyncPaginator,
    make_request_options,
)
from ....types.fine_tuning.jobs import checkpoint_list_params
from ....types.fine_tuning.jobs.fine_tuning_job_checkpoint import FineTuningJobCheckpoint

__all__ = ["Checkpoints", "AsyncCheckpoints"]


class Checkpoints(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CheckpointsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return CheckpointsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CheckpointsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return CheckpointsWithStreamingResponse(self)

    def list(
        self,
        fine_tuning_job_id: str,
        *,
        after: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncCursorPage[FineTuningJobCheckpoint]:
        """
        List checkpoints for a fine-tuning job.

        Args:
          after: Identifier for the last checkpoint ID from the previous pagination request.

          limit: Number of checkpoints to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not fine_tuning_job_id:
            raise ValueError(f"Expected a non-empty value for `fine_tuning_job_id` but received {fine_tuning_job_id!r}")
        return self._get_api_list(
            f"/fine_tuning/jobs/{fine_tuning_job_id}/checkpoints",
            page=SyncCursorPage[FineTuningJobCheckpoint],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                    },
                    checkpoint_list_params.CheckpointListParams,
                ),
            ),
            model=FineTuningJobCheckpoint,
        )


class AsyncCheckpoints(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCheckpointsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCheckpointsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCheckpointsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncCheckpointsWithStreamingResponse(self)

    def list(
        self,
        fine_tuning_job_id: str,
        *,
        after: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[FineTuningJobCheckpoint, AsyncCursorPage[FineTuningJobCheckpoint]]:
        """
        List checkpoints for a fine-tuning job.

        Args:
          after: Identifier for the last checkpoint ID from the previous pagination request.

          limit: Number of checkpoints to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not fine_tuning_job_id:
            raise ValueError(f"Expected a non-empty value for `fine_tuning_job_id` but received {fine_tuning_job_id!r}")
        return self._get_api_list(
            f"/fine_tuning/jobs/{fine_tuning_job_id}/checkpoints",
            page=AsyncCursorPage[FineTuningJobCheckpoint],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                    },
                    checkpoint_list_params.CheckpointListParams,
                ),
            ),
            model=FineTuningJobCheckpoint,
        )


class CheckpointsWithRawResponse:
    def __init__(self, checkpoints: Checkpoints) -> None:
        self._checkpoints = checkpoints

        self.list = _legacy_response.to_raw_response_wrapper(
            checkpoints.list,
        )


class AsyncCheckpointsWithRawResponse:
    def __init__(self, checkpoints: AsyncCheckpoints) -> None:
        self._checkpoints = checkpoints

        self.list = _legacy_response.async_to_raw_response_wrapper(
            checkpoints.list,
        )


class CheckpointsWithStreamingResponse:
    def __init__(self, checkpoints: Checkpoints) -> None:
        self._checkpoints = checkpoints

        self.list = to_streamed_response_wrapper(
            checkpoints.list,
        )


class AsyncCheckpointsWithStreamingResponse:
    def __init__(self, checkpoints: AsyncCheckpoints) -> None:
        self._checkpoints = checkpoints

        self.list = async_to_streamed_response_wrapper(
            checkpoints.list,
        )
