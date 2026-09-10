# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, Iterable, cast

import httpx2

from ..... import _legacy_response
from ....._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
from ....._utils import path_template, maybe_transform, strip_not_given, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ....._streaming import Stream, AsyncStream
from ....._base_client import make_request_options
from .....types.beta.agents.sessions import event_create_params
from .....types.beta.agent_session_event import AgentSessionEvent
from .....types.beta.agent_session_input_param import AgentSessionInputParam

__all__ = ["Events", "AsyncEvents"]


class Events(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> EventsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return EventsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EventsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return EventsWithStreamingResponse(self)

    def create(
        self,
        session_id: str,
        *,
        events: Iterable[AgentSessionInputParam],
        idempotency_key: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Submits message, cancellation, or tool-result events to a managed agent session.
        See
        [session events](https://developers.openai.com/api/docs/guides/agents-api/sessions/events).

        Args:
          events: The input events to submit to the session.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {**strip_not_given({"Idempotency-Key": idempotency_key}), **(extra_headers or {})}
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._post(
            path_template("/agents/sessions/{session_id}/events", session_id=session_id),
            body=maybe_transform({"events": events}, event_create_params.EventCreateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=NoneType,
        )

    def stream(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Stream[AgentSessionEvent]:
        """Streams live events for an agent session.

        See
        [session events](https://developers.openai.com/api/docs/guides/agents-api/sessions/events).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "text/event-stream", **(extra_headers or {})}
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get(
            path_template("/agents/sessions/{session_id}/events", session_id=session_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=cast(Any, AgentSessionEvent),  # Union types cannot be passed in as arguments in the type system
            stream=True,
            stream_cls=Stream[AgentSessionEvent],
        )


class AsyncEvents(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncEventsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncEventsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEventsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncEventsWithStreamingResponse(self)

    async def create(
        self,
        session_id: str,
        *,
        events: Iterable[AgentSessionInputParam],
        idempotency_key: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Submits message, cancellation, or tool-result events to a managed agent session.
        See
        [session events](https://developers.openai.com/api/docs/guides/agents-api/sessions/events).

        Args:
          events: The input events to submit to the session.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        extra_headers = {**strip_not_given({"Idempotency-Key": idempotency_key}), **(extra_headers or {})}
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._post(
            path_template("/agents/sessions/{session_id}/events", session_id=session_id),
            body=await async_maybe_transform({"events": events}, event_create_params.EventCreateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=NoneType,
        )

    async def stream(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AsyncStream[AgentSessionEvent]:
        """Streams live events for an agent session.

        See
        [session events](https://developers.openai.com/api/docs/guides/agents-api/sessions/events).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "text/event-stream", **(extra_headers or {})}
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._get(
            path_template("/agents/sessions/{session_id}/events", session_id=session_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=cast(Any, AgentSessionEvent),  # Union types cannot be passed in as arguments in the type system
            stream=True,
            stream_cls=AsyncStream[AgentSessionEvent],
        )


class EventsWithRawResponse:
    def __init__(self, events: Events) -> None:
        self._events = events

        self.create = _legacy_response.to_raw_response_wrapper(
            events.create,
        )
        self.stream = _legacy_response.to_raw_response_wrapper(
            events.stream,
        )


class AsyncEventsWithRawResponse:
    def __init__(self, events: AsyncEvents) -> None:
        self._events = events

        self.create = _legacy_response.async_to_raw_response_wrapper(
            events.create,
        )
        self.stream = _legacy_response.async_to_raw_response_wrapper(
            events.stream,
        )


class EventsWithStreamingResponse:
    def __init__(self, events: Events) -> None:
        self._events = events

        self.create = to_streamed_response_wrapper(
            events.create,
        )
        self.stream = to_streamed_response_wrapper(
            events.stream,
        )


class AsyncEventsWithStreamingResponse:
    def __init__(self, events: AsyncEvents) -> None:
        self._events = events

        self.create = async_to_streamed_response_wrapper(
            events.create,
        )
        self.stream = async_to_streamed_response_wrapper(
            events.stream,
        )
