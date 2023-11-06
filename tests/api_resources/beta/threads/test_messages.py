# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

import os

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai._client import OpenAI, AsyncOpenAI
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.beta.threads import ThreadMessage

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
api_key = "My API Key"


class TestMessages:
    strict_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        message = client.beta.threads.messages.create(
            "string",
            content="x",
            role="user",
        )
        assert_matches_type(ThreadMessage, message, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        message = client.beta.threads.messages.create(
            "string",
            content="x",
            role="user",
            file_ids=["string"],
            metadata={},
        )
        assert_matches_type(ThreadMessage, message, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.beta.threads.messages.with_raw_response.create(
            "string",
            content="x",
            role="user",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(ThreadMessage, message, path=["response"])

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        message = client.beta.threads.messages.retrieve(
            "string",
            thread_id="string",
        )
        assert_matches_type(ThreadMessage, message, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.beta.threads.messages.with_raw_response.retrieve(
            "string",
            thread_id="string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(ThreadMessage, message, path=["response"])

    @parametrize
    def test_method_update(self, client: OpenAI) -> None:
        message = client.beta.threads.messages.update(
            "string",
            thread_id="string",
        )
        assert_matches_type(ThreadMessage, message, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: OpenAI) -> None:
        message = client.beta.threads.messages.update(
            "string",
            thread_id="string",
            metadata={},
        )
        assert_matches_type(ThreadMessage, message, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: OpenAI) -> None:
        response = client.beta.threads.messages.with_raw_response.update(
            "string",
            thread_id="string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(ThreadMessage, message, path=["response"])

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        message = client.beta.threads.messages.list(
            "string",
        )
        assert_matches_type(SyncCursorPage[ThreadMessage], message, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        message = client.beta.threads.messages.list(
            "string",
            after="string",
            before="string",
            limit=0,
            order="asc",
        )
        assert_matches_type(SyncCursorPage[ThreadMessage], message, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.beta.threads.messages.with_raw_response.list(
            "string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(SyncCursorPage[ThreadMessage], message, path=["response"])


class TestAsyncMessages:
    strict_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    async def test_method_create(self, client: AsyncOpenAI) -> None:
        message = await client.beta.threads.messages.create(
            "string",
            content="x",
            role="user",
        )
        assert_matches_type(ThreadMessage, message, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, client: AsyncOpenAI) -> None:
        message = await client.beta.threads.messages.create(
            "string",
            content="x",
            role="user",
            file_ids=["string"],
            metadata={},
        )
        assert_matches_type(ThreadMessage, message, path=["response"])

    @parametrize
    async def test_raw_response_create(self, client: AsyncOpenAI) -> None:
        response = await client.beta.threads.messages.with_raw_response.create(
            "string",
            content="x",
            role="user",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(ThreadMessage, message, path=["response"])

    @parametrize
    async def test_method_retrieve(self, client: AsyncOpenAI) -> None:
        message = await client.beta.threads.messages.retrieve(
            "string",
            thread_id="string",
        )
        assert_matches_type(ThreadMessage, message, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, client: AsyncOpenAI) -> None:
        response = await client.beta.threads.messages.with_raw_response.retrieve(
            "string",
            thread_id="string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(ThreadMessage, message, path=["response"])

    @parametrize
    async def test_method_update(self, client: AsyncOpenAI) -> None:
        message = await client.beta.threads.messages.update(
            "string",
            thread_id="string",
        )
        assert_matches_type(ThreadMessage, message, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, client: AsyncOpenAI) -> None:
        message = await client.beta.threads.messages.update(
            "string",
            thread_id="string",
            metadata={},
        )
        assert_matches_type(ThreadMessage, message, path=["response"])

    @parametrize
    async def test_raw_response_update(self, client: AsyncOpenAI) -> None:
        response = await client.beta.threads.messages.with_raw_response.update(
            "string",
            thread_id="string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(ThreadMessage, message, path=["response"])

    @parametrize
    async def test_method_list(self, client: AsyncOpenAI) -> None:
        message = await client.beta.threads.messages.list(
            "string",
        )
        assert_matches_type(AsyncCursorPage[ThreadMessage], message, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, client: AsyncOpenAI) -> None:
        message = await client.beta.threads.messages.list(
            "string",
            after="string",
            before="string",
            limit=0,
            order="asc",
        )
        assert_matches_type(AsyncCursorPage[ThreadMessage], message, path=["response"])

    @parametrize
    async def test_raw_response_list(self, client: AsyncOpenAI) -> None:
        response = await client.beta.threads.messages.with_raw_response.list(
            "string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(AsyncCursorPage[ThreadMessage], message, path=["response"])
