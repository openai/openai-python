# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter

import openai._legacy_response as _legacy_response
from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type

# pyright: reportDeprecated=false

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSpeech:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_create(self, client: OpenAI, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        speech = client.audio.speech.create(
            input="string",
            model="string",
            voice="alloy",
        )
        assert isinstance(speech, _legacy_response.HttpxBinaryResponseContent)
        assert speech.json() == {"foo": "bar"}

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_create_with_all_params(self, client: OpenAI, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        speech = client.audio.speech.create(
            input="string",
            model="string",
            voice="alloy",
            response_format="mp3",
            speed=0.25,
        )
        assert isinstance(speech, _legacy_response.HttpxBinaryResponseContent)
        assert speech.json() == {"foo": "bar"}

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_create(self, client: OpenAI, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        response = client.audio.speech.with_raw_response.create(
            input="string",
            model="string",
            voice="alloy",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        speech = response.parse()
        assert_matches_type(_legacy_response.HttpxBinaryResponseContent, speech, path=["response"])

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_create(self, client: OpenAI, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        with client.audio.speech.with_streaming_response.create(
            input="string",
            model="string",
            voice="alloy",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            speech = response.parse()
            assert_matches_type(bytes, speech, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSpeech:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_create(self, async_client: AsyncOpenAI, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        speech = await async_client.audio.speech.create(
            input="string",
            model="string",
            voice="alloy",
        )
        assert isinstance(speech, _legacy_response.HttpxBinaryResponseContent)
        assert speech.json() == {"foo": "bar"}

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        speech = await async_client.audio.speech.create(
            input="string",
            model="string",
            voice="alloy",
            response_format="mp3",
            speed=0.25,
        )
        assert isinstance(speech, _legacy_response.HttpxBinaryResponseContent)
        assert speech.json() == {"foo": "bar"}

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_create(self, async_client: AsyncOpenAI, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        response = await async_client.audio.speech.with_raw_response.create(
            input="string",
            model="string",
            voice="alloy",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        speech = response.parse()
        assert_matches_type(_legacy_response.HttpxBinaryResponseContent, speech, path=["response"])

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_create(self, async_client: AsyncOpenAI, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        async with async_client.audio.speech.with_streaming_response.create(
            input="string",
            model="string",
            voice="alloy",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            speech = await response.parse()
            assert_matches_type(bytes, speech, path=["response"])

        assert cast(Any, response.is_closed) is True
