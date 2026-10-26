# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Mapping, cast

import httpx2

from ... import _legacy_response
from ..._files import deepcopy_with_paths
from ..._types import Body, Omit, Query, Headers, NotGiven, FileTypes, omit, not_given
from ..._utils import extract_files, path_template, maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ...pagination import SyncCursorPage, AsyncCursorPage
from ...types.audio import voice_consent_list_params, voice_consent_create_params, voice_consent_update_params
from ..._base_client import AsyncPaginator, make_request_options
from ...types.audio.voice_consent import VoiceConsent
from ...types.audio.voice_consent_deleted import VoiceConsentDeleted

__all__ = ["VoiceConsents", "AsyncVoiceConsents"]


class VoiceConsents(SyncAPIResource):
    """Turn audio into text or text into audio."""

    @cached_property
    def with_raw_response(self) -> VoiceConsentsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return VoiceConsentsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> VoiceConsentsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return VoiceConsentsWithStreamingResponse(self)

    def create(
        self,
        *,
        language: str,
        name: str,
        recording: FileTypes,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> VoiceConsent:
        """
        Upload a voice consent recording.

        Args:
          language: The BCP 47 language tag for the consent phrase (for example, `en-US`).

          name: The label to use for this consent recording.

          recording: The consent audio recording file. Maximum size is 10 MiB.

              Supported MIME types: `audio/mpeg`, `audio/wav`, `audio/x-wav`, `audio/ogg`,
              `audio/aac`, `audio/flac`, `audio/webm`, `audio/mp4`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_with_paths(
            {
                "language": language,
                "name": name,
                "recording": recording,
            },
            [["recording"]],
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["recording"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/audio/voice_consents",
            body=maybe_transform(body, voice_consent_create_params.VoiceConsentCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=VoiceConsent,
        )

    def retrieve(
        self,
        consent_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> VoiceConsent:
        """
        Retrieves a voice consent recording.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not consent_id:
            raise ValueError(f"Expected a non-empty value for `consent_id` but received {consent_id!r}")
        return self._get(
            path_template("/audio/voice_consents/{consent_id}", consent_id=consent_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=VoiceConsent,
        )

    def update(
        self,
        consent_id: str,
        *,
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> VoiceConsent:
        """
        Updates a voice consent recording (metadata only).

        Args:
          name: The updated label for this consent recording.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not consent_id:
            raise ValueError(f"Expected a non-empty value for `consent_id` but received {consent_id!r}")
        return self._post(
            path_template("/audio/voice_consents/{consent_id}", consent_id=consent_id),
            body=maybe_transform({"name": name}, voice_consent_update_params.VoiceConsentUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=VoiceConsent,
        )

    def list(
        self,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPage[VoiceConsent]:
        """Returns a list of voice consent recordings.

        Args:
          after: A cursor for use in pagination.

        `after` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include after=obj_foo in order to
              fetch the next page of the list.

          limit: A limit on the number of objects to be returned. Limit can range between 1 and
              100, and the default is 20.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/audio/voice_consents",
            page=SyncCursorPage[VoiceConsent],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                    },
                    voice_consent_list_params.VoiceConsentListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=VoiceConsent,
        )

    def delete(
        self,
        consent_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> VoiceConsentDeleted:
        """
        Deletes a voice consent recording.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not consent_id:
            raise ValueError(f"Expected a non-empty value for `consent_id` but received {consent_id!r}")
        return self._delete(
            path_template("/audio/voice_consents/{consent_id}", consent_id=consent_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=VoiceConsentDeleted,
        )


class AsyncVoiceConsents(AsyncAPIResource):
    """Turn audio into text or text into audio."""

    @cached_property
    def with_raw_response(self) -> AsyncVoiceConsentsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncVoiceConsentsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncVoiceConsentsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncVoiceConsentsWithStreamingResponse(self)

    async def create(
        self,
        *,
        language: str,
        name: str,
        recording: FileTypes,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> VoiceConsent:
        """
        Upload a voice consent recording.

        Args:
          language: The BCP 47 language tag for the consent phrase (for example, `en-US`).

          name: The label to use for this consent recording.

          recording: The consent audio recording file. Maximum size is 10 MiB.

              Supported MIME types: `audio/mpeg`, `audio/wav`, `audio/x-wav`, `audio/ogg`,
              `audio/aac`, `audio/flac`, `audio/webm`, `audio/mp4`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_with_paths(
            {
                "language": language,
                "name": name,
                "recording": recording,
            },
            [["recording"]],
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["recording"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/audio/voice_consents",
            body=await async_maybe_transform(body, voice_consent_create_params.VoiceConsentCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=VoiceConsent,
        )

    async def retrieve(
        self,
        consent_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> VoiceConsent:
        """
        Retrieves a voice consent recording.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not consent_id:
            raise ValueError(f"Expected a non-empty value for `consent_id` but received {consent_id!r}")
        return await self._get(
            path_template("/audio/voice_consents/{consent_id}", consent_id=consent_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=VoiceConsent,
        )

    async def update(
        self,
        consent_id: str,
        *,
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> VoiceConsent:
        """
        Updates a voice consent recording (metadata only).

        Args:
          name: The updated label for this consent recording.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not consent_id:
            raise ValueError(f"Expected a non-empty value for `consent_id` but received {consent_id!r}")
        return await self._post(
            path_template("/audio/voice_consents/{consent_id}", consent_id=consent_id),
            body=await async_maybe_transform({"name": name}, voice_consent_update_params.VoiceConsentUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=VoiceConsent,
        )

    def list(
        self,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[VoiceConsent, AsyncCursorPage[VoiceConsent]]:
        """Returns a list of voice consent recordings.

        Args:
          after: A cursor for use in pagination.

        `after` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include after=obj_foo in order to
              fetch the next page of the list.

          limit: A limit on the number of objects to be returned. Limit can range between 1 and
              100, and the default is 20.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/audio/voice_consents",
            page=AsyncCursorPage[VoiceConsent],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                    },
                    voice_consent_list_params.VoiceConsentListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=VoiceConsent,
        )

    async def delete(
        self,
        consent_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> VoiceConsentDeleted:
        """
        Deletes a voice consent recording.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not consent_id:
            raise ValueError(f"Expected a non-empty value for `consent_id` but received {consent_id!r}")
        return await self._delete(
            path_template("/audio/voice_consents/{consent_id}", consent_id=consent_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=VoiceConsentDeleted,
        )


class VoiceConsentsWithRawResponse:
    def __init__(self, voice_consents: VoiceConsents) -> None:
        self._voice_consents = voice_consents

        self.create = _legacy_response.to_raw_response_wrapper(
            voice_consents.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            voice_consents.retrieve,
        )
        self.update = _legacy_response.to_raw_response_wrapper(
            voice_consents.update,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            voice_consents.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            voice_consents.delete,
        )


class AsyncVoiceConsentsWithRawResponse:
    def __init__(self, voice_consents: AsyncVoiceConsents) -> None:
        self._voice_consents = voice_consents

        self.create = _legacy_response.async_to_raw_response_wrapper(
            voice_consents.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            voice_consents.retrieve,
        )
        self.update = _legacy_response.async_to_raw_response_wrapper(
            voice_consents.update,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            voice_consents.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            voice_consents.delete,
        )


class VoiceConsentsWithStreamingResponse:
    def __init__(self, voice_consents: VoiceConsents) -> None:
        self._voice_consents = voice_consents

        self.create = to_streamed_response_wrapper(
            voice_consents.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            voice_consents.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            voice_consents.update,
        )
        self.list = to_streamed_response_wrapper(
            voice_consents.list,
        )
        self.delete = to_streamed_response_wrapper(
            voice_consents.delete,
        )


class AsyncVoiceConsentsWithStreamingResponse:
    def __init__(self, voice_consents: AsyncVoiceConsents) -> None:
        self._voice_consents = voice_consents

        self.create = async_to_streamed_response_wrapper(
            voice_consents.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            voice_consents.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            voice_consents.update,
        )
        self.list = async_to_streamed_response_wrapper(
            voice_consents.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            voice_consents.delete,
        )
