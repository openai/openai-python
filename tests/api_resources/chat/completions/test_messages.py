# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.chat import ChatCompletionStoreMessage

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMessages:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        message = client.chat.completions.messages.list(
            completion_id="completion_id",
        )
        assert_matches_type(SyncCursorPage[ChatCompletionStoreMessage], message, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        message = client.chat.completions.messages.list(
            completion_id="completion_id",
            after="after",
            limit=0,
            order="asc",
        )
        assert_matches_type(SyncCursorPage[ChatCompletionStoreMessage], message, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.chat.completions.messages.with_raw_response.list(
            completion_id="completion_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(SyncCursorPage[ChatCompletionStoreMessage], message, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.chat.completions.messages.with_streaming_response.list(
            completion_id="completion_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = response.parse()
            assert_matches_type(SyncCursorPage[ChatCompletionStoreMessage], message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `completion_id` but received ''"):
            client.chat.completions.messages.with_raw_response.list(
                completion_id="",
            )


class TestAsyncMessages:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        message = await async_client.chat.completions.messages.list(
            completion_id="completion_id",
        )
        assert_matches_type(AsyncCursorPage[ChatCompletionStoreMessage], message, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        message = await async_client.chat.completions.messages.list(
            completion_id="completion_id",
            after="after",
            limit=0,
            order="asc",
        )
        assert_matches_type(AsyncCursorPage[ChatCompletionStoreMessage], message, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.chat.completions.messages.with_raw_response.list(
            completion_id="completion_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(AsyncCursorPage[ChatCompletionStoreMessage], message, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.chat.completions.messages.with_streaming_response.list(
            completion_id="completion_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = await response.parse()
            assert_matches_type(AsyncCursorPage[ChatCompletionStoreMessage], message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `completion_id` but received ''"):
            await async_client.chat.completions.messages.with_raw_response.list(
                completion_id="",
            )
