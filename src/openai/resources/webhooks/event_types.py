# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx2

from ... import _legacy_response
from ..._types import Body, Query, Headers, NotGiven, not_given
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ..._base_client import make_request_options
from ...types.webhooks.webhook_event_type_list import WebhookEventTypeList

__all__ = ["EventTypes", "AsyncEventTypes"]


class EventTypes(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> EventTypesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return EventTypesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EventTypesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return EventTypesWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> WebhookEventTypeList:
        """Returns webhook event types visible to the authenticated project."""
        return self._get(
            "/webhook_event_types",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=WebhookEventTypeList,
        )


class AsyncEventTypes(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncEventTypesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncEventTypesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEventTypesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncEventTypesWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> WebhookEventTypeList:
        """Returns webhook event types visible to the authenticated project."""
        return await self._get(
            "/webhook_event_types",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=WebhookEventTypeList,
        )


class EventTypesWithRawResponse:
    def __init__(self, event_types: EventTypes) -> None:
        self._event_types = event_types

        self.list = _legacy_response.to_raw_response_wrapper(
            event_types.list,
        )


class AsyncEventTypesWithRawResponse:
    def __init__(self, event_types: AsyncEventTypes) -> None:
        self._event_types = event_types

        self.list = _legacy_response.async_to_raw_response_wrapper(
            event_types.list,
        )


class EventTypesWithStreamingResponse:
    def __init__(self, event_types: EventTypes) -> None:
        self._event_types = event_types

        self.list = to_streamed_response_wrapper(
            event_types.list,
        )


class AsyncEventTypesWithStreamingResponse:
    def __init__(self, event_types: AsyncEventTypes) -> None:
        self._event_types = event_types

        self.list = async_to_streamed_response_wrapper(
            event_types.list,
        )
