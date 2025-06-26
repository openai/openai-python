# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.responses import ResponseItem

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestInputItems:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        input_item = client.responses.input_items.list(
            response_id="response_id",
        )
        assert_matches_type(SyncCursorPage[ResponseItem], input_item, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        input_item = client.responses.input_items.list(
            response_id="response_id",
            after="after",
            before="before",
            include=["code_interpreter_call.outputs"],
            limit=0,
            order="asc",
        )
        assert_matches_type(SyncCursorPage[ResponseItem], input_item, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.responses.input_items.with_raw_response.list(
            response_id="response_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        input_item = response.parse()
        assert_matches_type(SyncCursorPage[ResponseItem], input_item, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.responses.input_items.with_streaming_response.list(
            response_id="response_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            input_item = response.parse()
            assert_matches_type(SyncCursorPage[ResponseItem], input_item, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `response_id` but received ''"):
            client.responses.input_items.with_raw_response.list(
                response_id="",
            )


class TestAsyncInputItems:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        input_item = await async_client.responses.input_items.list(
            response_id="response_id",
        )
        assert_matches_type(AsyncCursorPage[ResponseItem], input_item, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        input_item = await async_client.responses.input_items.list(
            response_id="response_id",
            after="after",
            before="before",
            include=["code_interpreter_call.outputs"],
            limit=0,
            order="asc",
        )
        assert_matches_type(AsyncCursorPage[ResponseItem], input_item, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.responses.input_items.with_raw_response.list(
            response_id="response_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        input_item = response.parse()
        assert_matches_type(AsyncCursorPage[ResponseItem], input_item, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.responses.input_items.with_streaming_response.list(
            response_id="response_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            input_item = await response.parse()
            assert_matches_type(AsyncCursorPage[ResponseItem], input_item, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `response_id` but received ''"):
            await async_client.responses.input_items.with_raw_response.list(
                response_id="",
            )
