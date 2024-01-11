# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from .speech import Speech, AsyncSpeech, SpeechWithRawResponse, AsyncSpeechWithRawResponse
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from .translations import Translations, AsyncTranslations, TranslationsWithRawResponse, AsyncTranslationsWithRawResponse
from .transcriptions import (
    Transcriptions,
    AsyncTranscriptions,
    TranscriptionsWithRawResponse,
    AsyncTranscriptionsWithRawResponse,
)

__all__ = ["Audio", "AsyncAudio"]


class Audio(SyncAPIResource):
    @cached_property
    def transcriptions(self) -> Transcriptions:
        return Transcriptions(self._client)

    @cached_property
    def translations(self) -> Translations:
        return Translations(self._client)

    @cached_property
    def speech(self) -> Speech:
        return Speech(self._client)

    @cached_property
    def with_raw_response(self) -> AudioWithRawResponse:
        return AudioWithRawResponse(self)


class AsyncAudio(AsyncAPIResource):
    @cached_property
    def transcriptions(self) -> AsyncTranscriptions:
        return AsyncTranscriptions(self._client)

    @cached_property
    def translations(self) -> AsyncTranslations:
        return AsyncTranslations(self._client)

    @cached_property
    def speech(self) -> AsyncSpeech:
        return AsyncSpeech(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncAudioWithRawResponse:
        return AsyncAudioWithRawResponse(self)


class AudioWithRawResponse:
    def __init__(self, audio: Audio) -> None:
        self.transcriptions = TranscriptionsWithRawResponse(audio.transcriptions)
        self.translations = TranslationsWithRawResponse(audio.translations)
        self.speech = SpeechWithRawResponse(audio.speech)


class AsyncAudioWithRawResponse:
    def __init__(self, audio: AsyncAudio) -> None:
        self.transcriptions = AsyncTranscriptionsWithRawResponse(audio.transcriptions)
        self.translations = AsyncTranslationsWithRawResponse(audio.translations)
        self.speech = AsyncSpeechWithRawResponse(audio.speech)
