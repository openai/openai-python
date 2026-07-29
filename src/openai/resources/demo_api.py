# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Literal

import httpx

from .. import _legacy_response
from ..types import demo_api_list_params, demo_api_create_params, demo_api_retrieve_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import path_template, maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from .._base_client import make_request_options
from ..types.demo_widget import DemoWidget
from ..types.demo_api_list_response import DemoAPIListResponse
from ..types.demo_widget_configuration_param import DemoWidgetConfigurationParam

__all__ = ["DemoAPI", "AsyncDemoAPI"]


class DemoAPI(SyncAPIResource):
    """Manage demo widgets used to test SDK generation."""

    @cached_property
    def with_raw_response(self) -> DemoAPIWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return DemoAPIWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DemoAPIWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return DemoAPIWithStreamingResponse(self)

    def create(
        self,
        *,
        configuration: DemoWidgetConfigurationParam,
        name: str,
        metadata: Dict[str, str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DemoWidget:
        """
        Creates a demo API widget.

        Args:
          configuration: Demo-only configuration applied to a widget.

          name: The human-readable name of the widget.

          metadata: Optional metadata attached to the widget.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/demo_api/widgets",
            body=maybe_transform(
                {
                    "configuration": configuration,
                    "name": name,
                    "metadata": metadata,
                },
                demo_api_create_params.DemoAPICreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=DemoWidget,
        )

    def retrieve(
        self,
        widget_id: str,
        *,
        include_history: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DemoWidget:
        """
        Retrieves a demo API widget.

        Args:
          include_history: Whether to include the widget's status history.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not widget_id:
            raise ValueError(f"Expected a non-empty value for `widget_id` but received {widget_id!r}")
        return self._get(
            path_template("/demo_api/widgets/{widget_id}", widget_id=widget_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"include_history": include_history}, demo_api_retrieve_params.DemoAPIRetrieveParams
                ),
                security={"bearer_auth": True},
            ),
            cast_to=DemoWidget,
        )

    def list(
        self,
        *,
        limit: int | Omit = omit,
        status: Literal["pending", "active", "archived"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DemoAPIListResponse:
        """
        Lists demo API widgets.

        Args:
          limit: The maximum number of widgets to return.

          status: Filters widgets by their current status.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/demo_api/widgets",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "status": status,
                    },
                    demo_api_list_params.DemoAPIListParams,
                ),
                security={"bearer_auth": True},
            ),
            cast_to=DemoAPIListResponse,
        )


class AsyncDemoAPI(AsyncAPIResource):
    """Manage demo widgets used to test SDK generation."""

    @cached_property
    def with_raw_response(self) -> AsyncDemoAPIWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDemoAPIWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDemoAPIWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncDemoAPIWithStreamingResponse(self)

    async def create(
        self,
        *,
        configuration: DemoWidgetConfigurationParam,
        name: str,
        metadata: Dict[str, str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DemoWidget:
        """
        Creates a demo API widget.

        Args:
          configuration: Demo-only configuration applied to a widget.

          name: The human-readable name of the widget.

          metadata: Optional metadata attached to the widget.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/demo_api/widgets",
            body=await async_maybe_transform(
                {
                    "configuration": configuration,
                    "name": name,
                    "metadata": metadata,
                },
                demo_api_create_params.DemoAPICreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=DemoWidget,
        )

    async def retrieve(
        self,
        widget_id: str,
        *,
        include_history: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DemoWidget:
        """
        Retrieves a demo API widget.

        Args:
          include_history: Whether to include the widget's status history.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not widget_id:
            raise ValueError(f"Expected a non-empty value for `widget_id` but received {widget_id!r}")
        return await self._get(
            path_template("/demo_api/widgets/{widget_id}", widget_id=widget_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"include_history": include_history}, demo_api_retrieve_params.DemoAPIRetrieveParams
                ),
                security={"bearer_auth": True},
            ),
            cast_to=DemoWidget,
        )

    async def list(
        self,
        *,
        limit: int | Omit = omit,
        status: Literal["pending", "active", "archived"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DemoAPIListResponse:
        """
        Lists demo API widgets.

        Args:
          limit: The maximum number of widgets to return.

          status: Filters widgets by their current status.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/demo_api/widgets",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "limit": limit,
                        "status": status,
                    },
                    demo_api_list_params.DemoAPIListParams,
                ),
                security={"bearer_auth": True},
            ),
            cast_to=DemoAPIListResponse,
        )


class DemoAPIWithRawResponse:
    def __init__(self, demo_api: DemoAPI) -> None:
        self._demo_api = demo_api

        self.create = _legacy_response.to_raw_response_wrapper(
            demo_api.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            demo_api.retrieve,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            demo_api.list,
        )


class AsyncDemoAPIWithRawResponse:
    def __init__(self, demo_api: AsyncDemoAPI) -> None:
        self._demo_api = demo_api

        self.create = _legacy_response.async_to_raw_response_wrapper(
            demo_api.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            demo_api.retrieve,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            demo_api.list,
        )


class DemoAPIWithStreamingResponse:
    def __init__(self, demo_api: DemoAPI) -> None:
        self._demo_api = demo_api

        self.create = to_streamed_response_wrapper(
            demo_api.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            demo_api.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            demo_api.list,
        )


class AsyncDemoAPIWithStreamingResponse:
    def __init__(self, demo_api: AsyncDemoAPI) -> None:
        self._demo_api = demo_api

        self.create = async_to_streamed_response_wrapper(
            demo_api.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            demo_api.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            demo_api.list,
        )
