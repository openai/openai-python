# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx2

from ..... import _legacy_response
from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ....._utils import path_template, maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from .....pagination import SyncCursorPage, AsyncCursorPage
from ....._base_client import AsyncPaginator, make_request_options
from .....types.beta.agents.sessions import trace_list_params
from .....types.beta.agents.sessions.session_trace import SessionTrace

__all__ = ["Traces", "AsyncTraces"]


class Traces(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TracesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return TracesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TracesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return TracesWithStreamingResponse(self)

    def list(
        self,
        session_id: str,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPage[SessionTrace]:
        """
        Lists published root-turn traces as OTLP JSON, ordered by turn creation time and
        ID. Unpublished traces are skipped. Each page returns data available when read;
        it does not wait for late traces. Trace reads and the JSON response are limited
        to 16 MiB per request. If the limit is exceeded, request fewer traces.

        Args:
          after: Return resources after this resource ID in the selected order.

          limit: The maximum number of resources to return, between 1 and 100. Defaults to 20.

          order: The order in which resources are returned. Defaults to `desc`.

              - `asc` - Returns resources in ascending order.
              - `desc` - Returns resources in descending order.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get_api_list(
            path_template("/agents/sessions/{session_id}/traces", session_id=session_id),
            page=SyncCursorPage[SessionTrace],
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
                    },
                    trace_list_params.TraceListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=SessionTrace,
        )


class AsyncTraces(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTracesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTracesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTracesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncTracesWithStreamingResponse(self)

    def list(
        self,
        session_id: str,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[SessionTrace, AsyncCursorPage[SessionTrace]]:
        """
        Lists published root-turn traces as OTLP JSON, ordered by turn creation time and
        ID. Unpublished traces are skipped. Each page returns data available when read;
        it does not wait for late traces. Trace reads and the JSON response are limited
        to 16 MiB per request. If the limit is exceeded, request fewer traces.

        Args:
          after: Return resources after this resource ID in the selected order.

          limit: The maximum number of resources to return, between 1 and 100. Defaults to 20.

          order: The order in which resources are returned. Defaults to `desc`.

              - `asc` - Returns resources in ascending order.
              - `desc` - Returns resources in descending order.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get_api_list(
            path_template("/agents/sessions/{session_id}/traces", session_id=session_id),
            page=AsyncCursorPage[SessionTrace],
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
                    },
                    trace_list_params.TraceListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=SessionTrace,
        )


class TracesWithRawResponse:
    def __init__(self, traces: Traces) -> None:
        self._traces = traces

        self.list = _legacy_response.to_raw_response_wrapper(
            traces.list,
        )


class AsyncTracesWithRawResponse:
    def __init__(self, traces: AsyncTraces) -> None:
        self._traces = traces

        self.list = _legacy_response.async_to_raw_response_wrapper(
            traces.list,
        )


class TracesWithStreamingResponse:
    def __init__(self, traces: Traces) -> None:
        self._traces = traces

        self.list = to_streamed_response_wrapper(
            traces.list,
        )


class AsyncTracesWithStreamingResponse:
    def __init__(self, traces: AsyncTraces) -> None:
        self._traces = traces

        self.list = async_to_streamed_response_wrapper(
            traces.list,
        )
