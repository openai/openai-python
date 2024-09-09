# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from ..... import _legacy_response
from ....._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ....._utils import (
    maybe_transform,
    async_maybe_transform,
)
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from .....pagination import SyncCursorPage, AsyncCursorPage
from ....._base_client import AsyncPaginator, make_request_options
from .....types.beta.threads.runs import step_list_params, step_retrieve_params
from .....types.beta.threads.runs.run_step import RunStep
from .....types.beta.threads.runs.run_step_include import RunStepInclude

__all__ = ["Steps", "AsyncSteps"]


class Steps(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> StepsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return StepsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> StepsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return StepsWithStreamingResponse(self)

    def retrieve(
        self,
        step_id: str,
        *,
        thread_id: str,
        run_id: str,
        include: List[RunStepInclude] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RunStep:
        """
        Retrieves a run step.

        Args:
          include: A list of additional fields to include in the response. Currently the only
              supported value is `step_details.tool_calls[*].file_search.results[*].content`
              to fetch the file search result content.

              See the
              [file search tool documentation](https://platform.openai.com/docs/assistants/tools/file-search/customizing-file-search-settings)
              for more information.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        if not step_id:
            raise ValueError(f"Expected a non-empty value for `step_id` but received {step_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return self._get(
            f"/threads/{thread_id}/runs/{run_id}/steps/{step_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"include": include}, step_retrieve_params.StepRetrieveParams),
            ),
            cast_to=RunStep,
        )

    def list(
        self,
        run_id: str,
        *,
        thread_id: str,
        after: str | NotGiven = NOT_GIVEN,
        before: str | NotGiven = NOT_GIVEN,
        include: List[RunStepInclude] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncCursorPage[RunStep]:
        """
        Returns a list of run steps belonging to a run.

        Args:
          after: A cursor for use in pagination. `after` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include after=obj_foo in order to
              fetch the next page of the list.

          before: A cursor for use in pagination. `before` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include before=obj_foo in order to
              fetch the previous page of the list.

          include: A list of additional fields to include in the response. Currently the only
              supported value is `step_details.tool_calls[*].file_search.results[*].content`
              to fetch the file search result content.

              See the
              [file search tool documentation](https://platform.openai.com/docs/assistants/tools/file-search/customizing-file-search-settings)
              for more information.

          limit: A limit on the number of objects to be returned. Limit can range between 1 and
              100, and the default is 20.

          order: Sort order by the `created_at` timestamp of the objects. `asc` for ascending
              order and `desc` for descending order.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return self._get_api_list(
            f"/threads/{thread_id}/runs/{run_id}/steps",
            page=SyncCursorPage[RunStep],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "before": before,
                        "include": include,
                        "limit": limit,
                        "order": order,
                    },
                    step_list_params.StepListParams,
                ),
            ),
            model=RunStep,
        )


class AsyncSteps(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncStepsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncStepsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncStepsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncStepsWithStreamingResponse(self)

    async def retrieve(
        self,
        step_id: str,
        *,
        thread_id: str,
        run_id: str,
        include: List[RunStepInclude] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RunStep:
        """
        Retrieves a run step.

        Args:
          include: A list of additional fields to include in the response. Currently the only
              supported value is `step_details.tool_calls[*].file_search.results[*].content`
              to fetch the file search result content.

              See the
              [file search tool documentation](https://platform.openai.com/docs/assistants/tools/file-search/customizing-file-search-settings)
              for more information.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        if not step_id:
            raise ValueError(f"Expected a non-empty value for `step_id` but received {step_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return await self._get(
            f"/threads/{thread_id}/runs/{run_id}/steps/{step_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"include": include}, step_retrieve_params.StepRetrieveParams),
            ),
            cast_to=RunStep,
        )

    def list(
        self,
        run_id: str,
        *,
        thread_id: str,
        after: str | NotGiven = NOT_GIVEN,
        before: str | NotGiven = NOT_GIVEN,
        include: List[RunStepInclude] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[RunStep, AsyncCursorPage[RunStep]]:
        """
        Returns a list of run steps belonging to a run.

        Args:
          after: A cursor for use in pagination. `after` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include after=obj_foo in order to
              fetch the next page of the list.

          before: A cursor for use in pagination. `before` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include before=obj_foo in order to
              fetch the previous page of the list.

          include: A list of additional fields to include in the response. Currently the only
              supported value is `step_details.tool_calls[*].file_search.results[*].content`
              to fetch the file search result content.

              See the
              [file search tool documentation](https://platform.openai.com/docs/assistants/tools/file-search/customizing-file-search-settings)
              for more information.

          limit: A limit on the number of objects to be returned. Limit can range between 1 and
              100, and the default is 20.

          order: Sort order by the `created_at` timestamp of the objects. `asc` for ascending
              order and `desc` for descending order.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return self._get_api_list(
            f"/threads/{thread_id}/runs/{run_id}/steps",
            page=AsyncCursorPage[RunStep],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "before": before,
                        "include": include,
                        "limit": limit,
                        "order": order,
                    },
                    step_list_params.StepListParams,
                ),
            ),
            model=RunStep,
        )


class StepsWithRawResponse:
    def __init__(self, steps: Steps) -> None:
        self._steps = steps

        self.retrieve = _legacy_response.to_raw_response_wrapper(
            steps.retrieve,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            steps.list,
        )


class AsyncStepsWithRawResponse:
    def __init__(self, steps: AsyncSteps) -> None:
        self._steps = steps

        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            steps.retrieve,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            steps.list,
        )


class StepsWithStreamingResponse:
    def __init__(self, steps: Steps) -> None:
        self._steps = steps

        self.retrieve = to_streamed_response_wrapper(
            steps.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            steps.list,
        )


class AsyncStepsWithStreamingResponse:
    def __init__(self, steps: AsyncSteps) -> None:
        self._steps = steps

        self.retrieve = async_to_streamed_response_wrapper(
            steps.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            steps.list,
        )
