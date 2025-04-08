# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from .... import _legacy_response
from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ....pagination import SyncCursorPage, AsyncCursorPage
from ...._base_client import AsyncPaginator, make_request_options
from ....types.evals.runs import output_item_list_params
from ....types.evals.runs.output_item_list_response import OutputItemListResponse
from ....types.evals.runs.output_item_retrieve_response import OutputItemRetrieveResponse

__all__ = ["OutputItems", "AsyncOutputItems"]


class OutputItems(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OutputItemsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return OutputItemsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OutputItemsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return OutputItemsWithStreamingResponse(self)

    def retrieve(
        self,
        output_item_id: str,
        *,
        eval_id: str,
        run_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OutputItemRetrieveResponse:
        """
        Get an evaluation run output item by ID.

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
        if not output_item_id:
            raise ValueError(f"Expected a non-empty value for `output_item_id` but received {output_item_id!r}")
        return self._get(
            f"/evals/{eval_id}/runs/{run_id}/output_items/{output_item_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OutputItemRetrieveResponse,
        )

    def list(
        self,
        run_id: str,
        *,
        eval_id: str,
        after: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        status: Literal["fail", "pass"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncCursorPage[OutputItemListResponse]:
        """
        Get a list of output items for an evaluation run.

        Args:
          after: Identifier for the last output item from the previous pagination request.

          limit: Number of output items to retrieve.

          order: Sort order for output items by timestamp. Use `asc` for ascending order or
              `desc` for descending order. Defaults to `asc`.

          status: Filter output items by status. Use `failed` to filter by failed output items or
              `pass` to filter by passed output items.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not eval_id:
            raise ValueError(f"Expected a non-empty value for `eval_id` but received {eval_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        return self._get_api_list(
            f"/evals/{eval_id}/runs/{run_id}/output_items",
            page=SyncCursorPage[OutputItemListResponse],
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
                    output_item_list_params.OutputItemListParams,
                ),
            ),
            model=OutputItemListResponse,
        )


class AsyncOutputItems(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOutputItemsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncOutputItemsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOutputItemsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncOutputItemsWithStreamingResponse(self)

    async def retrieve(
        self,
        output_item_id: str,
        *,
        eval_id: str,
        run_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OutputItemRetrieveResponse:
        """
        Get an evaluation run output item by ID.

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
        if not output_item_id:
            raise ValueError(f"Expected a non-empty value for `output_item_id` but received {output_item_id!r}")
        return await self._get(
            f"/evals/{eval_id}/runs/{run_id}/output_items/{output_item_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OutputItemRetrieveResponse,
        )

    def list(
        self,
        run_id: str,
        *,
        eval_id: str,
        after: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        status: Literal["fail", "pass"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[OutputItemListResponse, AsyncCursorPage[OutputItemListResponse]]:
        """
        Get a list of output items for an evaluation run.

        Args:
          after: Identifier for the last output item from the previous pagination request.

          limit: Number of output items to retrieve.

          order: Sort order for output items by timestamp. Use `asc` for ascending order or
              `desc` for descending order. Defaults to `asc`.

          status: Filter output items by status. Use `failed` to filter by failed output items or
              `pass` to filter by passed output items.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not eval_id:
            raise ValueError(f"Expected a non-empty value for `eval_id` but received {eval_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        return self._get_api_list(
            f"/evals/{eval_id}/runs/{run_id}/output_items",
            page=AsyncCursorPage[OutputItemListResponse],
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
                    output_item_list_params.OutputItemListParams,
                ),
            ),
            model=OutputItemListResponse,
        )


class OutputItemsWithRawResponse:
    def __init__(self, output_items: OutputItems) -> None:
        self._output_items = output_items

        self.retrieve = _legacy_response.to_raw_response_wrapper(
            output_items.retrieve,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            output_items.list,
        )


class AsyncOutputItemsWithRawResponse:
    def __init__(self, output_items: AsyncOutputItems) -> None:
        self._output_items = output_items

        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            output_items.retrieve,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            output_items.list,
        )


class OutputItemsWithStreamingResponse:
    def __init__(self, output_items: OutputItems) -> None:
        self._output_items = output_items

        self.retrieve = to_streamed_response_wrapper(
            output_items.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            output_items.list,
        )


class AsyncOutputItemsWithStreamingResponse:
    def __init__(self, output_items: AsyncOutputItems) -> None:
        self._output_items = output_items

        self.retrieve = async_to_streamed_response_wrapper(
            output_items.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            output_items.list,
        )
