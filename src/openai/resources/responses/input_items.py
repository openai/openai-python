# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, cast
from typing_extensions import Literal

import httpx

from ... import _legacy_response
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ...pagination import SyncCursorPage, AsyncCursorPage
from ..._base_client import AsyncPaginator, make_request_options
from ...types.responses import input_item_list_params
from ...types.responses.response_item_list import Data

__all__ = ["InputItems", "AsyncInputItems"]


class InputItems(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> InputItemsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return InputItemsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> InputItemsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return InputItemsWithStreamingResponse(self)

    def list(
        self,
        response_id: str,
        *,
        after: str | NotGiven = NOT_GIVEN,
        before: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncCursorPage[Data]:
        """
        Returns a list of input items for a given response.

        Args:
          after: An item ID to list items after, used in pagination.

          before: An item ID to list items before, used in pagination.

          limit: A limit on the number of objects to be returned. Limit can range between 1 and
              100, and the default is 20.

          order: The order to return the input items in. Default is `asc`.

              - `asc`: Return the input items in ascending order.
              - `desc`: Return the input items in descending order.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not response_id:
            raise ValueError(f"Expected a non-empty value for `response_id` but received {response_id!r}")
        return self._get_api_list(
            f"/responses/{response_id}/input_items",
            page=SyncCursorPage[Data],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "before": before,
                        "limit": limit,
                        "order": order,
                    },
                    input_item_list_params.InputItemListParams,
                ),
            ),
            model=cast(Any, Data),  # Union types cannot be passed in as arguments in the type system
        )


class AsyncInputItems(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncInputItemsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncInputItemsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncInputItemsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncInputItemsWithStreamingResponse(self)

    def list(
        self,
        response_id: str,
        *,
        after: str | NotGiven = NOT_GIVEN,
        before: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[Data, AsyncCursorPage[Data]]:
        """
        Returns a list of input items for a given response.

        Args:
          after: An item ID to list items after, used in pagination.

          before: An item ID to list items before, used in pagination.

          limit: A limit on the number of objects to be returned. Limit can range between 1 and
              100, and the default is 20.

          order: The order to return the input items in. Default is `asc`.

              - `asc`: Return the input items in ascending order.
              - `desc`: Return the input items in descending order.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not response_id:
            raise ValueError(f"Expected a non-empty value for `response_id` but received {response_id!r}")
        return self._get_api_list(
            f"/responses/{response_id}/input_items",
            page=AsyncCursorPage[Data],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "before": before,
                        "limit": limit,
                        "order": order,
                    },
                    input_item_list_params.InputItemListParams,
                ),
            ),
            model=cast(Any, Data),  # Union types cannot be passed in as arguments in the type system
        )


class InputItemsWithRawResponse:
    def __init__(self, input_items: InputItems) -> None:
        self._input_items = input_items

        self.list = _legacy_response.to_raw_response_wrapper(
            input_items.list,
        )


class AsyncInputItemsWithRawResponse:
    def __init__(self, input_items: AsyncInputItems) -> None:
        self._input_items = input_items

        self.list = _legacy_response.async_to_raw_response_wrapper(
            input_items.list,
        )


class InputItemsWithStreamingResponse:
    def __init__(self, input_items: InputItems) -> None:
        self._input_items = input_items

        self.list = to_streamed_response_wrapper(
            input_items.list,
        )


class AsyncInputItemsWithStreamingResponse:
    def __init__(self, input_items: AsyncInputItems) -> None:
        self._input_items = input_items

        self.list = async_to_streamed_response_wrapper(
            input_items.list,
        )
