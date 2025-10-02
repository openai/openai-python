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


class TestCalls:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_create(self, client: OpenAI, respx_mock: MockRouter) -> None:
        respx_mock.post("/realtime/calls").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        call = client.realtime.calls.create(
            sdp="sdp",
        )
        assert isinstance(call, _legacy_response.HttpxBinaryResponseContent)
        assert call.json() == {"foo": "bar"}

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_create_with_all_params(self, client: OpenAI, respx_mock: MockRouter) -> None:
        respx_mock.post("/realtime/calls").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        call = client.realtime.calls.create(
            sdp="sdp",
            session={
                "type": "realtime",
                "audio": {
                    "input": {
                        "format": {
                            "rate": 24000,
                            "type": "audio/pcm",
                        },
                        "noise_reduction": {"type": "near_field"},
                        "transcription": {
                            "language": "language",
                            "model": "whisper-1",
                            "prompt": "prompt",
                        },
                        "turn_detection": {
                            "type": "server_vad",
                            "create_response": True,
                            "idle_timeout_ms": 5000,
                            "interrupt_response": True,
                            "prefix_padding_ms": 0,
                            "silence_duration_ms": 0,
                            "threshold": 0,
                        },
                    },
                    "output": {
                        "format": {
                            "rate": 24000,
                            "type": "audio/pcm",
                        },
                        "speed": 0.25,
                        "voice": "ash",
                    },
                },
                "include": ["item.input_audio_transcription.logprobs"],
                "instructions": "instructions",
                "max_output_tokens": 0,
                "model": "string",
                "output_modalities": ["text"],
                "prompt": {
                    "id": "id",
                    "variables": {"foo": "string"},
                    "version": "version",
                },
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
        assert isinstance(call, _legacy_response.HttpxBinaryResponseContent)
        assert call.json() == {"foo": "bar"}

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_create(self, client: OpenAI, respx_mock: MockRouter) -> None:
        respx_mock.post("/realtime/calls").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        response = client.realtime.calls.with_raw_response.create(
            sdp="sdp",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        call = response.parse()
        assert_matches_type(_legacy_response.HttpxBinaryResponseContent, call, path=["response"])

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_create(self, client: OpenAI, respx_mock: MockRouter) -> None:
        respx_mock.post("/realtime/calls").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        with client.realtime.calls.with_streaming_response.create(
            sdp="sdp",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            call = response.parse()
            assert_matches_type(bytes, call, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_accept(self, client: OpenAI) -> None:
        call = client.realtime.calls.accept(
            call_id="call_id",
            type="realtime",
        )
        assert call is None

    @parametrize
    def test_method_accept_with_all_params(self, client: OpenAI) -> None:
        call = client.realtime.calls.accept(
            call_id="call_id",
            type="realtime",
            audio={
                "input": {
                    "format": {
                        "rate": 24000,
                        "type": "audio/pcm",
                    },
                    "noise_reduction": {"type": "near_field"},
                    "transcription": {
                        "language": "language",
                        "model": "whisper-1",
                        "prompt": "prompt",
                    },
                    "turn_detection": {
                        "type": "server_vad",
                        "create_response": True,
                        "idle_timeout_ms": 5000,
                        "interrupt_response": True,
                        "prefix_padding_ms": 0,
                        "silence_duration_ms": 0,
                        "threshold": 0,
                    },
                },
                "output": {
                    "format": {
                        "rate": 24000,
                        "type": "audio/pcm",
                    },
                    "speed": 0.25,
                    "voice": "ash",
                },
            },
            include=["item.input_audio_transcription.logprobs"],
            instructions="instructions",
            max_output_tokens=0,
            model="string",
            output_modalities=["text"],
            prompt={
                "id": "id",
                "variables": {"foo": "string"},
                "version": "version",
            },
            tool_choice="none",
            tools=[
                {
                    "description": "description",
                    "name": "name",
                    "parameters": {},
                    "type": "function",
                }
            ],
            tracing="auto",
            truncation="auto",
        )
        assert call is None

    @parametrize
    def test_raw_response_accept(self, client: OpenAI) -> None:
        response = client.realtime.calls.with_raw_response.accept(
            call_id="call_id",
            type="realtime",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        call = response.parse()
        assert call is None

    @parametrize
    def test_streaming_response_accept(self, client: OpenAI) -> None:
        with client.realtime.calls.with_streaming_response.accept(
            call_id="call_id",
            type="realtime",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            call = response.parse()
            assert call is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_accept(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `call_id` but received ''"):
            client.realtime.calls.with_raw_response.accept(
                call_id="",
                type="realtime",
            )

    @parametrize
    def test_method_hangup(self, client: OpenAI) -> None:
        call = client.realtime.calls.hangup(
            "call_id",
        )
        assert call is None

    @parametrize
    def test_raw_response_hangup(self, client: OpenAI) -> None:
        response = client.realtime.calls.with_raw_response.hangup(
            "call_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        call = response.parse()
        assert call is None

    @parametrize
    def test_streaming_response_hangup(self, client: OpenAI) -> None:
        with client.realtime.calls.with_streaming_response.hangup(
            "call_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            call = response.parse()
            assert call is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_hangup(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `call_id` but received ''"):
            client.realtime.calls.with_raw_response.hangup(
                "",
            )

    @parametrize
    def test_method_refer(self, client: OpenAI) -> None:
        call = client.realtime.calls.refer(
            call_id="call_id",
            target_uri="tel:+14155550123",
        )
        assert call is None

    @parametrize
    def test_raw_response_refer(self, client: OpenAI) -> None:
        response = client.realtime.calls.with_raw_response.refer(
            call_id="call_id",
            target_uri="tel:+14155550123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        call = response.parse()
        assert call is None

    @parametrize
    def test_streaming_response_refer(self, client: OpenAI) -> None:
        with client.realtime.calls.with_streaming_response.refer(
            call_id="call_id",
            target_uri="tel:+14155550123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            call = response.parse()
            assert call is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_refer(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `call_id` but received ''"):
            client.realtime.calls.with_raw_response.refer(
                call_id="",
                target_uri="tel:+14155550123",
            )

    @parametrize
    def test_method_reject(self, client: OpenAI) -> None:
        call = client.realtime.calls.reject(
            call_id="call_id",
        )
        assert call is None

    @parametrize
    def test_method_reject_with_all_params(self, client: OpenAI) -> None:
        call = client.realtime.calls.reject(
            call_id="call_id",
            status_code=486,
        )
        assert call is None

    @parametrize
    def test_raw_response_reject(self, client: OpenAI) -> None:
        response = client.realtime.calls.with_raw_response.reject(
            call_id="call_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        call = response.parse()
        assert call is None

    @parametrize
    def test_streaming_response_reject(self, client: OpenAI) -> None:
        with client.realtime.calls.with_streaming_response.reject(
            call_id="call_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            call = response.parse()
            assert call is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_reject(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `call_id` but received ''"):
            client.realtime.calls.with_raw_response.reject(
                call_id="",
            )


class TestAsyncCalls:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_create(self, async_client: AsyncOpenAI, respx_mock: MockRouter) -> None:
        respx_mock.post("/realtime/calls").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        call = await async_client.realtime.calls.create(
            sdp="sdp",
        )
        assert isinstance(call, _legacy_response.HttpxBinaryResponseContent)
        assert call.json() == {"foo": "bar"}

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI, respx_mock: MockRouter) -> None:
        respx_mock.post("/realtime/calls").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        call = await async_client.realtime.calls.create(
            sdp="sdp",
            session={
                "type": "realtime",
                "audio": {
                    "input": {
                        "format": {
                            "rate": 24000,
                            "type": "audio/pcm",
                        },
                        "noise_reduction": {"type": "near_field"},
                        "transcription": {
                            "language": "language",
                            "model": "whisper-1",
                            "prompt": "prompt",
                        },
                        "turn_detection": {
                            "type": "server_vad",
                            "create_response": True,
                            "idle_timeout_ms": 5000,
                            "interrupt_response": True,
                            "prefix_padding_ms": 0,
                            "silence_duration_ms": 0,
                            "threshold": 0,
                        },
                    },
                    "output": {
                        "format": {
                            "rate": 24000,
                            "type": "audio/pcm",
                        },
                        "speed": 0.25,
                        "voice": "ash",
                    },
                },
                "include": ["item.input_audio_transcription.logprobs"],
                "instructions": "instructions",
                "max_output_tokens": 0,
                "model": "string",
                "output_modalities": ["text"],
                "prompt": {
                    "id": "id",
                    "variables": {"foo": "string"},
                    "version": "version",
                },
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
        assert isinstance(call, _legacy_response.HttpxBinaryResponseContent)
        assert call.json() == {"foo": "bar"}

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_create(self, async_client: AsyncOpenAI, respx_mock: MockRouter) -> None:
        respx_mock.post("/realtime/calls").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        response = await async_client.realtime.calls.with_raw_response.create(
            sdp="sdp",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        call = response.parse()
        assert_matches_type(_legacy_response.HttpxBinaryResponseContent, call, path=["response"])

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_create(self, async_client: AsyncOpenAI, respx_mock: MockRouter) -> None:
        respx_mock.post("/realtime/calls").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        async with async_client.realtime.calls.with_streaming_response.create(
            sdp="sdp",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            call = await response.parse()
            assert_matches_type(bytes, call, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_accept(self, async_client: AsyncOpenAI) -> None:
        call = await async_client.realtime.calls.accept(
            call_id="call_id",
            type="realtime",
        )
        assert call is None

    @parametrize
    async def test_method_accept_with_all_params(self, async_client: AsyncOpenAI) -> None:
        call = await async_client.realtime.calls.accept(
            call_id="call_id",
            type="realtime",
            audio={
                "input": {
                    "format": {
                        "rate": 24000,
                        "type": "audio/pcm",
                    },
                    "noise_reduction": {"type": "near_field"},
                    "transcription": {
                        "language": "language",
                        "model": "whisper-1",
                        "prompt": "prompt",
                    },
                    "turn_detection": {
                        "type": "server_vad",
                        "create_response": True,
                        "idle_timeout_ms": 5000,
                        "interrupt_response": True,
                        "prefix_padding_ms": 0,
                        "silence_duration_ms": 0,
                        "threshold": 0,
                    },
                },
                "output": {
                    "format": {
                        "rate": 24000,
                        "type": "audio/pcm",
                    },
                    "speed": 0.25,
                    "voice": "ash",
                },
            },
            include=["item.input_audio_transcription.logprobs"],
            instructions="instructions",
            max_output_tokens=0,
            model="string",
            output_modalities=["text"],
            prompt={
                "id": "id",
                "variables": {"foo": "string"},
                "version": "version",
            },
            tool_choice="none",
            tools=[
                {
                    "description": "description",
                    "name": "name",
                    "parameters": {},
                    "type": "function",
                }
            ],
            tracing="auto",
            truncation="auto",
        )
        assert call is None

    @parametrize
    async def test_raw_response_accept(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.realtime.calls.with_raw_response.accept(
            call_id="call_id",
            type="realtime",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        call = response.parse()
        assert call is None

    @parametrize
    async def test_streaming_response_accept(self, async_client: AsyncOpenAI) -> None:
        async with async_client.realtime.calls.with_streaming_response.accept(
            call_id="call_id",
            type="realtime",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            call = await response.parse()
            assert call is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_accept(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `call_id` but received ''"):
            await async_client.realtime.calls.with_raw_response.accept(
                call_id="",
                type="realtime",
            )

    @parametrize
    async def test_method_hangup(self, async_client: AsyncOpenAI) -> None:
        call = await async_client.realtime.calls.hangup(
            "call_id",
        )
        assert call is None

    @parametrize
    async def test_raw_response_hangup(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.realtime.calls.with_raw_response.hangup(
            "call_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        call = response.parse()
        assert call is None

    @parametrize
    async def test_streaming_response_hangup(self, async_client: AsyncOpenAI) -> None:
        async with async_client.realtime.calls.with_streaming_response.hangup(
            "call_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            call = await response.parse()
            assert call is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_hangup(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `call_id` but received ''"):
            await async_client.realtime.calls.with_raw_response.hangup(
                "",
            )

    @parametrize
    async def test_method_refer(self, async_client: AsyncOpenAI) -> None:
        call = await async_client.realtime.calls.refer(
            call_id="call_id",
            target_uri="tel:+14155550123",
        )
        assert call is None

    @parametrize
    async def test_raw_response_refer(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.realtime.calls.with_raw_response.refer(
            call_id="call_id",
            target_uri="tel:+14155550123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        call = response.parse()
        assert call is None

    @parametrize
    async def test_streaming_response_refer(self, async_client: AsyncOpenAI) -> None:
        async with async_client.realtime.calls.with_streaming_response.refer(
            call_id="call_id",
            target_uri="tel:+14155550123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            call = await response.parse()
            assert call is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_refer(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `call_id` but received ''"):
            await async_client.realtime.calls.with_raw_response.refer(
                call_id="",
                target_uri="tel:+14155550123",
            )

    @parametrize
    async def test_method_reject(self, async_client: AsyncOpenAI) -> None:
        call = await async_client.realtime.calls.reject(
            call_id="call_id",
        )
        assert call is None

    @parametrize
    async def test_method_reject_with_all_params(self, async_client: AsyncOpenAI) -> None:
        call = await async_client.realtime.calls.reject(
            call_id="call_id",
            status_code=486,
        )
        assert call is None

    @parametrize
    async def test_raw_response_reject(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.realtime.calls.with_raw_response.reject(
            call_id="call_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        call = response.parse()
        assert call is None

    @parametrize
    async def test_streaming_response_reject(self, async_client: AsyncOpenAI) -> None:
        async with async_client.realtime.calls.with_streaming_response.reject(
            call_id="call_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            call = await response.parse()
            assert call is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_reject(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `call_id` but received ''"):
            await async_client.realtime.calls.with_raw_response.reject(
                call_id="",
            )
