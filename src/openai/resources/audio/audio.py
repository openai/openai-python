# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import TYPE_CHECKING

from ..._resource import SyncAPIResource, AsyncAPIResource
from .translations import Translations, AsyncTranslations
from .transcriptions import Transcriptions, AsyncTranscriptions

if TYPE_CHECKING:
    from ..._client import OpenAI, AsyncOpenAI

__all__ = ["Audio", "AsyncAudio"]


class Audio(SyncAPIResource):
    transcriptions: Transcriptions
    translations: Translations

    def __init__(self, client: OpenAI) -> None:
        super().__init__(client)
        self.transcriptions = Transcriptions(client)
        self.translations = Translations(client)


class AsyncAudio(AsyncAPIResource):
    transcriptions: AsyncTranscriptions
    translations: AsyncTranslations

    def __init__(self, client: AsyncOpenAI) -> None:
        super().__init__(client)
        self.transcriptions = AsyncTranscriptions(client)
        self.translations = AsyncTranslations(client)
