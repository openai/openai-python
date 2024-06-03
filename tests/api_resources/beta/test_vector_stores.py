# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.beta import (
    VectorStore,
    VectorStoreDeleted,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestVectorStores:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        vector_store = client.beta.vector_stores.create()
        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        vector_store = client.beta.vector_stores.create(
            chunking_strategy={"type": "auto"},
            expires_after={
                "anchor": "last_active_at",
                "days": 1,
            },
            file_ids=["string", "string", "string"],
            metadata={},
            name="string",
        )
        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.beta.vector_stores.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vector_store = response.parse()
        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.beta.vector_stores.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            vector_store = response.parse()
            assert_matches_type(VectorStore, vector_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        vector_store = client.beta.vector_stores.retrieve(
            "string",
        )
        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.beta.vector_stores.with_raw_response.retrieve(
            "string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vector_store = response.parse()
        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.beta.vector_stores.with_streaming_response.retrieve(
            "string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            vector_store = response.parse()
            assert_matches_type(VectorStore, vector_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vector_store_id` but received ''"):
            client.beta.vector_stores.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_update(self, client: OpenAI) -> None:
        vector_store = client.beta.vector_stores.update(
            "string",
        )
        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: OpenAI) -> None:
        vector_store = client.beta.vector_stores.update(
            "string",
            expires_after={
                "anchor": "last_active_at",
                "days": 1,
            },
            metadata={},
            name="string",
        )
        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: OpenAI) -> None:
        response = client.beta.vector_stores.with_raw_response.update(
            "string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vector_store = response.parse()
        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: OpenAI) -> None:
        with client.beta.vector_stores.with_streaming_response.update(
            "string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            vector_store = response.parse()
            assert_matches_type(VectorStore, vector_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vector_store_id` but received ''"):
            client.beta.vector_stores.with_raw_response.update(
                "",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        vector_store = client.beta.vector_stores.list()
        assert_matches_type(SyncCursorPage[VectorStore], vector_store, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        vector_store = client.beta.vector_stores.list(
            after="string",
            before="string",
            limit=0,
            order="asc",
        )
        assert_matches_type(SyncCursorPage[VectorStore], vector_store, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.beta.vector_stores.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vector_store = response.parse()
        assert_matches_type(SyncCursorPage[VectorStore], vector_store, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.beta.vector_stores.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            vector_store = response.parse()
            assert_matches_type(SyncCursorPage[VectorStore], vector_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        vector_store = client.beta.vector_stores.delete(
            "string",
        )
        assert_matches_type(VectorStoreDeleted, vector_store, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.beta.vector_stores.with_raw_response.delete(
            "string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vector_store = response.parse()
        assert_matches_type(VectorStoreDeleted, vector_store, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.beta.vector_stores.with_streaming_response.delete(
            "string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            vector_store = response.parse()
            assert_matches_type(VectorStoreDeleted, vector_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vector_store_id` but received ''"):
            client.beta.vector_stores.with_raw_response.delete(
                "",
            )


class TestAsyncVectorStores:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        vector_store = await async_client.beta.vector_stores.create()
        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        vector_store = await async_client.beta.vector_stores.create(
            chunking_strategy={"type": "auto"},
            expires_after={
                "anchor": "last_active_at",
                "days": 1,
            },
            file_ids=["string", "string", "string"],
            metadata={},
            name="string",
        )
        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.vector_stores.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vector_store = response.parse()
        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.vector_stores.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            vector_store = await response.parse()
            assert_matches_type(VectorStore, vector_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        vector_store = await async_client.beta.vector_stores.retrieve(
            "string",
        )
        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.vector_stores.with_raw_response.retrieve(
            "string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vector_store = response.parse()
        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.vector_stores.with_streaming_response.retrieve(
            "string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            vector_store = await response.parse()
            assert_matches_type(VectorStore, vector_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vector_store_id` but received ''"):
            await async_client.beta.vector_stores.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncOpenAI) -> None:
        vector_store = await async_client.beta.vector_stores.update(
            "string",
        )
        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncOpenAI) -> None:
        vector_store = await async_client.beta.vector_stores.update(
            "string",
            expires_after={
                "anchor": "last_active_at",
                "days": 1,
            },
            metadata={},
            name="string",
        )
        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.vector_stores.with_raw_response.update(
            "string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vector_store = response.parse()
        assert_matches_type(VectorStore, vector_store, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.vector_stores.with_streaming_response.update(
            "string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            vector_store = await response.parse()
            assert_matches_type(VectorStore, vector_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vector_store_id` but received ''"):
            await async_client.beta.vector_stores.with_raw_response.update(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        vector_store = await async_client.beta.vector_stores.list()
        assert_matches_type(AsyncCursorPage[VectorStore], vector_store, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        vector_store = await async_client.beta.vector_stores.list(
            after="string",
            before="string",
            limit=0,
            order="asc",
        )
        assert_matches_type(AsyncCursorPage[VectorStore], vector_store, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.vector_stores.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vector_store = response.parse()
        assert_matches_type(AsyncCursorPage[VectorStore], vector_store, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.vector_stores.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            vector_store = await response.parse()
            assert_matches_type(AsyncCursorPage[VectorStore], vector_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        vector_store = await async_client.beta.vector_stores.delete(
            "string",
        )
        assert_matches_type(VectorStoreDeleted, vector_store, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.vector_stores.with_raw_response.delete(
            "string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        vector_store = response.parse()
        assert_matches_type(VectorStoreDeleted, vector_store, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.vector_stores.with_streaming_response.delete(
            "string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            vector_store = await response.parse()
            assert_matches_type(VectorStoreDeleted, vector_store, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vector_store_id` but received ''"):
            await async_client.beta.vector_stores.with_raw_response.delete(
                "",
            )
