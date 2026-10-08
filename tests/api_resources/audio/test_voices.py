# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types.audio import Voice

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestVoices:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create_overload_1(self, client: OpenAI) -> None:
        voice = client.audio.voices.create(
            audio_sample=b"Example data",
            consent="consent",
            name="x",
        )
        assert_matches_type(Voice, voice, path=["response"])

    @parametrize
    def test_method_create_with_all_params_overload_1(self, client: OpenAI) -> None:
        voice = client.audio.voices.create(
            audio_sample=b"Example data",
            consent="consent",
            name="x",
            type="audio_sample",
        )
        assert_matches_type(Voice, voice, path=["response"])

    @parametrize
    def test_raw_response_create_overload_1(self, client: OpenAI) -> None:
        response = client.audio.voices.with_raw_response.create(
            audio_sample=b"Example data",
            consent="consent",
            name="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        voice = response.parse()
        assert_matches_type(Voice, voice, path=["response"])

    @parametrize
    def test_streaming_response_create_overload_1(self, client: OpenAI) -> None:
        with client.audio.voices.with_streaming_response.create(
            audio_sample=b"Example data",
            consent="consent",
            name="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            voice = response.parse()
            assert_matches_type(Voice, voice, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncVoices:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        voice = await async_client.audio.voices.create(
            audio_sample=b"Example data",
            consent="consent",
            name="x",
        )
        assert_matches_type(Voice, voice, path=["response"])

    @parametrize
    async def test_method_create_with_all_params_overload_1(self, async_client: AsyncOpenAI) -> None:
        voice = await async_client.audio.voices.create(
            audio_sample=b"Example data",
            consent="consent",
            name="x",
            type="audio_sample",
        )
        assert_matches_type(Voice, voice, path=["response"])

    @parametrize
    async def test_raw_response_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.audio.voices.with_raw_response.create(
            audio_sample=b"Example data",
            consent="consent",
            name="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        voice = response.parse()
        assert_matches_type(Voice, voice, path=["response"])

    @parametrize
    async def test_streaming_response_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        async with async_client.audio.voices.with_streaming_response.create(
            audio_sample=b"Example data",
            consent="consent",
            name="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            voice = await response.parse()
            assert_matches_type(Voice, voice, path=["response"])

        assert cast(Any, response.is_closed) is True
