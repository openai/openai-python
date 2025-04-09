# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Literal

import httpx

from ... import _legacy_response
from ...types import eval_list_params, eval_create_params, eval_update_params
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import (
    maybe_transform,
    async_maybe_transform,
)
from ..._compat import cached_property
from .runs.runs import (
    Runs,
    AsyncRuns,
    RunsWithRawResponse,
    AsyncRunsWithRawResponse,
    RunsWithStreamingResponse,
    AsyncRunsWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ...pagination import SyncCursorPage, AsyncCursorPage
from ..._base_client import AsyncPaginator, make_request_options
from ...types.eval_list_response import EvalListResponse
from ...types.eval_create_response import EvalCreateResponse
from ...types.eval_delete_response import EvalDeleteResponse
from ...types.eval_update_response import EvalUpdateResponse
from ...types.eval_retrieve_response import EvalRetrieveResponse
from ...types.shared_params.metadata import Metadata

__all__ = ["Evals", "AsyncEvals"]


class Evals(SyncAPIResource):
    @cached_property
    def runs(self) -> Runs:
        return Runs(self._client)

    @cached_property
    def with_raw_response(self) -> EvalsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return EvalsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EvalsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return EvalsWithStreamingResponse(self)

    def create(
        self,
        *,
        data_source_config: eval_create_params.DataSourceConfig,
        testing_criteria: Iterable[eval_create_params.TestingCriterion],
        metadata: Optional[Metadata] | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        share_with_openai: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EvalCreateResponse:
        """
        Create the structure of an evaluation that can be used to test a model's
        performance. An evaluation is a set of testing criteria and a datasource. After
        creating an evaluation, you can run it on different models and model parameters.
        We support several types of graders and datasources. For more information, see
        the [Evals guide](https://platform.openai.com/docs/guides/evals).

        Args:
          data_source_config: The configuration for the data source used for the evaluation runs.

          testing_criteria: A list of graders for all eval runs in this group.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format, and
              querying for objects via API or the dashboard.

              Keys are strings with a maximum length of 64 characters. Values are strings with
              a maximum length of 512 characters.

          name: The name of the evaluation.

          share_with_openai: Indicates whether the evaluation is shared with OpenAI.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/evals",
            body=maybe_transform(
                {
                    "data_source_config": data_source_config,
                    "testing_criteria": testing_criteria,
                    "metadata": metadata,
                    "name": name,
                    "share_with_openai": share_with_openai,
                },
                eval_create_params.EvalCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvalCreateResponse,
        )

    def retrieve(
        self,
        eval_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EvalRetrieveResponse:
        """
        Get an evaluation by ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not eval_id:
            raise ValueError(f"Expected a non-empty value for `eval_id` but received {eval_id!r}")
        return self._get(
            f"/evals/{eval_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvalRetrieveResponse,
        )

    def update(
        self,
        eval_id: str,
        *,
        metadata: Optional[Metadata] | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EvalUpdateResponse:
        """
        Update certain properties of an evaluation.

        Args:
          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format, and
              querying for objects via API or the dashboard.

              Keys are strings with a maximum length of 64 characters. Values are strings with
              a maximum length of 512 characters.

          name: Rename the evaluation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not eval_id:
            raise ValueError(f"Expected a non-empty value for `eval_id` but received {eval_id!r}")
        return self._post(
            f"/evals/{eval_id}",
            body=maybe_transform(
                {
                    "metadata": metadata,
                    "name": name,
                },
                eval_update_params.EvalUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvalUpdateResponse,
        )

    def list(
        self,
        *,
        after: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        order_by: Literal["created_at", "updated_at"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncCursorPage[EvalListResponse]:
        """
        List evaluations for a project.

        Args:
          after: Identifier for the last eval from the previous pagination request.

          limit: Number of evals to retrieve.

          order: Sort order for evals by timestamp. Use `asc` for ascending order or `desc` for
              descending order.

          order_by: Evals can be ordered by creation time or last updated time. Use `created_at` for
              creation time or `updated_at` for last updated time.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/evals",
            page=SyncCursorPage[EvalListResponse],
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
                        "order_by": order_by,
                    },
                    eval_list_params.EvalListParams,
                ),
            ),
            model=EvalListResponse,
        )

    def delete(
        self,
        eval_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EvalDeleteResponse:
        """
        Delete an evaluation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not eval_id:
            raise ValueError(f"Expected a non-empty value for `eval_id` but received {eval_id!r}")
        return self._delete(
            f"/evals/{eval_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvalDeleteResponse,
        )


class AsyncEvals(AsyncAPIResource):
    @cached_property
    def runs(self) -> AsyncRuns:
        return AsyncRuns(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncEvalsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncEvalsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEvalsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncEvalsWithStreamingResponse(self)

    async def create(
        self,
        *,
        data_source_config: eval_create_params.DataSourceConfig,
        testing_criteria: Iterable[eval_create_params.TestingCriterion],
        metadata: Optional[Metadata] | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        share_with_openai: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EvalCreateResponse:
        """
        Create the structure of an evaluation that can be used to test a model's
        performance. An evaluation is a set of testing criteria and a datasource. After
        creating an evaluation, you can run it on different models and model parameters.
        We support several types of graders and datasources. For more information, see
        the [Evals guide](https://platform.openai.com/docs/guides/evals).

        Args:
          data_source_config: The configuration for the data source used for the evaluation runs.

          testing_criteria: A list of graders for all eval runs in this group.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format, and
              querying for objects via API or the dashboard.

              Keys are strings with a maximum length of 64 characters. Values are strings with
              a maximum length of 512 characters.

          name: The name of the evaluation.

          share_with_openai: Indicates whether the evaluation is shared with OpenAI.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/evals",
            body=await async_maybe_transform(
                {
                    "data_source_config": data_source_config,
                    "testing_criteria": testing_criteria,
                    "metadata": metadata,
                    "name": name,
                    "share_with_openai": share_with_openai,
                },
                eval_create_params.EvalCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvalCreateResponse,
        )

    async def retrieve(
        self,
        eval_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EvalRetrieveResponse:
        """
        Get an evaluation by ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not eval_id:
            raise ValueError(f"Expected a non-empty value for `eval_id` but received {eval_id!r}")
        return await self._get(
            f"/evals/{eval_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvalRetrieveResponse,
        )

    async def update(
        self,
        eval_id: str,
        *,
        metadata: Optional[Metadata] | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EvalUpdateResponse:
        """
        Update certain properties of an evaluation.

        Args:
          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format, and
              querying for objects via API or the dashboard.

              Keys are strings with a maximum length of 64 characters. Values are strings with
              a maximum length of 512 characters.

          name: Rename the evaluation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not eval_id:
            raise ValueError(f"Expected a non-empty value for `eval_id` but received {eval_id!r}")
        return await self._post(
            f"/evals/{eval_id}",
            body=await async_maybe_transform(
                {
                    "metadata": metadata,
                    "name": name,
                },
                eval_update_params.EvalUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvalUpdateResponse,
        )

    def list(
        self,
        *,
        after: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        order_by: Literal["created_at", "updated_at"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[EvalListResponse, AsyncCursorPage[EvalListResponse]]:
        """
        List evaluations for a project.

        Args:
          after: Identifier for the last eval from the previous pagination request.

          limit: Number of evals to retrieve.

          order: Sort order for evals by timestamp. Use `asc` for ascending order or `desc` for
              descending order.

          order_by: Evals can be ordered by creation time or last updated time. Use `created_at` for
              creation time or `updated_at` for last updated time.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/evals",
            page=AsyncCursorPage[EvalListResponse],
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
                        "order_by": order_by,
                    },
                    eval_list_params.EvalListParams,
                ),
            ),
            model=EvalListResponse,
        )

    async def delete(
        self,
        eval_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EvalDeleteResponse:
        """
        Delete an evaluation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not eval_id:
            raise ValueError(f"Expected a non-empty value for `eval_id` but received {eval_id!r}")
        return await self._delete(
            f"/evals/{eval_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EvalDeleteResponse,
        )


class EvalsWithRawResponse:
    def __init__(self, evals: Evals) -> None:
        self._evals = evals

        self.create = _legacy_response.to_raw_response_wrapper(
            evals.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            evals.retrieve,
        )
        self.update = _legacy_response.to_raw_response_wrapper(
            evals.update,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            evals.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            evals.delete,
        )

    @cached_property
    def runs(self) -> RunsWithRawResponse:
        return RunsWithRawResponse(self._evals.runs)


class AsyncEvalsWithRawResponse:
    def __init__(self, evals: AsyncEvals) -> None:
        self._evals = evals

        self.create = _legacy_response.async_to_raw_response_wrapper(
            evals.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            evals.retrieve,
        )
        self.update = _legacy_response.async_to_raw_response_wrapper(
            evals.update,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            evals.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            evals.delete,
        )

    @cached_property
    def runs(self) -> AsyncRunsWithRawResponse:
        return AsyncRunsWithRawResponse(self._evals.runs)


class EvalsWithStreamingResponse:
    def __init__(self, evals: Evals) -> None:
        self._evals = evals

        self.create = to_streamed_response_wrapper(
            evals.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            evals.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            evals.update,
        )
        self.list = to_streamed_response_wrapper(
            evals.list,
        )
        self.delete = to_streamed_response_wrapper(
            evals.delete,
        )

    @cached_property
    def runs(self) -> RunsWithStreamingResponse:
        return RunsWithStreamingResponse(self._evals.runs)


class AsyncEvalsWithStreamingResponse:
    def __init__(self, evals: AsyncEvals) -> None:
        self._evals = evals

        self.create = async_to_streamed_response_wrapper(
            evals.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            evals.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            evals.update,
        )
        self.list = async_to_streamed_response_wrapper(
            evals.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            evals.delete,
        )

    @cached_property
    def runs(self) -> AsyncRunsWithStreamingResponse:
        return AsyncRunsWithStreamingResponse(self._evals.runs)
