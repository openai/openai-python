# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal

import httpx

from ... import _legacy_response
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import (
    maybe_transform,
    async_maybe_transform,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
    to_custom_streamed_response_wrapper,
    async_to_custom_streamed_response_wrapper,
)
from ...types.audio import speech_create_params
from ..._base_client import make_request_options
from ...types.audio.speech_model import SpeechModel

__all__ = ["Speech", "AsyncSpeech"]


class Speech(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SpeechWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return SpeechWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SpeechWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return SpeechWithStreamingResponse(self)

    def create(
        self,
        *,
        input: str,
        model: Union[str, SpeechModel],
        voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        response_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] | NotGiven = NOT_GIVEN,
        speed: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> _legacy_response.HttpxBinaryResponseContent:
        """
        Generates audio from the input text.

        Args:
          input: The text to generate audio for. The maximum length is 4096 characters.

          model:
              One of the available [TTS models](https://platform.openai.com/docs/models#tts):
              `tts-1` or `tts-1-hd`

          voice: The voice to use when generating the audio. Supported voices are `alloy`,
              `echo`, `fable`, `onyx`, `nova`, and `shimmer`. Previews of the voices are
              available in the
              [Text to speech guide](https://platform.openai.com/docs/guides/text-to-speech#voice-options).

          response_format: The format to audio in. Supported formats are `mp3`, `opus`, `aac`, `flac`,
              `wav`, and `pcm`.

          speed: The speed of the generated audio. Select a value from `0.25` to `4.0`. `1.0` is
              the default.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
        return self._post(
            "/audio/speech",
            body=maybe_transform(
                {
                    "input": input,
                    "model": model,
                    "voice": voice,
                    "response_format": response_format,
                    "speed": speed,
                },
                speech_create_params.SpeechCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=_legacy_response.HttpxBinaryResponseContent,
        )


class AsyncSpeech(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSpeechWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSpeechWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSpeechWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncSpeechWithStreamingResponse(self)

    async def create(
        self,
        *,
        input: str,
        model: Union[str, SpeechModel],
        voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        response_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] | NotGiven = NOT_GIVEN,
        speed: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> _legacy_response.HttpxBinaryResponseContent:
        """
        Generates audio from the input text.

        Args:
          input: The text to generate audio for. The maximum length is 4096 characters.

          model:
              One of the available [TTS models](https://platform.openai.com/docs/models#tts):
              `tts-1` or `tts-1-hd`

          voice: The voice to use when generating the audio. Supported voices are `alloy`,
              `echo`, `fable`, `onyx`, `nova`, and `shimmer`. Previews of the voices are
              available in the
              [Text to speech guide](https://platform.openai.com/docs/guides/text-to-speech#voice-options).

          response_format: The format to audio in. Supported formats are `mp3`, `opus`, `aac`, `flac`,
              `wav`, and `pcm`.

          speed: The speed of the generated audio. Select a value from `0.25` to `4.0`. `1.0` is
              the default.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
        return await self._post(
            "/audio/speech",
            body=await async_maybe_transform(
                {
                    "input": input,
                    "model": model,
                    "voice": voice,
                    "response_format": response_format,
                    "speed": speed,
                },
                speech_create_params.SpeechCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=_legacy_response.HttpxBinaryResponseContent,
        )


class SpeechWithRawResponse:
    def __init__(self, speech: Speech) -> None:
        self._speech = speech

        self.create = _legacy_response.to_raw_response_wrapper(
            speech.create,
        )


class AsyncSpeechWithRawResponse:
    def __init__(self, speech: AsyncSpeech) -> None:
        self._speech = speech

        self.create = _legacy_response.async_to_raw_response_wrapper(
            speech.create,
        )


class SpeechWithStreamingResponse:
    def __init__(self, speech: Speech) -> None:
        self._speech = speech

        self.create = to_custom_streamed_response_wrapper(
            speech.create,
            StreamedBinaryAPIResponse,
        )


class AsyncSpeechWithStreamingResponse:
    def __init__(self, speech: AsyncSpeech) -> None:
        self._speech = speech

        self.create = async_to_custom_streamed_response_wrapper(
            speech.create,
            AsyncStreamedBinaryAPIResponse,
        )
