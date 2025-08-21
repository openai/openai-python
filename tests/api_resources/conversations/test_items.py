# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncConversationCursorPage, AsyncConversationCursorPage
from openai.types.conversations import (
    Conversation,
    ConversationItem,
    ConversationItemList,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestItems:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        item = client.conversations.items.create(
            conversation_id="conv_123",
            items=[
                {
                    "content": "string",
                    "role": "user",
                }
            ],
        )
        assert_matches_type(ConversationItemList, item, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        item = client.conversations.items.create(
            conversation_id="conv_123",
            items=[
                {
                    "content": "string",
                    "role": "user",
                    "type": "message",
                }
            ],
            include=["code_interpreter_call.outputs"],
        )
        assert_matches_type(ConversationItemList, item, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.conversations.items.with_raw_response.create(
            conversation_id="conv_123",
            items=[
                {
                    "content": "string",
                    "role": "user",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        item = response.parse()
        assert_matches_type(ConversationItemList, item, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.conversations.items.with_streaming_response.create(
            conversation_id="conv_123",
            items=[
                {
                    "content": "string",
                    "role": "user",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            item = response.parse()
            assert_matches_type(ConversationItemList, item, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `conversation_id` but received ''"):
            client.conversations.items.with_raw_response.create(
                conversation_id="",
                items=[
                    {
                        "content": "string",
                        "role": "user",
                    }
                ],
            )

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        item = client.conversations.items.retrieve(
            item_id="msg_abc",
            conversation_id="conv_123",
        )
        assert_matches_type(ConversationItem, item, path=["response"])

    @parametrize
    def test_method_retrieve_with_all_params(self, client: OpenAI) -> None:
        item = client.conversations.items.retrieve(
            item_id="msg_abc",
            conversation_id="conv_123",
            include=["code_interpreter_call.outputs"],
        )
        assert_matches_type(ConversationItem, item, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.conversations.items.with_raw_response.retrieve(
            item_id="msg_abc",
            conversation_id="conv_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        item = response.parse()
        assert_matches_type(ConversationItem, item, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.conversations.items.with_streaming_response.retrieve(
            item_id="msg_abc",
            conversation_id="conv_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            item = response.parse()
            assert_matches_type(ConversationItem, item, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `conversation_id` but received ''"):
            client.conversations.items.with_raw_response.retrieve(
                item_id="msg_abc",
                conversation_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `item_id` but received ''"):
            client.conversations.items.with_raw_response.retrieve(
                item_id="",
                conversation_id="conv_123",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        item = client.conversations.items.list(
            conversation_id="conv_123",
        )
        assert_matches_type(SyncConversationCursorPage[ConversationItem], item, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        item = client.conversations.items.list(
            conversation_id="conv_123",
            after="after",
            include=["code_interpreter_call.outputs"],
            limit=0,
            order="asc",
        )
        assert_matches_type(SyncConversationCursorPage[ConversationItem], item, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.conversations.items.with_raw_response.list(
            conversation_id="conv_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        item = response.parse()
        assert_matches_type(SyncConversationCursorPage[ConversationItem], item, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.conversations.items.with_streaming_response.list(
            conversation_id="conv_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            item = response.parse()
            assert_matches_type(SyncConversationCursorPage[ConversationItem], item, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `conversation_id` but received ''"):
            client.conversations.items.with_raw_response.list(
                conversation_id="",
            )

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        item = client.conversations.items.delete(
            item_id="msg_abc",
            conversation_id="conv_123",
        )
        assert_matches_type(Conversation, item, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.conversations.items.with_raw_response.delete(
            item_id="msg_abc",
            conversation_id="conv_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        item = response.parse()
        assert_matches_type(Conversation, item, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.conversations.items.with_streaming_response.delete(
            item_id="msg_abc",
            conversation_id="conv_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            item = response.parse()
            assert_matches_type(Conversation, item, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `conversation_id` but received ''"):
            client.conversations.items.with_raw_response.delete(
                item_id="msg_abc",
                conversation_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `item_id` but received ''"):
            client.conversations.items.with_raw_response.delete(
                item_id="",
                conversation_id="conv_123",
            )


class TestAsyncItems:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        item = await async_client.conversations.items.create(
            conversation_id="conv_123",
            items=[
                {
                    "content": "string",
                    "role": "user",
                }
            ],
        )
        assert_matches_type(ConversationItemList, item, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        item = await async_client.conversations.items.create(
            conversation_id="conv_123",
            items=[
                {
                    "content": "string",
                    "role": "user",
                    "type": "message",
                }
            ],
            include=["code_interpreter_call.outputs"],
        )
        assert_matches_type(ConversationItemList, item, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.conversations.items.with_raw_response.create(
            conversation_id="conv_123",
            items=[
                {
                    "content": "string",
                    "role": "user",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        item = response.parse()
        assert_matches_type(ConversationItemList, item, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.conversations.items.with_streaming_response.create(
            conversation_id="conv_123",
            items=[
                {
                    "content": "string",
                    "role": "user",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            item = await response.parse()
            assert_matches_type(ConversationItemList, item, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `conversation_id` but received ''"):
            await async_client.conversations.items.with_raw_response.create(
                conversation_id="",
                items=[
                    {
                        "content": "string",
                        "role": "user",
                    }
                ],
            )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        item = await async_client.conversations.items.retrieve(
            item_id="msg_abc",
            conversation_id="conv_123",
        )
        assert_matches_type(ConversationItem, item, path=["response"])

    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncOpenAI) -> None:
        item = await async_client.conversations.items.retrieve(
            item_id="msg_abc",
            conversation_id="conv_123",
            include=["code_interpreter_call.outputs"],
        )
        assert_matches_type(ConversationItem, item, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.conversations.items.with_raw_response.retrieve(
            item_id="msg_abc",
            conversation_id="conv_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        item = response.parse()
        assert_matches_type(ConversationItem, item, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.conversations.items.with_streaming_response.retrieve(
            item_id="msg_abc",
            conversation_id="conv_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            item = await response.parse()
            assert_matches_type(ConversationItem, item, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `conversation_id` but received ''"):
            await async_client.conversations.items.with_raw_response.retrieve(
                item_id="msg_abc",
                conversation_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `item_id` but received ''"):
            await async_client.conversations.items.with_raw_response.retrieve(
                item_id="",
                conversation_id="conv_123",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        item = await async_client.conversations.items.list(
            conversation_id="conv_123",
        )
        assert_matches_type(AsyncConversationCursorPage[ConversationItem], item, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        item = await async_client.conversations.items.list(
            conversation_id="conv_123",
            after="after",
            include=["code_interpreter_call.outputs"],
            limit=0,
            order="asc",
        )
        assert_matches_type(AsyncConversationCursorPage[ConversationItem], item, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.conversations.items.with_raw_response.list(
            conversation_id="conv_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        item = response.parse()
        assert_matches_type(AsyncConversationCursorPage[ConversationItem], item, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.conversations.items.with_streaming_response.list(
            conversation_id="conv_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            item = await response.parse()
            assert_matches_type(AsyncConversationCursorPage[ConversationItem], item, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `conversation_id` but received ''"):
            await async_client.conversations.items.with_raw_response.list(
                conversation_id="",
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        item = await async_client.conversations.items.delete(
            item_id="msg_abc",
            conversation_id="conv_123",
        )
        assert_matches_type(Conversation, item, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.conversations.items.with_raw_response.delete(
            item_id="msg_abc",
            conversation_id="conv_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        item = response.parse()
        assert_matches_type(Conversation, item, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.conversations.items.with_streaming_response.delete(
            item_id="msg_abc",
            conversation_id="conv_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            item = await response.parse()
            assert_matches_type(Conversation, item, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `conversation_id` but received ''"):
            await async_client.conversations.items.with_raw_response.delete(
                item_id="msg_abc",
                conversation_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `item_id` but received ''"):
            await async_client.conversations.items.with_raw_response.delete(
                item_id="",
                conversation_id="conv_123",
            )
