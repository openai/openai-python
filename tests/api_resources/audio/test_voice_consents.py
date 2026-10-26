# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.audio import VoiceConsent, VoiceConsentDeleted

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestVoiceConsents:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        voice_consent = client.audio.voice_consents.create(
            language="language",
            name="name",
            recording=b"Example data",
        )
        assert_matches_type(VoiceConsent, voice_consent, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.audio.voice_consents.with_raw_response.create(
            language="language",
            name="name",
            recording=b"Example data",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        voice_consent = response.parse()
        assert_matches_type(VoiceConsent, voice_consent, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.audio.voice_consents.with_streaming_response.create(
            language="language",
            name="name",
            recording=b"Example data",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            voice_consent = response.parse()
            assert_matches_type(VoiceConsent, voice_consent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        voice_consent = client.audio.voice_consents.retrieve(
            "consent_id",
        )
        assert_matches_type(VoiceConsent, voice_consent, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.audio.voice_consents.with_raw_response.retrieve(
            "consent_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        voice_consent = response.parse()
        assert_matches_type(VoiceConsent, voice_consent, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.audio.voice_consents.with_streaming_response.retrieve(
            "consent_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            voice_consent = response.parse()
            assert_matches_type(VoiceConsent, voice_consent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `consent_id` but received ''"):
            client.audio.voice_consents.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_update(self, client: OpenAI) -> None:
        voice_consent = client.audio.voice_consents.update(
            consent_id="consent_id",
            name="name",
        )
        assert_matches_type(VoiceConsent, voice_consent, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: OpenAI) -> None:
        response = client.audio.voice_consents.with_raw_response.update(
            consent_id="consent_id",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        voice_consent = response.parse()
        assert_matches_type(VoiceConsent, voice_consent, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: OpenAI) -> None:
        with client.audio.voice_consents.with_streaming_response.update(
            consent_id="consent_id",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            voice_consent = response.parse()
            assert_matches_type(VoiceConsent, voice_consent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `consent_id` but received ''"):
            client.audio.voice_consents.with_raw_response.update(
                consent_id="",
                name="name",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        voice_consent = client.audio.voice_consents.list()
        assert_matches_type(SyncCursorPage[VoiceConsent], voice_consent, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        voice_consent = client.audio.voice_consents.list(
            after="after",
            limit=0,
        )
        assert_matches_type(SyncCursorPage[VoiceConsent], voice_consent, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.audio.voice_consents.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        voice_consent = response.parse()
        assert_matches_type(SyncCursorPage[VoiceConsent], voice_consent, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.audio.voice_consents.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            voice_consent = response.parse()
            assert_matches_type(SyncCursorPage[VoiceConsent], voice_consent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        voice_consent = client.audio.voice_consents.delete(
            "consent_id",
        )
        assert_matches_type(VoiceConsentDeleted, voice_consent, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.audio.voice_consents.with_raw_response.delete(
            "consent_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        voice_consent = response.parse()
        assert_matches_type(VoiceConsentDeleted, voice_consent, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.audio.voice_consents.with_streaming_response.delete(
            "consent_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            voice_consent = response.parse()
            assert_matches_type(VoiceConsentDeleted, voice_consent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `consent_id` but received ''"):
            client.audio.voice_consents.with_raw_response.delete(
                "",
            )


class TestAsyncVoiceConsents:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        voice_consent = await async_client.audio.voice_consents.create(
            language="language",
            name="name",
            recording=b"Example data",
        )
        assert_matches_type(VoiceConsent, voice_consent, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.audio.voice_consents.with_raw_response.create(
            language="language",
            name="name",
            recording=b"Example data",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        voice_consent = response.parse()
        assert_matches_type(VoiceConsent, voice_consent, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.audio.voice_consents.with_streaming_response.create(
            language="language",
            name="name",
            recording=b"Example data",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            voice_consent = await response.parse()
            assert_matches_type(VoiceConsent, voice_consent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        voice_consent = await async_client.audio.voice_consents.retrieve(
            "consent_id",
        )
        assert_matches_type(VoiceConsent, voice_consent, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.audio.voice_consents.with_raw_response.retrieve(
            "consent_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        voice_consent = response.parse()
        assert_matches_type(VoiceConsent, voice_consent, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.audio.voice_consents.with_streaming_response.retrieve(
            "consent_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            voice_consent = await response.parse()
            assert_matches_type(VoiceConsent, voice_consent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `consent_id` but received ''"):
            await async_client.audio.voice_consents.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncOpenAI) -> None:
        voice_consent = await async_client.audio.voice_consents.update(
            consent_id="consent_id",
            name="name",
        )
        assert_matches_type(VoiceConsent, voice_consent, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.audio.voice_consents.with_raw_response.update(
            consent_id="consent_id",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        voice_consent = response.parse()
        assert_matches_type(VoiceConsent, voice_consent, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncOpenAI) -> None:
        async with async_client.audio.voice_consents.with_streaming_response.update(
            consent_id="consent_id",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            voice_consent = await response.parse()
            assert_matches_type(VoiceConsent, voice_consent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `consent_id` but received ''"):
            await async_client.audio.voice_consents.with_raw_response.update(
                consent_id="",
                name="name",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        voice_consent = await async_client.audio.voice_consents.list()
        assert_matches_type(AsyncCursorPage[VoiceConsent], voice_consent, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        voice_consent = await async_client.audio.voice_consents.list(
            after="after",
            limit=0,
        )
        assert_matches_type(AsyncCursorPage[VoiceConsent], voice_consent, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.audio.voice_consents.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        voice_consent = response.parse()
        assert_matches_type(AsyncCursorPage[VoiceConsent], voice_consent, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.audio.voice_consents.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            voice_consent = await response.parse()
            assert_matches_type(AsyncCursorPage[VoiceConsent], voice_consent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        voice_consent = await async_client.audio.voice_consents.delete(
            "consent_id",
        )
        assert_matches_type(VoiceConsentDeleted, voice_consent, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.audio.voice_consents.with_raw_response.delete(
            "consent_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        voice_consent = response.parse()
        assert_matches_type(VoiceConsentDeleted, voice_consent, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.audio.voice_consents.with_streaming_response.delete(
            "consent_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            voice_consent = await response.parse()
            assert_matches_type(VoiceConsentDeleted, voice_consent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `consent_id` but received ''"):
            await async_client.audio.voice_consents.with_raw_response.delete(
                "",
            )
