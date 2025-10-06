# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, Mapping, cast

import httpx

from .... import _legacy_response
from .threads import (
    Threads,
    AsyncThreads,
    ThreadsWithRawResponse,
    AsyncThreadsWithRawResponse,
    ThreadsWithStreamingResponse,
    AsyncThreadsWithStreamingResponse,
)
from .sessions import (
    Sessions,
    AsyncSessions,
    SessionsWithRawResponse,
    AsyncSessionsWithRawResponse,
    SessionsWithStreamingResponse,
    AsyncSessionsWithStreamingResponse,
)
from ...._types import Body, Query, Headers, NotGiven, FileTypes, not_given
from ...._utils import extract_files, maybe_transform, deepcopy_minimal, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ....types.beta import chatkit_upload_file_params
from ...._base_client import make_request_options
from ....types.beta.chatkit_upload_file_response import ChatKitUploadFileResponse

__all__ = ["ChatKit", "AsyncChatKit"]


class ChatKit(SyncAPIResource):
    @cached_property
    def sessions(self) -> Sessions:
        return Sessions(self._client)

    @cached_property
    def threads(self) -> Threads:
        return Threads(self._client)

    @cached_property
    def with_raw_response(self) -> ChatKitWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return ChatKitWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ChatKitWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return ChatKitWithStreamingResponse(self)

    def upload_file(
        self,
        *,
        file: FileTypes,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ChatKitUploadFileResponse:
        """
        Upload a ChatKit file

        Args:
          file: Binary file contents to store with the ChatKit session. Supports PDFs and PNG,
              JPG, JPEG, GIF, or WEBP images.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"OpenAI-Beta": "chatkit_beta=v1", **(extra_headers or {})}
        body = deepcopy_minimal({"file": file})
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        if files:
            # It should be noted that the actual Content-Type header that will be
            # sent to the server will contain a `boundary` parameter, e.g.
            # multipart/form-data; boundary=---abc--
            extra_headers["Content-Type"] = "multipart/form-data"
        return cast(
            ChatKitUploadFileResponse,
            self._post(
                "/chatkit/files",
                body=maybe_transform(body, chatkit_upload_file_params.ChatKitUploadFileParams),
                files=files,
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ChatKitUploadFileResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class AsyncChatKit(AsyncAPIResource):
    @cached_property
    def sessions(self) -> AsyncSessions:
        return AsyncSessions(self._client)

    @cached_property
    def threads(self) -> AsyncThreads:
        return AsyncThreads(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncChatKitWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncChatKitWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncChatKitWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncChatKitWithStreamingResponse(self)

    async def upload_file(
        self,
        *,
        file: FileTypes,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ChatKitUploadFileResponse:
        """
        Upload a ChatKit file

        Args:
          file: Binary file contents to store with the ChatKit session. Supports PDFs and PNG,
              JPG, JPEG, GIF, or WEBP images.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"OpenAI-Beta": "chatkit_beta=v1", **(extra_headers or {})}
        body = deepcopy_minimal({"file": file})
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        if files:
            # It should be noted that the actual Content-Type header that will be
            # sent to the server will contain a `boundary` parameter, e.g.
            # multipart/form-data; boundary=---abc--
            extra_headers["Content-Type"] = "multipart/form-data"
        return cast(
            ChatKitUploadFileResponse,
            await self._post(
                "/chatkit/files",
                body=await async_maybe_transform(body, chatkit_upload_file_params.ChatKitUploadFileParams),
                files=files,
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ChatKitUploadFileResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class ChatKitWithRawResponse:
    def __init__(self, chatkit: ChatKit) -> None:
        self._chatkit = chatkit

        self.upload_file = _legacy_response.to_raw_response_wrapper(
            chatkit.upload_file,
        )

    @cached_property
    def sessions(self) -> SessionsWithRawResponse:
        return SessionsWithRawResponse(self._chatkit.sessions)

    @cached_property
    def threads(self) -> ThreadsWithRawResponse:
        return ThreadsWithRawResponse(self._chatkit.threads)


class AsyncChatKitWithRawResponse:
    def __init__(self, chatkit: AsyncChatKit) -> None:
        self._chatkit = chatkit

        self.upload_file = _legacy_response.async_to_raw_response_wrapper(
            chatkit.upload_file,
        )

    @cached_property
    def sessions(self) -> AsyncSessionsWithRawResponse:
        return AsyncSessionsWithRawResponse(self._chatkit.sessions)

    @cached_property
    def threads(self) -> AsyncThreadsWithRawResponse:
        return AsyncThreadsWithRawResponse(self._chatkit.threads)


class ChatKitWithStreamingResponse:
    def __init__(self, chatkit: ChatKit) -> None:
        self._chatkit = chatkit

        self.upload_file = to_streamed_response_wrapper(
            chatkit.upload_file,
        )

    @cached_property
    def sessions(self) -> SessionsWithStreamingResponse:
        return SessionsWithStreamingResponse(self._chatkit.sessions)

    @cached_property
    def threads(self) -> ThreadsWithStreamingResponse:
        return ThreadsWithStreamingResponse(self._chatkit.threads)


class AsyncChatKitWithStreamingResponse:
    def __init__(self, chatkit: AsyncChatKit) -> None:
        self._chatkit = chatkit

        self.upload_file = async_to_streamed_response_wrapper(
            chatkit.upload_file,
        )

    @cached_property
    def sessions(self) -> AsyncSessionsWithStreamingResponse:
        return AsyncSessionsWithStreamingResponse(self._chatkit.sessions)

    @cached_property
    def threads(self) -> AsyncThreadsWithStreamingResponse:
        return AsyncThreadsWithStreamingResponse(self._chatkit.threads)
