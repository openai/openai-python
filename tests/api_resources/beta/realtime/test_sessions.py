# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types.beta.realtime import SessionCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSessions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        session = client.beta.realtime.sessions.create()
        assert_matches_type(SessionCreateResponse, session, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        session = client.beta.realtime.sessions.create(
            input_audio_format="pcm16",
            input_audio_noise_reduction={"type": "near_field"},
            input_audio_transcription={
                "language": "language",
                "model": "model",
                "prompt": "prompt",
            },
            instructions="instructions",
            max_response_output_tokens=0,
            modalities=["text"],
            model="gpt-4o-realtime-preview",
            output_audio_format="pcm16",
            temperature=0,
            tool_choice="tool_choice",
            tools=[
                {
                    "description": "description",
                    "name": "name",
                    "parameters": {},
                    "type": "function",
                }
            ],
            turn_detection={
                "create_response": True,
                "eagerness": "low",
                "interrupt_response": True,
                "prefix_padding_ms": 0,
                "silence_duration_ms": 0,
                "threshold": 0,
                "type": "server_vad",
            },
            voice="ash",
        )
        assert_matches_type(SessionCreateResponse, session, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.beta.realtime.sessions.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionCreateResponse, session, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.beta.realtime.sessions.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(SessionCreateResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSessions:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        session = await async_client.beta.realtime.sessions.create()
        assert_matches_type(SessionCreateResponse, session, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        session = await async_client.beta.realtime.sessions.create(
            input_audio_format="pcm16",
            input_audio_noise_reduction={"type": "near_field"},
            input_audio_transcription={
                "language": "language",
                "model": "model",
                "prompt": "prompt",
            },
            instructions="instructions",
            max_response_output_tokens=0,
            modalities=["text"],
            model="gpt-4o-realtime-preview",
            output_audio_format="pcm16",
            temperature=0,
            tool_choice="tool_choice",
            tools=[
                {
                    "description": "description",
                    "name": "name",
                    "parameters": {},
                    "type": "function",
                }
            ],
            turn_detection={
                "create_response": True,
                "eagerness": "low",
                "interrupt_response": True,
                "prefix_padding_ms": 0,
                "silence_duration_ms": 0,
                "threshold": 0,
                "type": "server_vad",
            },
            voice="ash",
        )
        assert_matches_type(SessionCreateResponse, session, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.realtime.sessions.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionCreateResponse, session, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.realtime.sessions.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(SessionCreateResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True
