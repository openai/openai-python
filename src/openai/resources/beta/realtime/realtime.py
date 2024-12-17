# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .sessions import (
    Sessions,
    AsyncSessions,
    SessionsWithRawResponse,
    AsyncSessionsWithRawResponse,
    SessionsWithStreamingResponse,
    AsyncSessionsWithStreamingResponse,
)
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["Realtime", "AsyncRealtime"]


class Realtime(SyncAPIResource):
    @cached_property
    def sessions(self) -> Sessions:
        return Sessions(self._client)

    @cached_property
    def with_raw_response(self) -> RealtimeWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return RealtimeWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RealtimeWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return RealtimeWithStreamingResponse(self)


class AsyncRealtime(AsyncAPIResource):
    @cached_property
    def sessions(self) -> AsyncSessions:
        return AsyncSessions(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncRealtimeWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRealtimeWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRealtimeWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncRealtimeWithStreamingResponse(self)


class RealtimeWithRawResponse:
    def __init__(self, realtime: Realtime) -> None:
        self._realtime = realtime

    @cached_property
    def sessions(self) -> SessionsWithRawResponse:
        return SessionsWithRawResponse(self._realtime.sessions)


class AsyncRealtimeWithRawResponse:
    def __init__(self, realtime: AsyncRealtime) -> None:
        self._realtime = realtime

    @cached_property
    def sessions(self) -> AsyncSessionsWithRawResponse:
        return AsyncSessionsWithRawResponse(self._realtime.sessions)


class RealtimeWithStreamingResponse:
    def __init__(self, realtime: Realtime) -> None:
        self._realtime = realtime

    @cached_property
    def sessions(self) -> SessionsWithStreamingResponse:
        return SessionsWithStreamingResponse(self._realtime.sessions)


class AsyncRealtimeWithStreamingResponse:
    def __init__(self, realtime: AsyncRealtime) -> None:
        self._realtime = realtime

    @cached_property
    def sessions(self) -> AsyncSessionsWithStreamingResponse:
        return AsyncSessionsWithStreamingResponse(self._realtime.sessions)
