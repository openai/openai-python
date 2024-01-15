# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai._client import OpenAI, AsyncOpenAI
from openai.types.audio import Transcription

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
api_key = "My API Key"


class TestTranscriptions:
    strict_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        transcription = client.audio.transcriptions.create(
            file=b"raw file contents",
            model="whisper-1",
        )
        assert_matches_type(Transcription, transcription, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        transcription = client.audio.transcriptions.create(
            file=b"raw file contents",
            model="whisper-1",
            language="string",
            prompt="string",
            response_format="json",
            temperature=0,
        )
        assert_matches_type(Transcription, transcription, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.audio.transcriptions.with_raw_response.create(
            file=b"raw file contents",
            model="whisper-1",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transcription = response.parse()
        assert_matches_type(Transcription, transcription, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.audio.transcriptions.with_streaming_response.create(
            file=b"raw file contents",
            model="whisper-1",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transcription = response.parse()
            assert_matches_type(Transcription, transcription, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncTranscriptions:
    strict_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    async def test_method_create(self, client: AsyncOpenAI) -> None:
        transcription = await client.audio.transcriptions.create(
            file=b"raw file contents",
            model="whisper-1",
        )
        assert_matches_type(Transcription, transcription, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, client: AsyncOpenAI) -> None:
        transcription = await client.audio.transcriptions.create(
            file=b"raw file contents",
            model="whisper-1",
            language="string",
            prompt="string",
            response_format="json",
            temperature=0,
        )
        assert_matches_type(Transcription, transcription, path=["response"])

    @parametrize
    async def test_raw_response_create(self, client: AsyncOpenAI) -> None:
        response = await client.audio.transcriptions.with_raw_response.create(
            file=b"raw file contents",
            model="whisper-1",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transcription = response.parse()
        assert_matches_type(Transcription, transcription, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, client: AsyncOpenAI) -> None:
        async with client.audio.transcriptions.with_streaming_response.create(
            file=b"raw file contents",
            model="whisper-1",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transcription = await response.parse()
            assert_matches_type(Transcription, transcription, path=["response"])

        assert cast(Any, response.is_closed) is True
