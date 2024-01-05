# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

import os

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai._client import OpenAI, AsyncOpenAI
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.beta.threads.messages import MessageFile

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
api_key = "My API Key"


class TestFiles:
    strict_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        file = client.beta.threads.messages.files.retrieve(
            "file-abc123",
            thread_id="thread_abc123",
            message_id="msg_abc123",
        )
        assert_matches_type(MessageFile, file, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.beta.threads.messages.files.with_raw_response.retrieve(
            "file-abc123",
            thread_id="thread_abc123",
            message_id="msg_abc123",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(MessageFile, file, path=["response"])

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        file = client.beta.threads.messages.files.list(
            "string",
            thread_id="string",
        )
        assert_matches_type(SyncCursorPage[MessageFile], file, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        file = client.beta.threads.messages.files.list(
            "string",
            thread_id="string",
            after="string",
            before="string",
            limit=0,
            order="asc",
        )
        assert_matches_type(SyncCursorPage[MessageFile], file, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.beta.threads.messages.files.with_raw_response.list(
            "string",
            thread_id="string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(SyncCursorPage[MessageFile], file, path=["response"])


class TestAsyncFiles:
    strict_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    async def test_method_retrieve(self, client: AsyncOpenAI) -> None:
        file = await client.beta.threads.messages.files.retrieve(
            "file-abc123",
            thread_id="thread_abc123",
            message_id="msg_abc123",
        )
        assert_matches_type(MessageFile, file, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, client: AsyncOpenAI) -> None:
        response = await client.beta.threads.messages.files.with_raw_response.retrieve(
            "file-abc123",
            thread_id="thread_abc123",
            message_id="msg_abc123",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(MessageFile, file, path=["response"])

    @parametrize
    async def test_method_list(self, client: AsyncOpenAI) -> None:
        file = await client.beta.threads.messages.files.list(
            "string",
            thread_id="string",
        )
        assert_matches_type(AsyncCursorPage[MessageFile], file, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, client: AsyncOpenAI) -> None:
        file = await client.beta.threads.messages.files.list(
            "string",
            thread_id="string",
            after="string",
            before="string",
            limit=0,
            order="asc",
        )
        assert_matches_type(AsyncCursorPage[MessageFile], file, path=["response"])

    @parametrize
    async def test_raw_response_list(self, client: AsyncOpenAI) -> None:
        response = await client.beta.threads.messages.files.with_raw_response.list(
            "string",
            thread_id="string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(AsyncCursorPage[MessageFile], file, path=["response"])
