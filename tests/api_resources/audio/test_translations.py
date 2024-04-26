# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types.audio import Translation

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTranslations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        translation = client.audio.translations.create(
            file=b"raw file contents",
            model="whisper-1",
        )
        assert_matches_type(Translation, translation, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        translation = client.audio.translations.create(
            file=b"raw file contents",
            model="whisper-1",
            prompt="string",
            response_format="string",
            temperature=0,
        )
        assert_matches_type(Translation, translation, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.audio.translations.with_raw_response.create(
            file=b"raw file contents",
            model="whisper-1",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        translation = response.parse()
        assert_matches_type(Translation, translation, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.audio.translations.with_streaming_response.create(
            file=b"raw file contents",
            model="whisper-1",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            translation = response.parse()
            assert_matches_type(Translation, translation, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncTranslations:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        translation = await async_client.audio.translations.create(
            file=b"raw file contents",
            model="whisper-1",
        )
        assert_matches_type(Translation, translation, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        translation = await async_client.audio.translations.create(
            file=b"raw file contents",
            model="whisper-1",
            prompt="string",
            response_format="string",
            temperature=0,
        )
        assert_matches_type(Translation, translation, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.audio.translations.with_raw_response.create(
            file=b"raw file contents",
            model="whisper-1",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        translation = response.parse()
        assert_matches_type(Translation, translation, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.audio.translations.with_streaming_response.create(
            file=b"raw file contents",
            model="whisper-1",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            translation = await response.parse()
            assert_matches_type(Translation, translation, path=["response"])

        assert cast(Any, response.is_closed) is True
