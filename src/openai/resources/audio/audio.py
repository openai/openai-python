# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .speech import (
    Speech,
    AsyncSpeech,
    SpeechWithRawResponse,
    AsyncSpeechWithRawResponse,
    SpeechWithStreamingResponse,
    AsyncSpeechWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from .translations import (
    Translations,
    AsyncTranslations,
    TranslationsWithRawResponse,
    AsyncTranslationsWithRawResponse,
    TranslationsWithStreamingResponse,
    AsyncTranslationsWithStreamingResponse,
)
from .transcriptions import (
    Transcriptions,
    AsyncTranscriptions,
    TranscriptionsWithRawResponse,
    AsyncTranscriptionsWithRawResponse,
    TranscriptionsWithStreamingResponse,
    AsyncTranscriptionsWithStreamingResponse,
)

__all__ = ["Audio", "AsyncAudio"]


class Audio(SyncAPIResource):
    @cached_property
    def transcriptions(self) -> Transcriptions:
        """Turn audio into text or text into audio."""
        return Transcriptions(self._client)

    @cached_property
    def translations(self) -> Translations:
        """Turn audio into text or text into audio."""
        return Translations(self._client)

    @cached_property
    def speech(self) -> Speech:
        """Turn audio into text or text into audio."""
        return Speech(self._client)

    @cached_property
    def with_raw_response(self) -> AudioWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AudioWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AudioWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AudioWithStreamingResponse(self)


class AsyncAudio(AsyncAPIResource):
    @cached_property
    def transcriptions(self) -> AsyncTranscriptions:
        """Turn audio into text or text into audio."""
        return AsyncTranscriptions(self._client)

    @cached_property
    def translations(self) -> AsyncTranslations:
        """Turn audio into text or text into audio."""
        return AsyncTranslations(self._client)

    @cached_property
    def speech(self) -> AsyncSpeech:
        """Turn audio into text or text into audio."""
        return AsyncSpeech(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncAudioWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAudioWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAudioWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncAudioWithStreamingResponse(self)


class AudioWithRawResponse:
    def __init__(self, audio: Audio) -> None:
        self._audio = audio

    @cached_property
    def transcriptions(self) -> TranscriptionsWithRawResponse:
        """Turn audio into text or text into audio."""
        return TranscriptionsWithRawResponse(self._audio.transcriptions)

    @cached_property
    def translations(self) -> TranslationsWithRawResponse:
        """Turn audio into text or text into audio."""
        return TranslationsWithRawResponse(self._audio.translations)

    @cached_property
    def speech(self) -> SpeechWithRawResponse:
        """Turn audio into text or text into audio."""
        return SpeechWithRawResponse(self._audio.speech)


class AsyncAudioWithRawResponse:
    def __init__(self, audio: AsyncAudio) -> None:
        self._audio = audio

    @cached_property
    def transcriptions(self) -> AsyncTranscriptionsWithRawResponse:
        """Turn audio into text or text into audio."""
        return AsyncTranscriptionsWithRawResponse(self._audio.transcriptions)

    @cached_property
    def translations(self) -> AsyncTranslationsWithRawResponse:
        """Turn audio into text or text into audio."""
        return AsyncTranslationsWithRawResponse(self._audio.translations)

    @cached_property
    def speech(self) -> AsyncSpeechWithRawResponse:
        """Turn audio into text or text into audio."""
        return AsyncSpeechWithRawResponse(self._audio.speech)


class AudioWithStreamingResponse:
    def __init__(self, audio: Audio) -> None:
        self._audio = audio

    @cached_property
    def transcriptions(self) -> TranscriptionsWithStreamingResponse:
        """Turn audio into text or text into audio."""
        return TranscriptionsWithStreamingResponse(self._audio.transcriptions)

    @cached_property
    def translations(self) -> TranslationsWithStreamingResponse:
        """Turn audio into text or text into audio."""
        return TranslationsWithStreamingResponse(self._audio.translations)

    @cached_property
    def speech(self) -> SpeechWithStreamingResponse:
        """Turn audio into text or text into audio."""
        return SpeechWithStreamingResponse(self._audio.speech)


class AsyncAudioWithStreamingResponse:
    def __init__(self, audio: AsyncAudio) -> None:
        self._audio = audio

    @cached_property
    def transcriptions(self) -> AsyncTranscriptionsWithStreamingResponse:
        """Turn audio into text or text into audio."""
        return AsyncTranscriptionsWithStreamingResponse(self._audio.transcriptions)

    @cached_property
    def translations(self) -> AsyncTranslationsWithStreamingResponse:
        """Turn audio into text or text into audio."""
        return AsyncTranslationsWithStreamingResponse(self._audio.translations)

    @cached_property
    def speech(self) -> AsyncSpeechWithStreamingResponse:
        """Turn audio into text or text into audio."""
        return AsyncSpeechWithStreamingResponse(self._audio.speech)
