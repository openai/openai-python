# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types.realtime import ClientSecretCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestClientSecrets:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        client_secret = client.realtime.client_secrets.create()
        assert_matches_type(ClientSecretCreateResponse, client_secret, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        client_secret = client.realtime.client_secrets.create(
            expires_after={
                "anchor": "created_at",
                "seconds": 10,
            },
            session={
                "model": "string",
                "type": "realtime",
                "audio": {
                    "input": {
                        "format": "pcm16",
                        "noise_reduction": {"type": "near_field"},
                        "transcription": {
                            "language": "language",
                            "model": "whisper-1",
                            "prompt": "prompt",
                        },
                        "turn_detection": {
                            "create_response": True,
                            "eagerness": "low",
                            "idle_timeout_ms": 0,
                            "interrupt_response": True,
                            "prefix_padding_ms": 0,
                            "silence_duration_ms": 0,
                            "threshold": 0,
                            "type": "server_vad",
                        },
                    },
                    "output": {
                        "format": "pcm16",
                        "speed": 0.25,
                        "voice": "ash",
                    },
                },
                "client_secret": {
                    "expires_after": {
                        "anchor": "created_at",
                        "seconds": 0,
                    }
                },
                "include": ["item.input_audio_transcription.logprobs"],
                "instructions": "instructions",
                "max_output_tokens": 0,
                "output_modalities": ["text"],
                "prompt": {
                    "id": "id",
                    "variables": {"foo": "string"},
                    "version": "version",
                },
                "temperature": 0,
                "tool_choice": "none",
                "tools": [
                    {
                        "description": "description",
                        "name": "name",
                        "parameters": {},
                        "type": "function",
                    }
                ],
                "tracing": "auto",
                "truncation": "auto",
            },
        )
        assert_matches_type(ClientSecretCreateResponse, client_secret, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.realtime.client_secrets.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_secret = response.parse()
        assert_matches_type(ClientSecretCreateResponse, client_secret, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.realtime.client_secrets.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_secret = response.parse()
            assert_matches_type(ClientSecretCreateResponse, client_secret, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncClientSecrets:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        client_secret = await async_client.realtime.client_secrets.create()
        assert_matches_type(ClientSecretCreateResponse, client_secret, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        client_secret = await async_client.realtime.client_secrets.create(
            expires_after={
                "anchor": "created_at",
                "seconds": 10,
            },
            session={
                "model": "string",
                "type": "realtime",
                "audio": {
                    "input": {
                        "format": "pcm16",
                        "noise_reduction": {"type": "near_field"},
                        "transcription": {
                            "language": "language",
                            "model": "whisper-1",
                            "prompt": "prompt",
                        },
                        "turn_detection": {
                            "create_response": True,
                            "eagerness": "low",
                            "idle_timeout_ms": 0,
                            "interrupt_response": True,
                            "prefix_padding_ms": 0,
                            "silence_duration_ms": 0,
                            "threshold": 0,
                            "type": "server_vad",
                        },
                    },
                    "output": {
                        "format": "pcm16",
                        "speed": 0.25,
                        "voice": "ash",
                    },
                },
                "client_secret": {
                    "expires_after": {
                        "anchor": "created_at",
                        "seconds": 0,
                    }
                },
                "include": ["item.input_audio_transcription.logprobs"],
                "instructions": "instructions",
                "max_output_tokens": 0,
                "output_modalities": ["text"],
                "prompt": {
                    "id": "id",
                    "variables": {"foo": "string"},
                    "version": "version",
                },
                "temperature": 0,
                "tool_choice": "none",
                "tools": [
                    {
                        "description": "description",
                        "name": "name",
                        "parameters": {},
                        "type": "function",
                    }
                ],
                "tracing": "auto",
                "truncation": "auto",
            },
        )
        assert_matches_type(ClientSecretCreateResponse, client_secret, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.realtime.client_secrets.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_secret = response.parse()
        assert_matches_type(ClientSecretCreateResponse, client_secret, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.realtime.client_secrets.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_secret = await response.parse()
            assert_matches_type(ClientSecretCreateResponse, client_secret, path=["response"])

        assert cast(Any, response.is_closed) is True
