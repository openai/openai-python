# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Mapping, cast

import httpx

from ... import _legacy_response
from ...types import AudioResponseFormat
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven, FileTypes
from ..._utils import (
    extract_files,
    maybe_transform,
    deepcopy_minimal,
    async_maybe_transform,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ...types.audio import translation_create_params
from ..._base_client import make_request_options
from ...types.audio_model import AudioModel
from ...types.audio.translation import Translation
from ...types.audio_response_format import AudioResponseFormat

__all__ = ["Translations", "AsyncTranslations"]


class Translations(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TranslationsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return TranslationsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TranslationsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return TranslationsWithStreamingResponse(self)

    def create(
        self,
        *,
        file: FileTypes,
        model: Union[str, AudioModel],
        prompt: str | NotGiven = NOT_GIVEN,
        response_format: AudioResponseFormat | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Translation:
        """
        Translates audio into English.

        Args:
          file: The audio file object (not file name) translate, in one of these formats: flac,
              mp3, mp4, mpeg, mpga, m4a, ogg, wav, or webm.

          model: ID of the model to use. Only `whisper-1` (which is powered by our open source
              Whisper V2 model) is currently available.

          prompt: An optional text to guide the model's style or continue a previous audio
              segment. The
              [prompt](https://platform.openai.com/docs/guides/speech-to-text/prompting)
              should be in English.

          response_format: The format of the output, in one of these options: `json`, `text`, `srt`,
              `verbose_json`, or `vtt`.

          temperature: The sampling temperature, between 0 and 1. Higher values like 0.8 will make the
              output more random, while lower values like 0.2 will make it more focused and
              deterministic. If set to 0, the model will use
              [log probability](https://en.wikipedia.org/wiki/Log_probability) to
              automatically increase the temperature until certain thresholds are hit.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "file": file,
                "model": model,
                "prompt": prompt,
                "response_format": response_format,
                "temperature": temperature,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/audio/translations",
            body=maybe_transform(body, translation_create_params.TranslationCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Translation,
        )


class AsyncTranslations(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTranslationsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTranslationsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTranslationsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncTranslationsWithStreamingResponse(self)

    async def create(
        self,
        *,
        file: FileTypes,
        model: Union[str, AudioModel],
        prompt: str | NotGiven = NOT_GIVEN,
        response_format: AudioResponseFormat | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Translation:
        """
        Translates audio into English.

        Args:
          file: The audio file object (not file name) translate, in one of these formats: flac,
              mp3, mp4, mpeg, mpga, m4a, ogg, wav, or webm.

          model: ID of the model to use. Only `whisper-1` (which is powered by our open source
              Whisper V2 model) is currently available.

          prompt: An optional text to guide the model's style or continue a previous audio
              segment. The
              [prompt](https://platform.openai.com/docs/guides/speech-to-text/prompting)
              should be in English.

          response_format: The format of the output, in one of these options: `json`, `text`, `srt`,
              `verbose_json`, or `vtt`.

          temperature: The sampling temperature, between 0 and 1. Higher values like 0.8 will make the
              output more random, while lower values like 0.2 will make it more focused and
              deterministic. If set to 0, the model will use
              [log probability](https://en.wikipedia.org/wiki/Log_probability) to
              automatically increase the temperature until certain thresholds are hit.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "file": file,
                "model": model,
                "prompt": prompt,
                "response_format": response_format,
                "temperature": temperature,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/audio/translations",
            body=await async_maybe_transform(body, translation_create_params.TranslationCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Translation,
        )


class TranslationsWithRawResponse:
    def __init__(self, translations: Translations) -> None:
        self._translations = translations

        self.create = _legacy_response.to_raw_response_wrapper(
            translations.create,
        )


class AsyncTranslationsWithRawResponse:
    def __init__(self, translations: AsyncTranslations) -> None:
        self._translations = translations

        self.create = _legacy_response.async_to_raw_response_wrapper(
            translations.create,
        )


class TranslationsWithStreamingResponse:
    def __init__(self, translations: Translations) -> None:
        self._translations = translations

        self.create = to_streamed_response_wrapper(
            translations.create,
        )


class AsyncTranslationsWithStreamingResponse:
    def __init__(self, translations: AsyncTranslations) -> None:
        self._translations = translations

        self.create = async_to_streamed_response_wrapper(
            translations.create,
        )
