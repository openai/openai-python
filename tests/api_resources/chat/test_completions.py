# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

import os

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types.chat import ChatCompletion

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
api_key = os.environ.get("API_KEY", "something1234")


class TestCompletions:
    strict_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    def test_method_create_overload_1(self, client: OpenAI) -> None:
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
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
                    "role": "system",
                    "content": "string",
                    "name": "string",
                    "function_call": {
                        "name": "string",
                        "arguments": "string",
                    },
                }
            ],
            model="gpt-3.5-turbo",
            frequency_penalty=-2,
            function_call="none",
            functions=[
                {
                    "name": "string",
                    "description": "string",
                    "parameters": {"foo": "bar"},
                }
            ],
            logit_bias={"foo": 0},
            max_tokens=0,
            n=1,
            presence_penalty=-2,
            stop="string",
            stream=False,
            temperature=1,
            top_p=1,
            user="user-1234",
        )
        assert_matches_type(ChatCompletion, completion, path=["response"])

    @parametrize
    def test_method_create_overload_2(self, client: OpenAI) -> None:
        client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
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
                    "role": "system",
                    "content": "string",
                    "name": "string",
                    "function_call": {
                        "name": "string",
                        "arguments": "string",
                    },
                }
            ],
            model="gpt-3.5-turbo",
            stream=True,
            frequency_penalty=-2,
            function_call="none",
            functions=[
                {
                    "name": "string",
                    "description": "string",
                    "parameters": {"foo": "bar"},
                }
            ],
            logit_bias={"foo": 0},
            max_tokens=0,
            n=1,
            presence_penalty=-2,
            stop="string",
            temperature=1,
            top_p=1,
            user="user-1234",
        )


class TestAsyncCompletions:
    strict_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    async def test_method_create_overload_1(self, client: AsyncOpenAI) -> None:
        completion = await client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
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
                    "role": "system",
                    "content": "string",
                    "name": "string",
                    "function_call": {
                        "name": "string",
                        "arguments": "string",
                    },
                }
            ],
            model="gpt-3.5-turbo",
            frequency_penalty=-2,
            function_call="none",
            functions=[
                {
                    "name": "string",
                    "description": "string",
                    "parameters": {"foo": "bar"},
                }
            ],
            logit_bias={"foo": 0},
            max_tokens=0,
            n=1,
            presence_penalty=-2,
            stop="string",
            stream=False,
            temperature=1,
            top_p=1,
            user="user-1234",
        )
        assert_matches_type(ChatCompletion, completion, path=["response"])

    @parametrize
    async def test_method_create_overload_2(self, client: AsyncOpenAI) -> None:
        await client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
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
                    "role": "system",
                    "content": "string",
                    "name": "string",
                    "function_call": {
                        "name": "string",
                        "arguments": "string",
                    },
                }
            ],
            model="gpt-3.5-turbo",
            stream=True,
            frequency_penalty=-2,
            function_call="none",
            functions=[
                {
                    "name": "string",
                    "description": "string",
                    "parameters": {"foo": "bar"},
                }
            ],
            logit_bias={"foo": 0},
            max_tokens=0,
            n=1,
            presence_penalty=-2,
            stop="string",
            temperature=1,
            top_p=1,
            user="user-1234",
        )
