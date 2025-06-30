# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types.audio import TranscriptionCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTranscriptions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create_overload_1(self, client: OpenAI) -> None:
        transcription = client.audio.transcriptions.create(
            file=b"raw file contents",
            model="gpt-4o-transcribe",
        )
        assert_matches_type(TranscriptionCreateResponse, transcription, path=["response"])

    @parametrize
    def test_method_create_with_all_params_overload_1(self, client: OpenAI) -> None:
        transcription = client.audio.transcriptions.create(
            file=b"raw file contents",
            model="gpt-4o-transcribe",
            chunking_strategy="auto",
            include=["logprobs"],
            language="language",
            prompt="prompt",
            response_format="json",
            stream=False,
            temperature=0,
            timestamp_granularities=["word"],
        )
        assert_matches_type(TranscriptionCreateResponse, transcription, path=["response"])

    @parametrize
    def test_raw_response_create_overload_1(self, client: OpenAI) -> None:
        response = client.audio.transcriptions.with_raw_response.create(
            file=b"raw file contents",
            model="gpt-4o-transcribe",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transcription = response.parse()
        assert_matches_type(TranscriptionCreateResponse, transcription, path=["response"])

    @parametrize
    def test_streaming_response_create_overload_1(self, client: OpenAI) -> None:
        with client.audio.transcriptions.with_streaming_response.create(
            file=b"raw file contents",
            model="gpt-4o-transcribe",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transcription = response.parse()
            assert_matches_type(TranscriptionCreateResponse, transcription, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_create_overload_2(self, client: OpenAI) -> None:
        transcription_stream = client.audio.transcriptions.create(
            file=b"raw file contents",
            model="gpt-4o-transcribe",
            stream=True,
        )
        transcription_stream.response.close()

    @parametrize
    def test_method_create_with_all_params_overload_2(self, client: OpenAI) -> None:
        transcription_stream = client.audio.transcriptions.create(
            file=b"raw file contents",
            model="gpt-4o-transcribe",
            stream=True,
            chunking_strategy="auto",
            include=["logprobs"],
            language="language",
            prompt="prompt",
            response_format="json",
            temperature=0,
            timestamp_granularities=["word"],
        )
        transcription_stream.response.close()

    @parametrize
    def test_raw_response_create_overload_2(self, client: OpenAI) -> None:
        response = client.audio.transcriptions.with_raw_response.create(
            file=b"raw file contents",
            model="gpt-4o-transcribe",
            stream=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        stream.close()

    @parametrize
    def test_streaming_response_create_overload_2(self, client: OpenAI) -> None:
        with client.audio.transcriptions.with_streaming_response.create(
            file=b"raw file contents",
            model="gpt-4o-transcribe",
            stream=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = response.parse()
            stream.close()

        assert cast(Any, response.is_closed) is True


class TestAsyncTranscriptions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        transcription = await async_client.audio.transcriptions.create(
            file=b"raw file contents",
            model="gpt-4o-transcribe",
        )
        assert_matches_type(TranscriptionCreateResponse, transcription, path=["response"])

    @parametrize
    async def test_method_create_with_all_params_overload_1(self, async_client: AsyncOpenAI) -> None:
        transcription = await async_client.audio.transcriptions.create(
            file=b"raw file contents",
            model="gpt-4o-transcribe",
            chunking_strategy="auto",
            include=["logprobs"],
            language="language",
            prompt="prompt",
            response_format="json",
            stream=False,
            temperature=0,
            timestamp_granularities=["word"],
        )
        assert_matches_type(TranscriptionCreateResponse, transcription, path=["response"])

    @parametrize
    async def test_raw_response_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.audio.transcriptions.with_raw_response.create(
            file=b"raw file contents",
            model="gpt-4o-transcribe",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transcription = response.parse()
        assert_matches_type(TranscriptionCreateResponse, transcription, path=["response"])

    @parametrize
    async def test_streaming_response_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        async with async_client.audio.transcriptions.with_streaming_response.create(
            file=b"raw file contents",
            model="gpt-4o-transcribe",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transcription = await response.parse()
            assert_matches_type(TranscriptionCreateResponse, transcription, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_create_overload_2(self, async_client: AsyncOpenAI) -> None:
        transcription_stream = await async_client.audio.transcriptions.create(
            file=b"raw file contents",
            model="gpt-4o-transcribe",
            stream=True,
        )
        await transcription_stream.response.aclose()

    @parametrize
    async def test_method_create_with_all_params_overload_2(self, async_client: AsyncOpenAI) -> None:
        transcription_stream = await async_client.audio.transcriptions.create(
            file=b"raw file contents",
            model="gpt-4o-transcribe",
            stream=True,
            chunking_strategy="auto",
            include=["logprobs"],
            language="language",
            prompt="prompt",
            response_format="json",
            temperature=0,
            timestamp_granularities=["word"],
        )
        await transcription_stream.response.aclose()

    @parametrize
    async def test_raw_response_create_overload_2(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.audio.transcriptions.with_raw_response.create(
            file=b"raw file contents",
            model="gpt-4o-transcribe",
            stream=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        await stream.close()

    @parametrize
    async def test_streaming_response_create_overload_2(self, async_client: AsyncOpenAI) -> None:
        async with async_client.audio.transcriptions.with_streaming_response.create(
            file=b"raw file contents",
            model="gpt-4o-transcribe",
            stream=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = await response.parse()
            await stream.close()

        assert cast(Any, response.is_closed) is True
