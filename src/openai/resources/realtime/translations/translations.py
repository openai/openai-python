# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from .client_secrets import (
    ClientSecrets,
    AsyncClientSecrets,
    ClientSecretsWithRawResponse,
    AsyncClientSecretsWithRawResponse,
    ClientSecretsWithStreamingResponse,
    AsyncClientSecretsWithStreamingResponse,
)

__all__ = ["Translations", "AsyncTranslations"]


class Translations(SyncAPIResource):
    @cached_property
    def client_secrets(self) -> ClientSecrets:
        return ClientSecrets(self._client)

    @cached_property
    def with_raw_response(self) -> TranslationsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
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


class AsyncTranslations(AsyncAPIResource):
    @cached_property
    def client_secrets(self) -> AsyncClientSecrets:
        return AsyncClientSecrets(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncTranslationsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
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


class TranslationsWithRawResponse:
    def __init__(self, translations: Translations) -> None:
        self._translations = translations

    @cached_property
    def client_secrets(self) -> ClientSecretsWithRawResponse:
        return ClientSecretsWithRawResponse(self._translations.client_secrets)


class AsyncTranslationsWithRawResponse:
    def __init__(self, translations: AsyncTranslations) -> None:
        self._translations = translations

    @cached_property
    def client_secrets(self) -> AsyncClientSecretsWithRawResponse:
        return AsyncClientSecretsWithRawResponse(self._translations.client_secrets)


class TranslationsWithStreamingResponse:
    def __init__(self, translations: Translations) -> None:
        self._translations = translations

    @cached_property
    def client_secrets(self) -> ClientSecretsWithStreamingResponse:
        return ClientSecretsWithStreamingResponse(self._translations.client_secrets)


class AsyncTranslationsWithStreamingResponse:
    def __init__(self, translations: AsyncTranslations) -> None:
        self._translations = translations

    @cached_property
    def client_secrets(self) -> AsyncClientSecretsWithStreamingResponse:
        return AsyncClientSecretsWithStreamingResponse(self._translations.client_secrets)
