# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types.realtime import RealtimeTranslationClientSecretCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestClientSecrets:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        client_secret = client.realtime.translations.client_secrets.create(
            session={"model": "model"},
        )
        assert_matches_type(RealtimeTranslationClientSecretCreateResponse, client_secret, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        client_secret = client.realtime.translations.client_secrets.create(
            session={
                "model": "model",
                "audio": {
                    "input": {
                        "noise_reduction": {"type": "near_field"},
                        "transcription": {"model": "model"},
                    },
                    "output": {"language": "language"},
                },
            },
            expires_after={
                "anchor": "created_at",
                "seconds": 10,
            },
        )
        assert_matches_type(RealtimeTranslationClientSecretCreateResponse, client_secret, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.realtime.translations.client_secrets.with_raw_response.create(
            session={"model": "model"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_secret = response.parse()
        assert_matches_type(RealtimeTranslationClientSecretCreateResponse, client_secret, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.realtime.translations.client_secrets.with_streaming_response.create(
            session={"model": "model"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_secret = response.parse()
            assert_matches_type(RealtimeTranslationClientSecretCreateResponse, client_secret, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncClientSecrets:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        client_secret = await async_client.realtime.translations.client_secrets.create(
            session={"model": "model"},
        )
        assert_matches_type(RealtimeTranslationClientSecretCreateResponse, client_secret, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        client_secret = await async_client.realtime.translations.client_secrets.create(
            session={
                "model": "model",
                "audio": {
                    "input": {
                        "noise_reduction": {"type": "near_field"},
                        "transcription": {"model": "model"},
                    },
                    "output": {"language": "language"},
                },
            },
            expires_after={
                "anchor": "created_at",
                "seconds": 10,
            },
        )
        assert_matches_type(RealtimeTranslationClientSecretCreateResponse, client_secret, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.realtime.translations.client_secrets.with_raw_response.create(
            session={"model": "model"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_secret = response.parse()
        assert_matches_type(RealtimeTranslationClientSecretCreateResponse, client_secret, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.realtime.translations.client_secrets.with_streaming_response.create(
            session={"model": "model"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_secret = await response.parse()
            assert_matches_type(RealtimeTranslationClientSecretCreateResponse, client_secret, path=["response"])

        assert cast(Any, response.is_closed) is True
