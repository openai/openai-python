# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal

import httpx

from .... import _legacy_response
from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import (
    maybe_transform,
    async_maybe_transform,
)
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from .output_items import (
    OutputItems,
    AsyncOutputItems,
    OutputItemsWithRawResponse,
    AsyncOutputItemsWithRawResponse,
    OutputItemsWithStreamingResponse,
    AsyncOutputItemsWithStreamingResponse,
)
from ....pagination import SyncCursorPage, AsyncCursorPage
from ....types.evals import run_list_params, run_create_params
from ...._base_client import AsyncPaginator, make_request_options
from ....types.shared_params.metadata import Metadata
from ....types.evals.run_list_response import RunListResponse
from ....types.evals.run_cancel_response import RunCancelResponse
from ....types.evals.run_create_response import RunCreateResponse
from ....types.evals.run_delete_response import RunDeleteResponse
from ....types.evals.run_retrieve_response import RunRetrieveResponse

__all__ = ["Runs", "AsyncRuns"]


class Runs(SyncAPIResource):
    @cached_property
    def output_items(self) -> OutputItems:
        return OutputItems(self._client)

    @cached_property
    def with_raw_response(self) -> RunsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return RunsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RunsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return RunsWithStreamingResponse(self)

    def create(
        self,
        eval_id: str,
        *,
        data_source: run_create_params.DataSource,
        metadata: Optional[Metadata] | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RunCreateResponse:
        """Create a new evaluation run.

        This is the endpoint that will kick off grading.

        Args:
          data_source: Details about the run's data source.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format, and
              querying for objects via API or the dashboard.

              Keys are strings with a maximum length of 64 characters. Values are strings with
              a maximum length of 512 characters.

          name: The name of the run.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not eval_id:
            raise ValueError(f"Expected a non-empty value for `eval_id` but received {eval_id!r}")
        return self._post(
            f"/evals/{eval_id}/runs",
            body=maybe_transform(
                {
                    "data_source": data_source,
                    "metadata": metadata,
                    "name": name,
                },
                run_create_params.RunCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RunCreateResponse,
        )

    def retrieve(
        self,
        run_id: str,
        *,
        eval_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RunRetrieveResponse:
        """
        Get an evaluation run by ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not eval_id:
            raise ValueError(f"Expected a non-empty value for `eval_id` but received {eval_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        return self._get(
            f"/evals/{eval_id}/runs/{run_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RunRetrieveResponse,
        )

    def list(
        self,
        eval_id: str,
        *,
        after: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        status: Literal["queued", "in_progress", "completed", "canceled", "failed"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncCursorPage[RunListResponse]:
        """
        Get a list of runs for an evaluation.

        Args:
          after: Identifier for the last run from the previous pagination request.

          limit: Number of runs to retrieve.

          order: Sort order for runs by timestamp. Use `asc` for ascending order or `desc` for
              descending order. Defaults to `asc`.

          status: Filter runs by status. Use "queued" | "in_progress" | "failed" | "completed" |
              "canceled".

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not eval_id:
            raise ValueError(f"Expected a non-empty value for `eval_id` but received {eval_id!r}")
        return self._get_api_list(
            f"/evals/{eval_id}/runs",
            page=SyncCursorPage[RunListResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                        "order": order,
                        "status": status,
                    },
                    run_list_params.RunListParams,
                ),
            ),
            model=RunListResponse,
        )

    def delete(
        self,
        run_id: str,
        *,
        eval_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RunDeleteResponse:
        """
        Delete an eval run.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not eval_id:
            raise ValueError(f"Expected a non-empty value for `eval_id` but received {eval_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        return self._delete(
            f"/evals/{eval_id}/runs/{run_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RunDeleteResponse,
        )

    def cancel(
        self,
        run_id: str,
        *,
        eval_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RunCancelResponse:
        """
        Cancel an ongoing evaluation run.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not eval_id:
            raise ValueError(f"Expected a non-empty value for `eval_id` but received {eval_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        return self._post(
            f"/evals/{eval_id}/runs/{run_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RunCancelResponse,
        )


class AsyncRuns(AsyncAPIResource):
    @cached_property
    def output_items(self) -> AsyncOutputItems:
        return AsyncOutputItems(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncRunsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRunsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRunsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncRunsWithStreamingResponse(self)

    async def create(
        self,
        eval_id: str,
        *,
        data_source: run_create_params.DataSource,
        metadata: Optional[Metadata] | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RunCreateResponse:
        """Create a new evaluation run.

        This is the endpoint that will kick off grading.

        Args:
          data_source: Details about the run's data source.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format, and
              querying for objects via API or the dashboard.

              Keys are strings with a maximum length of 64 characters. Values are strings with
              a maximum length of 512 characters.

          name: The name of the run.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not eval_id:
            raise ValueError(f"Expected a non-empty value for `eval_id` but received {eval_id!r}")
        return await self._post(
            f"/evals/{eval_id}/runs",
            body=await async_maybe_transform(
                {
                    "data_source": data_source,
                    "metadata": metadata,
                    "name": name,
                },
                run_create_params.RunCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RunCreateResponse,
        )

    async def retrieve(
        self,
        run_id: str,
        *,
        eval_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RunRetrieveResponse:
        """
        Get an evaluation run by ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not eval_id:
            raise ValueError(f"Expected a non-empty value for `eval_id` but received {eval_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        return await self._get(
            f"/evals/{eval_id}/runs/{run_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RunRetrieveResponse,
        )

    def list(
        self,
        eval_id: str,
        *,
        after: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        status: Literal["queued", "in_progress", "completed", "canceled", "failed"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[RunListResponse, AsyncCursorPage[RunListResponse]]:
        """
        Get a list of runs for an evaluation.

        Args:
          after: Identifier for the last run from the previous pagination request.

          limit: Number of runs to retrieve.

          order: Sort order for runs by timestamp. Use `asc` for ascending order or `desc` for
              descending order. Defaults to `asc`.

          status: Filter runs by status. Use "queued" | "in_progress" | "failed" | "completed" |
              "canceled".

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not eval_id:
            raise ValueError(f"Expected a non-empty value for `eval_id` but received {eval_id!r}")
        return self._get_api_list(
            f"/evals/{eval_id}/runs",
            page=AsyncCursorPage[RunListResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                        "order": order,
                        "status": status,
                    },
                    run_list_params.RunListParams,
                ),
            ),
            model=RunListResponse,
        )

    async def delete(
        self,
        run_id: str,
        *,
        eval_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RunDeleteResponse:
        """
        Delete an eval run.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not eval_id:
            raise ValueError(f"Expected a non-empty value for `eval_id` but received {eval_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        return await self._delete(
            f"/evals/{eval_id}/runs/{run_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RunDeleteResponse,
        )

    async def cancel(
        self,
        run_id: str,
        *,
        eval_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RunCancelResponse:
        """
        Cancel an ongoing evaluation run.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not eval_id:
            raise ValueError(f"Expected a non-empty value for `eval_id` but received {eval_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        return await self._post(
            f"/evals/{eval_id}/runs/{run_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RunCancelResponse,
        )


class RunsWithRawResponse:
    def __init__(self, runs: Runs) -> None:
        self._runs = runs

        self.create = _legacy_response.to_raw_response_wrapper(
            runs.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            runs.retrieve,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            runs.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            runs.delete,
        )
        self.cancel = _legacy_response.to_raw_response_wrapper(
            runs.cancel,
        )

    @cached_property
    def output_items(self) -> OutputItemsWithRawResponse:
        return OutputItemsWithRawResponse(self._runs.output_items)


class AsyncRunsWithRawResponse:
    def __init__(self, runs: AsyncRuns) -> None:
        self._runs = runs

        self.create = _legacy_response.async_to_raw_response_wrapper(
            runs.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            runs.retrieve,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            runs.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            runs.delete,
        )
        self.cancel = _legacy_response.async_to_raw_response_wrapper(
            runs.cancel,
        )

    @cached_property
    def output_items(self) -> AsyncOutputItemsWithRawResponse:
        return AsyncOutputItemsWithRawResponse(self._runs.output_items)


class RunsWithStreamingResponse:
    def __init__(self, runs: Runs) -> None:
        self._runs = runs

        self.create = to_streamed_response_wrapper(
            runs.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            runs.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            runs.list,
        )
        self.delete = to_streamed_response_wrapper(
            runs.delete,
        )
        self.cancel = to_streamed_response_wrapper(
            runs.cancel,
        )

    @cached_property
    def output_items(self) -> OutputItemsWithStreamingResponse:
        return OutputItemsWithStreamingResponse(self._runs.output_items)


class AsyncRunsWithStreamingResponse:
    def __init__(self, runs: AsyncRuns) -> None:
        self._runs = runs

        self.create = async_to_streamed_response_wrapper(
            runs.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            runs.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            runs.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            runs.delete,
        )
        self.cancel = async_to_streamed_response_wrapper(
            runs.cancel,
        )

    @cached_property
    def output_items(self) -> AsyncOutputItemsWithStreamingResponse:
        return AsyncOutputItemsWithStreamingResponse(self._runs.output_items)
