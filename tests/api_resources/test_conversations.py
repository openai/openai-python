# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types.conversations import (
    Conversation,
    ConversationDeletedResource,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestConversations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        conversation = client.conversations.create()
        assert_matches_type(Conversation, conversation, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        conversation = client.conversations.create(
            items=[
                {
                    "content": "string",
                    "role": "user",
                    "type": "message",
                }
            ],
            metadata={"foo": "string"},
        )
        assert_matches_type(Conversation, conversation, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.conversations.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        conversation = response.parse()
        assert_matches_type(Conversation, conversation, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.conversations.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            conversation = response.parse()
            assert_matches_type(Conversation, conversation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        conversation = client.conversations.retrieve(
            "conv_123",
        )
        assert_matches_type(Conversation, conversation, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.conversations.with_raw_response.retrieve(
            "conv_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        conversation = response.parse()
        assert_matches_type(Conversation, conversation, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.conversations.with_streaming_response.retrieve(
            "conv_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            conversation = response.parse()
            assert_matches_type(Conversation, conversation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `conversation_id` but received ''"):
            client.conversations.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_update(self, client: OpenAI) -> None:
        conversation = client.conversations.update(
            conversation_id="conv_123",
            metadata={"foo": "string"},
        )
        assert_matches_type(Conversation, conversation, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: OpenAI) -> None:
        response = client.conversations.with_raw_response.update(
            conversation_id="conv_123",
            metadata={"foo": "string"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        conversation = response.parse()
        assert_matches_type(Conversation, conversation, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: OpenAI) -> None:
        with client.conversations.with_streaming_response.update(
            conversation_id="conv_123",
            metadata={"foo": "string"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            conversation = response.parse()
            assert_matches_type(Conversation, conversation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `conversation_id` but received ''"):
            client.conversations.with_raw_response.update(
                conversation_id="",
                metadata={"foo": "string"},
            )

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        conversation = client.conversations.delete(
            "conv_123",
        )
        assert_matches_type(ConversationDeletedResource, conversation, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.conversations.with_raw_response.delete(
            "conv_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        conversation = response.parse()
        assert_matches_type(ConversationDeletedResource, conversation, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.conversations.with_streaming_response.delete(
            "conv_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            conversation = response.parse()
            assert_matches_type(ConversationDeletedResource, conversation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `conversation_id` but received ''"):
            client.conversations.with_raw_response.delete(
                "",
            )


class TestAsyncConversations:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        conversation = await async_client.conversations.create()
        assert_matches_type(Conversation, conversation, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        conversation = await async_client.conversations.create(
            items=[
                {
                    "content": "string",
                    "role": "user",
                    "type": "message",
                }
            ],
            metadata={"foo": "string"},
        )
        assert_matches_type(Conversation, conversation, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.conversations.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        conversation = response.parse()
        assert_matches_type(Conversation, conversation, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.conversations.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            conversation = await response.parse()
            assert_matches_type(Conversation, conversation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        conversation = await async_client.conversations.retrieve(
            "conv_123",
        )
        assert_matches_type(Conversation, conversation, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.conversations.with_raw_response.retrieve(
            "conv_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        conversation = response.parse()
        assert_matches_type(Conversation, conversation, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.conversations.with_streaming_response.retrieve(
            "conv_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            conversation = await response.parse()
            assert_matches_type(Conversation, conversation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `conversation_id` but received ''"):
            await async_client.conversations.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncOpenAI) -> None:
        conversation = await async_client.conversations.update(
            conversation_id="conv_123",
            metadata={"foo": "string"},
        )
        assert_matches_type(Conversation, conversation, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.conversations.with_raw_response.update(
            conversation_id="conv_123",
            metadata={"foo": "string"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        conversation = response.parse()
        assert_matches_type(Conversation, conversation, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncOpenAI) -> None:
        async with async_client.conversations.with_streaming_response.update(
            conversation_id="conv_123",
            metadata={"foo": "string"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            conversation = await response.parse()
            assert_matches_type(Conversation, conversation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `conversation_id` but received ''"):
            await async_client.conversations.with_raw_response.update(
                conversation_id="",
                metadata={"foo": "string"},
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        conversation = await async_client.conversations.delete(
            "conv_123",
        )
        assert_matches_type(ConversationDeletedResource, conversation, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.conversations.with_raw_response.delete(
            "conv_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        conversation = response.parse()
        assert_matches_type(ConversationDeletedResource, conversation, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.conversations.with_streaming_response.delete(
            "conv_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            conversation = await response.parse()
            assert_matches_type(ConversationDeletedResource, conversation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `conversation_id` but received ''"):
            await async_client.conversations.with_raw_response.delete(
                "",
            )
