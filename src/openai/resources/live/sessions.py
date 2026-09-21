# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx2

from ... import _legacy_response
from ..._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
from ..._utils import path_template, maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
    to_streamed_response_wrapper,
    async_to_streamed_response_wrapper,
    to_custom_streamed_response_wrapper,
    async_to_custom_streamed_response_wrapper,
)
from ...types.live import (
    session_fork_params,
    session_refer_params,
    session_accept_params,
    session_reject_params,
)
from ..._base_client import make_request_options
from ...types.live.session_fork_response import SessionForkResponse
from ...types.live.media_session_fork_config_param import MediaSessionForkConfigParam

__all__ = ["Sessions", "AsyncSessions"]


class Sessions(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SessionsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return SessionsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SessionsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return SessionsWithStreamingResponse(self)

    def accept(
        self,
        session_id: str,
        *,
        session: session_accept_params.Session,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> None:
        """Accept an incoming SIP call.

        Supply session with type live, the model, and
        startup configuration. Before accepting calls, follow the
        [Live prompting guide](https://developers.openai.com/api/docs/guides/live-prompting)
        to write frontend conversation instructions and a separate backend prompt. SIP
        media format is negotiated; omit audio.format.

        Args:
          session: Model and startup configuration for the Live session that answers the incoming
              SIP call.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            path_template("/live/sessions/{session_id}/accept", session_id=session_id),
            body=maybe_transform({"session": session}, session_accept_params.SessionAcceptParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=NoneType,
        )

    def download_recording(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> _legacy_response.HttpxBinaryResponseContent:
        """
        Get Live session content

        Args:
          session_id: The ID of the stored Live session to download. Use the session ID returned when
              the session started with storage enabled.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "application/binary", **(extra_headers or {})}
        return self._get(
            path_template("/live/sessions/{session_id}/content", session_id=session_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=_legacy_response.HttpxBinaryResponseContent,
        )

    def fork(
        self,
        session_id: str,
        *,
        transport: session_fork_params.Transport,
        session: MediaSessionForkConfigParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SessionForkResponse:
        """
        Fork a stored Live session onto a new WebRTC connection.

        Args:
          transport: WebRTC transport with an SDP offer for the new connection to the forked session.

          session: Optional configuration overrides for the new Live session. Omit this object or
              send an empty object to inherit the stored session's settings.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return self._post(
            path_template("/live/sessions/{session_id}/fork", session_id=session_id),
            body=maybe_transform(
                {
                    "transport": transport,
                    "session": session,
                },
                session_fork_params.SessionForkParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=SessionForkResponse,
        )

    def hangup(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        End a SIP call identified by session_id.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            path_template("/live/sessions/{session_id}/hangup", session_id=session_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=NoneType,
        )

    def refer(
        self,
        session_id: str,
        *,
        target_uri: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> None:
        """Transfer a SIP call to another destination.

        Supply a nonblank target_uri for the
        SIP Refer-To header.

        Args:
          target_uri: Nonblank URI for the SIP Refer-To header, such as tel:+14155550123 or
              sip:agent@example.com.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            path_template("/live/sessions/{session_id}/refer", session_id=session_id),
            body=maybe_transform({"target_uri": target_uri}, session_refer_params.SessionReferParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=NoneType,
        )

    def reject(
        self,
        session_id: str,
        *,
        status_code: int,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> None:
        """Reject an incoming SIP call.

        Send a required SIP rejection status_code between
        300 and 699.

        Args:
          status_code: SIP rejection status sent to the caller. This field is required.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            path_template("/live/sessions/{session_id}/reject", session_id=session_id),
            body=maybe_transform({"status_code": status_code}, session_reject_params.SessionRejectParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=NoneType,
        )


class AsyncSessions(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSessionsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSessionsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSessionsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncSessionsWithStreamingResponse(self)

    async def accept(
        self,
        session_id: str,
        *,
        session: session_accept_params.Session,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> None:
        """Accept an incoming SIP call.

        Supply session with type live, the model, and
        startup configuration. Before accepting calls, follow the
        [Live prompting guide](https://developers.openai.com/api/docs/guides/live-prompting)
        to write frontend conversation instructions and a separate backend prompt. SIP
        media format is negotiated; omit audio.format.

        Args:
          session: Model and startup configuration for the Live session that answers the incoming
              SIP call.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            path_template("/live/sessions/{session_id}/accept", session_id=session_id),
            body=await async_maybe_transform({"session": session}, session_accept_params.SessionAcceptParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=NoneType,
        )

    async def download_recording(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> _legacy_response.HttpxBinaryResponseContent:
        """
        Get Live session content

        Args:
          session_id: The ID of the stored Live session to download. Use the session ID returned when
              the session started with storage enabled.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "application/binary", **(extra_headers or {})}
        return await self._get(
            path_template("/live/sessions/{session_id}/content", session_id=session_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=_legacy_response.HttpxBinaryResponseContent,
        )

    async def fork(
        self,
        session_id: str,
        *,
        transport: session_fork_params.Transport,
        session: MediaSessionForkConfigParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SessionForkResponse:
        """
        Fork a stored Live session onto a new WebRTC connection.

        Args:
          transport: WebRTC transport with an SDP offer for the new connection to the forked session.

          session: Optional configuration overrides for the new Live session. Omit this object or
              send an empty object to inherit the stored session's settings.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return await self._post(
            path_template("/live/sessions/{session_id}/fork", session_id=session_id),
            body=await async_maybe_transform(
                {
                    "transport": transport,
                    "session": session,
                },
                session_fork_params.SessionForkParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=SessionForkResponse,
        )

    async def hangup(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        End a SIP call identified by session_id.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            path_template("/live/sessions/{session_id}/hangup", session_id=session_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=NoneType,
        )

    async def refer(
        self,
        session_id: str,
        *,
        target_uri: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> None:
        """Transfer a SIP call to another destination.

        Supply a nonblank target_uri for the
        SIP Refer-To header.

        Args:
          target_uri: Nonblank URI for the SIP Refer-To header, such as tel:+14155550123 or
              sip:agent@example.com.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            path_template("/live/sessions/{session_id}/refer", session_id=session_id),
            body=await async_maybe_transform({"target_uri": target_uri}, session_refer_params.SessionReferParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=NoneType,
        )

    async def reject(
        self,
        session_id: str,
        *,
        status_code: int,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> None:
        """Reject an incoming SIP call.

        Send a required SIP rejection status_code between
        300 and 699.

        Args:
          status_code: SIP rejection status sent to the caller. This field is required.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            path_template("/live/sessions/{session_id}/reject", session_id=session_id),
            body=await async_maybe_transform({"status_code": status_code}, session_reject_params.SessionRejectParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=NoneType,
        )


class SessionsWithRawResponse:
    def __init__(self, sessions: Sessions) -> None:
        self._sessions = sessions

        self.accept = _legacy_response.to_raw_response_wrapper(
            sessions.accept,
        )
        self.download_recording = _legacy_response.to_raw_response_wrapper(
            sessions.download_recording,
        )
        self.fork = _legacy_response.to_raw_response_wrapper(
            sessions.fork,
        )
        self.hangup = _legacy_response.to_raw_response_wrapper(
            sessions.hangup,
        )
        self.refer = _legacy_response.to_raw_response_wrapper(
            sessions.refer,
        )
        self.reject = _legacy_response.to_raw_response_wrapper(
            sessions.reject,
        )


class AsyncSessionsWithRawResponse:
    def __init__(self, sessions: AsyncSessions) -> None:
        self._sessions = sessions

        self.accept = _legacy_response.async_to_raw_response_wrapper(
            sessions.accept,
        )
        self.download_recording = _legacy_response.async_to_raw_response_wrapper(
            sessions.download_recording,
        )
        self.fork = _legacy_response.async_to_raw_response_wrapper(
            sessions.fork,
        )
        self.hangup = _legacy_response.async_to_raw_response_wrapper(
            sessions.hangup,
        )
        self.refer = _legacy_response.async_to_raw_response_wrapper(
            sessions.refer,
        )
        self.reject = _legacy_response.async_to_raw_response_wrapper(
            sessions.reject,
        )


class SessionsWithStreamingResponse:
    def __init__(self, sessions: Sessions) -> None:
        self._sessions = sessions

        self.accept = to_streamed_response_wrapper(
            sessions.accept,
        )
        self.download_recording = to_custom_streamed_response_wrapper(
            sessions.download_recording,
            StreamedBinaryAPIResponse,
        )
        self.fork = to_streamed_response_wrapper(
            sessions.fork,
        )
        self.hangup = to_streamed_response_wrapper(
            sessions.hangup,
        )
        self.refer = to_streamed_response_wrapper(
            sessions.refer,
        )
        self.reject = to_streamed_response_wrapper(
            sessions.reject,
        )


class AsyncSessionsWithStreamingResponse:
    def __init__(self, sessions: AsyncSessions) -> None:
        self._sessions = sessions

        self.accept = async_to_streamed_response_wrapper(
            sessions.accept,
        )
        self.download_recording = async_to_custom_streamed_response_wrapper(
            sessions.download_recording,
            AsyncStreamedBinaryAPIResponse,
        )
        self.fork = async_to_streamed_response_wrapper(
            sessions.fork,
        )
        self.hangup = async_to_streamed_response_wrapper(
            sessions.hangup,
        )
        self.refer = async_to_streamed_response_wrapper(
            sessions.refer,
        )
        self.reject = async_to_streamed_response_wrapper(
            sessions.reject,
        )
