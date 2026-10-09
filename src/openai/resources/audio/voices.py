# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Mapping, cast
from typing_extensions import Literal

import httpx2

from ... import _legacy_response
from ..._files import deepcopy_with_paths
from ..._types import Body, Omit, Query, Headers, NotGiven, FileTypes, omit, not_given
from ..._utils import extract_files, required_args, maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ...types.audio import voice_create_params
from ..._base_client import make_request_options
from ...types.audio.voice import Voice

__all__ = ["Voices", "AsyncVoices"]


class Voices(SyncAPIResource):
    """Turn audio into text or text into audio."""

    @cached_property
    def with_raw_response(self) -> VoicesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return VoicesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> VoicesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return VoicesWithStreamingResponse(self)

    @required_args(["audio_sample", "consent", "name"])
    def create(
        self,
        *,
        audio_sample: FileTypes,
        consent: str,
        name: str,
        type: Literal["audio_sample"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Voice:
        """Create a custom voice you can use for audio output (for example, in
        Text-to-Speech and the Realtime API). This requires an audio sample and a
        previously uploaded consent recording.

        Send `name`, `audio_sample`, and the `consent` recording ID as multipart form
        data. The optional `type` defaults to `audio_sample`.

        Returns the saved voice's metadata. See the
        [custom voices guide](https://developers.openai.com/api/docs/guides/text-to-speech#custom-voices)
        for requirements and best practices. Custom voices are limited to eligible
        customers.

        Args:
          audio_sample: The sample audio recording file. Maximum size is 10 MiB.

              Supported MIME types: `audio/mpeg`, `audio/wav`, `audio/x-wav`, `audio/ogg`,
              `audio/aac`, `audio/flac`, `audio/webm`, `audio/mp4`.

          consent: The consent recording ID (for example, `cons_1234`).

          name: The name of the new voice.

          type: The voice creation method. Defaults to `audio_sample` when omitted.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_with_paths(
            {
                "audio_sample": audio_sample,
                "consent": consent,
                "name": name,
                "type": type,
            },
            [["audio_sample"]],
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["audio_sample"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/audio/voices",
            body=maybe_transform(body, voice_create_params.VoiceCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Voice,
        )


class AsyncVoices(AsyncAPIResource):
    """Turn audio into text or text into audio."""

    @cached_property
    def with_raw_response(self) -> AsyncVoicesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncVoicesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncVoicesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncVoicesWithStreamingResponse(self)

    @required_args(["audio_sample", "consent", "name"])
    async def create(
        self,
        *,
        audio_sample: FileTypes,
        consent: str,
        name: str,
        type: Literal["audio_sample"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Voice:
        """Create a custom voice you can use for audio output (for example, in
        Text-to-Speech and the Realtime API). This requires an audio sample and a
        previously uploaded consent recording.

        Send `name`, `audio_sample`, and the `consent` recording ID as multipart form
        data. The optional `type` defaults to `audio_sample`.

        Returns the saved voice's metadata. See the
        [custom voices guide](https://developers.openai.com/api/docs/guides/text-to-speech#custom-voices)
        for requirements and best practices. Custom voices are limited to eligible
        customers.

        Args:
          audio_sample: The sample audio recording file. Maximum size is 10 MiB.

              Supported MIME types: `audio/mpeg`, `audio/wav`, `audio/x-wav`, `audio/ogg`,
              `audio/aac`, `audio/flac`, `audio/webm`, `audio/mp4`.

          consent: The consent recording ID (for example, `cons_1234`).

          name: The name of the new voice.

          type: The voice creation method. Defaults to `audio_sample` when omitted.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_with_paths(
            {
                "audio_sample": audio_sample,
                "consent": consent,
                "name": name,
                "type": type,
            },
            [["audio_sample"]],
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["audio_sample"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/audio/voices",
            body=await async_maybe_transform(body, voice_create_params.VoiceCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Voice,
        )


class VoicesWithRawResponse:
    def __init__(self, voices: Voices) -> None:
        self._voices = voices

        self.create = _legacy_response.to_raw_response_wrapper(
            voices.create,
        )


class AsyncVoicesWithRawResponse:
    def __init__(self, voices: AsyncVoices) -> None:
        self._voices = voices

        self.create = _legacy_response.async_to_raw_response_wrapper(
            voices.create,
        )


class VoicesWithStreamingResponse:
    def __init__(self, voices: Voices) -> None:
        self._voices = voices

        self.create = to_streamed_response_wrapper(
            voices.create,
        )


class AsyncVoicesWithStreamingResponse:
    def __init__(self, voices: AsyncVoices) -> None:
        self._voices = voices

        self.create = async_to_streamed_response_wrapper(
            voices.create,
        )
