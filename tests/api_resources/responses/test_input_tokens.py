# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types.responses import InputTokenCountResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestInputTokens:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_count(self, client: OpenAI) -> None:
        input_token = client.responses.input_tokens.count()
        assert_matches_type(InputTokenCountResponse, input_token, path=["response"])

    @parametrize
    def test_method_count_with_all_params(self, client: OpenAI) -> None:
        input_token = client.responses.input_tokens.count(
            conversation="string",
            input="string",
            instructions="instructions",
            model="model",
            parallel_tool_calls=True,
            previous_response_id="resp_123",
            reasoning={
                "effort": "none",
                "generate_summary": "auto",
                "summary": "auto",
            },
            text={
                "format": {"type": "text"},
                "verbosity": "low",
            },
            tool_choice="none",
            tools=[
                {
                    "name": "name",
                    "parameters": {"foo": "bar"},
                    "strict": True,
                    "type": "function",
                    "description": "description",
                }
            ],
            truncation="auto",
        )
        assert_matches_type(InputTokenCountResponse, input_token, path=["response"])

    @parametrize
    def test_raw_response_count(self, client: OpenAI) -> None:
        response = client.responses.input_tokens.with_raw_response.count()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        input_token = response.parse()
        assert_matches_type(InputTokenCountResponse, input_token, path=["response"])

    @parametrize
    def test_streaming_response_count(self, client: OpenAI) -> None:
        with client.responses.input_tokens.with_streaming_response.count() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            input_token = response.parse()
            assert_matches_type(InputTokenCountResponse, input_token, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncInputTokens:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_count(self, async_client: AsyncOpenAI) -> None:
        input_token = await async_client.responses.input_tokens.count()
        assert_matches_type(InputTokenCountResponse, input_token, path=["response"])

    @parametrize
    async def test_method_count_with_all_params(self, async_client: AsyncOpenAI) -> None:
        input_token = await async_client.responses.input_tokens.count(
            conversation="string",
            input="string",
            instructions="instructions",
            model="model",
            parallel_tool_calls=True,
            previous_response_id="resp_123",
            reasoning={
                "effort": "none",
                "generate_summary": "auto",
                "summary": "auto",
            },
            text={
                "format": {"type": "text"},
                "verbosity": "low",
            },
            tool_choice="none",
            tools=[
                {
                    "name": "name",
                    "parameters": {"foo": "bar"},
                    "strict": True,
                    "type": "function",
                    "description": "description",
                }
            ],
            truncation="auto",
        )
        assert_matches_type(InputTokenCountResponse, input_token, path=["response"])

    @parametrize
    async def test_raw_response_count(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.responses.input_tokens.with_raw_response.count()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        input_token = response.parse()
        assert_matches_type(InputTokenCountResponse, input_token, path=["response"])

    @parametrize
    async def test_streaming_response_count(self, async_client: AsyncOpenAI) -> None:
        async with async_client.responses.input_tokens.with_streaming_response.count() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            input_token = await response.parse()
            assert_matches_type(InputTokenCountResponse, input_token, path=["response"])

        assert cast(Any, response.is_closed) is True
