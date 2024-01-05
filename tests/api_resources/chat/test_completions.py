# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

import os

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai._client import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletion

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
api_key = "My API Key"


class TestCompletions:
    strict_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    def test_method_create_overload_1(self, client: OpenAI) -> None:
        completion = client.chat.completions.create(
            messages=[
                {
                    "content": "string",
                    "role": "system",
                }
            ],
            model="gpt-3.5-turbo",
        )
        assert_matches_type(ChatCompletion, completion, path=["response"])

    @parametrize
    def test_method_create_with_all_params_overload_1(self, client: OpenAI) -> None:
        completion = client.chat.completions.create(
            messages=[
                {
                    "content": "string",
                    "role": "system",
                    "name": "string",
                }
            ],
            model="gpt-3.5-turbo",
            frequency_penalty=-2,
            function_call="none",
            functions=[
                {
                    "description": "string",
                    "name": "string",
                    "parameters": {"foo": "bar"},
                }
            ],
            logit_bias={"foo": 0},
            logprobs=True,
            max_tokens=0,
            n=1,
            presence_penalty=-2,
            response_format={"type": "json_object"},
            seed=-9223372036854776000,
            stop="string",
            stream=False,
            temperature=1,
            tool_choice="none",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "description": "string",
                        "name": "string",
                        "parameters": {"foo": "bar"},
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "description": "string",
                        "name": "string",
                        "parameters": {"foo": "bar"},
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "description": "string",
                        "name": "string",
                        "parameters": {"foo": "bar"},
                    },
                },
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
                    "role": "system",
                }
            ],
            model="gpt-3.5-turbo",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        completion = response.parse()
        assert_matches_type(ChatCompletion, completion, path=["response"])

    @parametrize
    def test_method_create_overload_2(self, client: OpenAI) -> None:
        client.chat.completions.create(
            messages=[
                {
                    "content": "string",
                    "role": "system",
                }
            ],
            model="gpt-3.5-turbo",
            stream=True,
        )

    @parametrize
    def test_method_create_with_all_params_overload_2(self, client: OpenAI) -> None:
        client.chat.completions.create(
            messages=[
                {
                    "content": "string",
                    "role": "system",
                    "name": "string",
                }
            ],
            model="gpt-3.5-turbo",
            stream=True,
            frequency_penalty=-2,
            function_call="none",
            functions=[
                {
                    "description": "string",
                    "name": "string",
                    "parameters": {"foo": "bar"},
                }
            ],
            logit_bias={"foo": 0},
            logprobs=True,
            max_tokens=0,
            n=1,
            presence_penalty=-2,
            response_format={"type": "json_object"},
            seed=-9223372036854776000,
            stop="string",
            temperature=1,
            tool_choice="none",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "description": "string",
                        "name": "string",
                        "parameters": {"foo": "bar"},
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "description": "string",
                        "name": "string",
                        "parameters": {"foo": "bar"},
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "description": "string",
                        "name": "string",
                        "parameters": {"foo": "bar"},
                    },
                },
            ],
            top_logprobs=0,
            top_p=1,
            user="user-1234",
        )

    @parametrize
    def test_raw_response_create_overload_2(self, client: OpenAI) -> None:
        response = client.chat.completions.with_raw_response.create(
            messages=[
                {
                    "content": "string",
                    "role": "system",
                }
            ],
            model="gpt-3.5-turbo",
            stream=True,
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        response.parse()


class TestAsyncCompletions:
    strict_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    async def test_method_create_overload_1(self, client: AsyncOpenAI) -> None:
        completion = await client.chat.completions.create(
            messages=[
                {
                    "content": "string",
                    "role": "system",
                }
            ],
            model="gpt-3.5-turbo",
        )
        assert_matches_type(ChatCompletion, completion, path=["response"])

    @parametrize
    async def test_method_create_with_all_params_overload_1(self, client: AsyncOpenAI) -> None:
        completion = await client.chat.completions.create(
            messages=[
                {
                    "content": "string",
                    "role": "system",
                    "name": "string",
                }
            ],
            model="gpt-3.5-turbo",
            frequency_penalty=-2,
            function_call="none",
            functions=[
                {
                    "description": "string",
                    "name": "string",
                    "parameters": {"foo": "bar"},
                }
            ],
            logit_bias={"foo": 0},
            logprobs=True,
            max_tokens=0,
            n=1,
            presence_penalty=-2,
            response_format={"type": "json_object"},
            seed=-9223372036854776000,
            stop="string",
            stream=False,
            temperature=1,
            tool_choice="none",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "description": "string",
                        "name": "string",
                        "parameters": {"foo": "bar"},
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "description": "string",
                        "name": "string",
                        "parameters": {"foo": "bar"},
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "description": "string",
                        "name": "string",
                        "parameters": {"foo": "bar"},
                    },
                },
            ],
            top_logprobs=0,
            top_p=1,
            user="user-1234",
        )
        assert_matches_type(ChatCompletion, completion, path=["response"])

    @parametrize
    async def test_raw_response_create_overload_1(self, client: AsyncOpenAI) -> None:
        response = await client.chat.completions.with_raw_response.create(
            messages=[
                {
                    "content": "string",
                    "role": "system",
                }
            ],
            model="gpt-3.5-turbo",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        completion = response.parse()
        assert_matches_type(ChatCompletion, completion, path=["response"])

    @parametrize
    async def test_method_create_overload_2(self, client: AsyncOpenAI) -> None:
        await client.chat.completions.create(
            messages=[
                {
                    "content": "string",
                    "role": "system",
                }
            ],
            model="gpt-3.5-turbo",
            stream=True,
        )

    @parametrize
    async def test_method_create_with_all_params_overload_2(self, client: AsyncOpenAI) -> None:
        await client.chat.completions.create(
            messages=[
                {
                    "content": "string",
                    "role": "system",
                    "name": "string",
                }
            ],
            model="gpt-3.5-turbo",
            stream=True,
            frequency_penalty=-2,
            function_call="none",
            functions=[
                {
                    "description": "string",
                    "name": "string",
                    "parameters": {"foo": "bar"},
                }
            ],
            logit_bias={"foo": 0},
            logprobs=True,
            max_tokens=0,
            n=1,
            presence_penalty=-2,
            response_format={"type": "json_object"},
            seed=-9223372036854776000,
            stop="string",
            temperature=1,
            tool_choice="none",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "description": "string",
                        "name": "string",
                        "parameters": {"foo": "bar"},
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "description": "string",
                        "name": "string",
                        "parameters": {"foo": "bar"},
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "description": "string",
                        "name": "string",
                        "parameters": {"foo": "bar"},
                    },
                },
            ],
            top_logprobs=0,
            top_p=1,
            user="user-1234",
        )

    @parametrize
    async def test_raw_response_create_overload_2(self, client: AsyncOpenAI) -> None:
        response = await client.chat.completions.with_raw_response.create(
            messages=[
                {
                    "content": "string",
                    "role": "system",
                }
            ],
            model="gpt-3.5-turbo",
            stream=True,
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        response.parse()
