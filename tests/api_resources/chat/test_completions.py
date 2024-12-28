# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest
import pydantic

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types.chat import (
    ChatCompletion,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCompletions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create_overload_1(self, client: OpenAI) -> None:
        completion = client.chat.completions.create(
            messages=[
                {
                    "content": "string",
                    "role": "developer",
                }
            ],
            model="gpt-4o",
        )
        assert_matches_type(ChatCompletion, completion, path=["response"])

    @parametrize
    def test_method_create_with_all_params_overload_1(self, client: OpenAI) -> None:
        completion = client.chat.completions.create(
            messages=[
                {
                    "content": "string",
                    "role": "developer",
                    "name": "name",
                }
            ],
            model="gpt-4o",
            audio={
                "format": "wav",
                "voice": "alloy",
            },
            frequency_penalty=-2,
            function_call="none",
            functions=[
                {
                    "name": "name",
                    "description": "description",
                    "parameters": {"foo": "bar"},
                }
            ],
            logit_bias={"foo": 0},
            logprobs=True,
            max_completion_tokens=0,
            max_tokens=0,
            metadata={"foo": "string"},
            modalities=["text"],
            n=1,
            parallel_tool_calls=True,
            prediction={
                "content": "string",
                "type": "content",
            },
            presence_penalty=-2,
            reasoning_effort="low",
            response_format={"type": "text"},
            seed=-9007199254740991,
            service_tier="auto",
            stop="string",
            store=True,
            stream=False,
            stream_options={"include_usage": True},
            temperature=1,
            tool_choice="none",
            tools=[
                {
                    "function": {
                        "name": "name",
                        "description": "description",
                        "parameters": {"foo": "bar"},
                        "strict": True,
                    },
                    "type": "function",
                }
            ],
            top_logprobs=0,
            top_p=1,
            user="user-1234",
        )
        assert_matches_type(ChatCompletion, completion, path=["response"])

    @parametrize
    def test_raw_response_create_overload_1(self, client: OpenAI) -> None:
        response = client.chat.completions.with_raw_response.create(
            messages=[
                {
                    "content": "string",
                    "role": "developer",
                }
            ],
            model="gpt-4o",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        completion = response.parse()
        assert_matches_type(ChatCompletion, completion, path=["response"])

    @parametrize
    def test_streaming_response_create_overload_1(self, client: OpenAI) -> None:
        with client.chat.completions.with_streaming_response.create(
            messages=[
                {
                    "content": "string",
                    "role": "developer",
                }
            ],
            model="gpt-4o",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            completion = response.parse()
            assert_matches_type(ChatCompletion, completion, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_create_overload_2(self, client: OpenAI) -> None:
        completion_stream = client.chat.completions.create(
            messages=[
                {
                    "content": "string",
                    "role": "developer",
                }
            ],
            model="gpt-4o",
            stream=True,
        )
        completion_stream.response.close()

    @parametrize
    def test_method_create_with_all_params_overload_2(self, client: OpenAI) -> None:
        completion_stream = client.chat.completions.create(
            messages=[
                {
                    "content": "string",
                    "role": "developer",
                    "name": "name",
                }
            ],
            model="gpt-4o",
            stream=True,
            audio={
                "format": "wav",
                "voice": "alloy",
            },
            frequency_penalty=-2,
            function_call="none",
            functions=[
                {
                    "name": "name",
                    "description": "description",
                    "parameters": {"foo": "bar"},
                }
            ],
            logit_bias={"foo": 0},
            logprobs=True,
            max_completion_tokens=0,
            max_tokens=0,
            metadata={"foo": "string"},
            modalities=["text"],
            n=1,
            parallel_tool_calls=True,
            prediction={
                "content": "string",
                "type": "content",
            },
            presence_penalty=-2,
            reasoning_effort="low",
            response_format={"type": "text"},
            seed=-9007199254740991,
            service_tier="auto",
            stop="string",
            store=True,
            stream_options={"include_usage": True},
            temperature=1,
            tool_choice="none",
            tools=[
                {
                    "function": {
                        "name": "name",
                        "description": "description",
                        "parameters": {"foo": "bar"},
                        "strict": True,
                    },
                    "type": "function",
                }
            ],
            top_logprobs=0,
            top_p=1,
            user="user-1234",
        )
        completion_stream.response.close()

    @parametrize
    def test_raw_response_create_overload_2(self, client: OpenAI) -> None:
        response = client.chat.completions.with_raw_response.create(
            messages=[
                {
                    "content": "string",
                    "role": "developer",
                }
            ],
            model="gpt-4o",
            stream=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        stream.close()

    @parametrize
    def test_streaming_response_create_overload_2(self, client: OpenAI) -> None:
        with client.chat.completions.with_streaming_response.create(
            messages=[
                {
                    "content": "string",
                    "role": "developer",
                }
            ],
            model="gpt-4o",
            stream=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = response.parse()
            stream.close()

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_create_disallows_pydantic(self, client: OpenAI) -> None:
        class MyModel(pydantic.BaseModel):
            a: str

        with pytest.raises(TypeError, match=r"You tried to pass a `BaseModel` class"):
            client.chat.completions.create(
                messages=[
                    {
                        "content": "string",
                        "role": "system",
                    }
                ],
                model="gpt-4o",
                response_format=cast(Any, MyModel),
            )


class TestAsyncCompletions:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        completion = await async_client.chat.completions.create(
            messages=[
                {
                    "content": "string",
                    "role": "developer",
                }
            ],
            model="gpt-4o",
        )
        assert_matches_type(ChatCompletion, completion, path=["response"])

    @parametrize
    async def test_method_create_with_all_params_overload_1(self, async_client: AsyncOpenAI) -> None:
        completion = await async_client.chat.completions.create(
            messages=[
                {
                    "content": "string",
                    "role": "developer",
                    "name": "name",
                }
            ],
            model="gpt-4o",
            audio={
                "format": "wav",
                "voice": "alloy",
            },
            frequency_penalty=-2,
            function_call="none",
            functions=[
                {
                    "name": "name",
                    "description": "description",
                    "parameters": {"foo": "bar"},
                }
            ],
            logit_bias={"foo": 0},
            logprobs=True,
            max_completion_tokens=0,
            max_tokens=0,
            metadata={"foo": "string"},
            modalities=["text"],
            n=1,
            parallel_tool_calls=True,
            prediction={
                "content": "string",
                "type": "content",
            },
            presence_penalty=-2,
            reasoning_effort="low",
            response_format={"type": "text"},
            seed=-9007199254740991,
            service_tier="auto",
            stop="string",
            store=True,
            stream=False,
            stream_options={"include_usage": True},
            temperature=1,
            tool_choice="none",
            tools=[
                {
                    "function": {
                        "name": "name",
                        "description": "description",
                        "parameters": {"foo": "bar"},
                        "strict": True,
                    },
                    "type": "function",
                }
            ],
            top_logprobs=0,
            top_p=1,
            user="user-1234",
        )
        assert_matches_type(ChatCompletion, completion, path=["response"])

    @parametrize
    async def test_raw_response_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.chat.completions.with_raw_response.create(
            messages=[
                {
                    "content": "string",
                    "role": "developer",
                }
            ],
            model="gpt-4o",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        completion = response.parse()
        assert_matches_type(ChatCompletion, completion, path=["response"])

    @parametrize
    async def test_streaming_response_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        async with async_client.chat.completions.with_streaming_response.create(
            messages=[
                {
                    "content": "string",
                    "role": "developer",
                }
            ],
            model="gpt-4o",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            completion = await response.parse()
            assert_matches_type(ChatCompletion, completion, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_create_overload_2(self, async_client: AsyncOpenAI) -> None:
        completion_stream = await async_client.chat.completions.create(
            messages=[
                {
                    "content": "string",
                    "role": "developer",
                }
            ],
            model="gpt-4o",
            stream=True,
        )
        await completion_stream.response.aclose()

    @parametrize
    async def test_method_create_with_all_params_overload_2(self, async_client: AsyncOpenAI) -> None:
        completion_stream = await async_client.chat.completions.create(
            messages=[
                {
                    "content": "string",
                    "role": "developer",
                    "name": "name",
                }
            ],
            model="gpt-4o",
            stream=True,
            audio={
                "format": "wav",
                "voice": "alloy",
            },
            frequency_penalty=-2,
            function_call="none",
            functions=[
                {
                    "name": "name",
                    "description": "description",
                    "parameters": {"foo": "bar"},
                }
            ],
            logit_bias={"foo": 0},
            logprobs=True,
            max_completion_tokens=0,
            max_tokens=0,
            metadata={"foo": "string"},
            modalities=["text"],
            n=1,
            parallel_tool_calls=True,
            prediction={
                "content": "string",
                "type": "content",
            },
            presence_penalty=-2,
            reasoning_effort="low",
            response_format={"type": "text"},
            seed=-9007199254740991,
            service_tier="auto",
            stop="string",
            store=True,
            stream_options={"include_usage": True},
            temperature=1,
            tool_choice="none",
            tools=[
                {
                    "function": {
                        "name": "name",
                        "description": "description",
                        "parameters": {"foo": "bar"},
                        "strict": True,
                    },
                    "type": "function",
                }
            ],
            top_logprobs=0,
            top_p=1,
            user="user-1234",
        )
        await completion_stream.response.aclose()

    @parametrize
    async def test_raw_response_create_overload_2(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.chat.completions.with_raw_response.create(
            messages=[
                {
                    "content": "string",
                    "role": "developer",
                }
            ],
            model="gpt-4o",
            stream=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        await stream.close()

    @parametrize
    async def test_streaming_response_create_overload_2(self, async_client: AsyncOpenAI) -> None:
        async with async_client.chat.completions.with_streaming_response.create(
            messages=[
                {
                    "content": "string",
                    "role": "developer",
                }
            ],
            model="gpt-4o",
            stream=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = await response.parse()
            await stream.close()

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_create_disallows_pydantic(self, async_client: AsyncOpenAI) -> None:
        class MyModel(pydantic.BaseModel):
            a: str

        with pytest.raises(TypeError, match=r"You tried to pass a `BaseModel` class"):
            await async_client.chat.completions.create(
                messages=[
                    {
                        "content": "string",
                        "role": "system",
                    }
                ],
                model="gpt-4o",
                response_format=cast(Any, MyModel),
            )
