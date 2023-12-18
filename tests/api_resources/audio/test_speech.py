# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

import os

import httpx
import pytest
from respx import MockRouter

from openai import OpenAI, AsyncOpenAI
from openai._types import BinaryResponseContent
from openai._client import OpenAI, AsyncOpenAI

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
api_key = "My API Key"


class TestSpeech:
    strict_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @pytest.mark.skip(reason="Mocked tests are currently broken")
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_create(self, client: OpenAI, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        speech = client.audio.speech.create(
            input="string",
            model="string",
            voice="alloy",
        )
        assert isinstance(speech, BinaryResponseContent)
        assert speech.json() == {"foo": "bar"}

    @pytest.mark.skip(reason="Mocked tests are currently broken")
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
        assert isinstance(speech, BinaryResponseContent)
        assert speech.json() == {"foo": "bar"}

    @pytest.mark.skip(reason="Mocked tests are currently broken")
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_create(self, client: OpenAI, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        response = client.audio.speech.with_raw_response.create(
            input="string",
            model="string",
            voice="alloy",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        speech = response.parse()
        assert isinstance(speech, BinaryResponseContent)
        assert speech.json() == {"foo": "bar"}


class TestAsyncSpeech:
    strict_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @pytest.mark.skip(reason="Mocked tests are currently broken")
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_create(self, client: AsyncOpenAI, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        speech = await client.audio.speech.create(
            input="string",
            model="string",
            voice="alloy",
        )
        assert isinstance(speech, BinaryResponseContent)
        assert speech.json() == {"foo": "bar"}

    @pytest.mark.skip(reason="Mocked tests are currently broken")
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_create_with_all_params(self, client: AsyncOpenAI, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        speech = await client.audio.speech.create(
            input="string",
            model="string",
            voice="alloy",
            response_format="mp3",
            speed=0.25,
        )
        assert isinstance(speech, BinaryResponseContent)
        assert speech.json() == {"foo": "bar"}

    @pytest.mark.skip(reason="Mocked tests are currently broken")
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_create(self, client: AsyncOpenAI, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        response = await client.audio.speech.with_raw_response.create(
            input="string",
            model="string",
            voice="alloy",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        speech = response.parse()
        assert isinstance(speech, BinaryResponseContent)
        assert speech.json() == {"foo": "bar"}
