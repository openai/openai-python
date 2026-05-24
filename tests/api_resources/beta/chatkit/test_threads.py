# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncConversationCursorPage, AsyncConversationCursorPage
from openai.types.beta.chatkit import ChatKitThread, ThreadDeleteResponse
from openai.types.beta.chatkit.chatkit_thread_item_list import Data

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestThreads:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        thread = client.beta.chatkit.threads.retrieve(
            "cthr_123",
        )
        assert_matches_type(ChatKitThread, thread, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.beta.chatkit.threads.with_raw_response.retrieve(
            "cthr_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        thread = response.parse()
        assert_matches_type(ChatKitThread, thread, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.beta.chatkit.threads.with_streaming_response.retrieve(
            "cthr_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            thread = response.parse()
            assert_matches_type(ChatKitThread, thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.beta.chatkit.threads.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        thread = client.beta.chatkit.threads.list()
        assert_matches_type(SyncConversationCursorPage[ChatKitThread], thread, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        thread = client.beta.chatkit.threads.list(
            after="after",
            before="before",
            limit=0,
            order="asc",
            user="x",
        )
        assert_matches_type(SyncConversationCursorPage[ChatKitThread], thread, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.beta.chatkit.threads.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        thread = response.parse()
        assert_matches_type(SyncConversationCursorPage[ChatKitThread], thread, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.beta.chatkit.threads.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            thread = response.parse()
            assert_matches_type(SyncConversationCursorPage[ChatKitThread], thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        thread = client.beta.chatkit.threads.delete(
            "cthr_123",
        )
        assert_matches_type(ThreadDeleteResponse, thread, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.beta.chatkit.threads.with_raw_response.delete(
            "cthr_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        thread = response.parse()
        assert_matches_type(ThreadDeleteResponse, thread, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.beta.chatkit.threads.with_streaming_response.delete(
            "cthr_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            thread = response.parse()
            assert_matches_type(ThreadDeleteResponse, thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.beta.chatkit.threads.with_raw_response.delete(
                "",
            )

    @parametrize
    def test_method_list_items(self, client: OpenAI) -> None:
        thread = client.beta.chatkit.threads.list_items(
            thread_id="cthr_123",
        )
        assert_matches_type(SyncConversationCursorPage[Data], thread, path=["response"])

    @parametrize
    def test_method_list_items_with_all_params(self, client: OpenAI) -> None:
        thread = client.beta.chatkit.threads.list_items(
            thread_id="cthr_123",
            after="after",
            before="before",
            limit=0,
            order="asc",
        )
        assert_matches_type(SyncConversationCursorPage[Data], thread, path=["response"])

    @parametrize
    def test_raw_response_list_items(self, client: OpenAI) -> None:
        response = client.beta.chatkit.threads.with_raw_response.list_items(
            thread_id="cthr_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        thread = response.parse()
        assert_matches_type(SyncConversationCursorPage[Data], thread, path=["response"])

    @parametrize
    def test_streaming_response_list_items(self, client: OpenAI) -> None:
        with client.beta.chatkit.threads.with_streaming_response.list_items(
            thread_id="cthr_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            thread = response.parse()
            assert_matches_type(SyncConversationCursorPage[Data], thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list_items(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.beta.chatkit.threads.with_raw_response.list_items(
                thread_id="",
            )


class TestAsyncThreads:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        thread = await async_client.beta.chatkit.threads.retrieve(
            "cthr_123",
        )
        assert_matches_type(ChatKitThread, thread, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.chatkit.threads.with_raw_response.retrieve(
            "cthr_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        thread = response.parse()
        assert_matches_type(ChatKitThread, thread, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.chatkit.threads.with_streaming_response.retrieve(
            "cthr_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            thread = await response.parse()
            assert_matches_type(ChatKitThread, thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.beta.chatkit.threads.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        thread = await async_client.beta.chatkit.threads.list()
        assert_matches_type(AsyncConversationCursorPage[ChatKitThread], thread, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        thread = await async_client.beta.chatkit.threads.list(
            after="after",
            before="before",
            limit=0,
            order="asc",
            user="x",
        )
        assert_matches_type(AsyncConversationCursorPage[ChatKitThread], thread, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.chatkit.threads.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        thread = response.parse()
        assert_matches_type(AsyncConversationCursorPage[ChatKitThread], thread, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.chatkit.threads.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            thread = await response.parse()
            assert_matches_type(AsyncConversationCursorPage[ChatKitThread], thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        thread = await async_client.beta.chatkit.threads.delete(
            "cthr_123",
        )
        assert_matches_type(ThreadDeleteResponse, thread, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.chatkit.threads.with_raw_response.delete(
            "cthr_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        thread = response.parse()
        assert_matches_type(ThreadDeleteResponse, thread, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.chatkit.threads.with_streaming_response.delete(
            "cthr_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            thread = await response.parse()
            assert_matches_type(ThreadDeleteResponse, thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.beta.chatkit.threads.with_raw_response.delete(
                "",
            )

    @parametrize
    async def test_method_list_items(self, async_client: AsyncOpenAI) -> None:
        thread = await async_client.beta.chatkit.threads.list_items(
            thread_id="cthr_123",
        )
        assert_matches_type(AsyncConversationCursorPage[Data], thread, path=["response"])

    @parametrize
    async def test_method_list_items_with_all_params(self, async_client: AsyncOpenAI) -> None:
        thread = await async_client.beta.chatkit.threads.list_items(
            thread_id="cthr_123",
            after="after",
            before="before",
            limit=0,
            order="asc",
        )
        assert_matches_type(AsyncConversationCursorPage[Data], thread, path=["response"])

    @parametrize
    async def test_raw_response_list_items(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.chatkit.threads.with_raw_response.list_items(
            thread_id="cthr_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        thread = response.parse()
        assert_matches_type(AsyncConversationCursorPage[Data], thread, path=["response"])

    @parametrize
    async def test_streaming_response_list_items(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.chatkit.threads.with_streaming_response.list_items(
            thread_id="cthr_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            thread = await response.parse()
            assert_matches_type(AsyncConversationCursorPage[Data], thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list_items(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.beta.chatkit.threads.with_raw_response.list_items(
                thread_id="",
            )
