# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.vector_stores import (
    VectorStoreFile,
    VectorStoreFileBatch,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFileBatches:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        file_batch = client.vector_stores.file_batches.create(
            vector_store_id="vs_abc123",
            file_ids=["string"],
        )
        assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        file_batch = client.vector_stores.file_batches.create(
            vector_store_id="vs_abc123",
            file_ids=["string"],
            attributes={"foo": "string"},
            chunking_strategy={"type": "auto"},
        )
        assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.vector_stores.file_batches.with_raw_response.create(
            vector_store_id="vs_abc123",
            file_ids=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file_batch = response.parse()
        assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.vector_stores.file_batches.with_streaming_response.create(
            vector_store_id="vs_abc123",
            file_ids=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file_batch = response.parse()
            assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vector_store_id` but received ''"):
            client.vector_stores.file_batches.with_raw_response.create(
                vector_store_id="",
                file_ids=["string"],
            )

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        file_batch = client.vector_stores.file_batches.retrieve(
            batch_id="vsfb_abc123",
            vector_store_id="vs_abc123",
        )
        assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.vector_stores.file_batches.with_raw_response.retrieve(
            batch_id="vsfb_abc123",
            vector_store_id="vs_abc123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file_batch = response.parse()
        assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.vector_stores.file_batches.with_streaming_response.retrieve(
            batch_id="vsfb_abc123",
            vector_store_id="vs_abc123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file_batch = response.parse()
            assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vector_store_id` but received ''"):
            client.vector_stores.file_batches.with_raw_response.retrieve(
                batch_id="vsfb_abc123",
                vector_store_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_id` but received ''"):
            client.vector_stores.file_batches.with_raw_response.retrieve(
                batch_id="",
                vector_store_id="vs_abc123",
            )

    @parametrize
    def test_method_cancel(self, client: OpenAI) -> None:
        file_batch = client.vector_stores.file_batches.cancel(
            batch_id="batch_id",
            vector_store_id="vector_store_id",
        )
        assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

    @parametrize
    def test_raw_response_cancel(self, client: OpenAI) -> None:
        response = client.vector_stores.file_batches.with_raw_response.cancel(
            batch_id="batch_id",
            vector_store_id="vector_store_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file_batch = response.parse()
        assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

    @parametrize
    def test_streaming_response_cancel(self, client: OpenAI) -> None:
        with client.vector_stores.file_batches.with_streaming_response.cancel(
            batch_id="batch_id",
            vector_store_id="vector_store_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file_batch = response.parse()
            assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_cancel(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vector_store_id` but received ''"):
            client.vector_stores.file_batches.with_raw_response.cancel(
                batch_id="batch_id",
                vector_store_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_id` but received ''"):
            client.vector_stores.file_batches.with_raw_response.cancel(
                batch_id="",
                vector_store_id="vector_store_id",
            )

    @parametrize
    def test_method_list_files(self, client: OpenAI) -> None:
        file_batch = client.vector_stores.file_batches.list_files(
            batch_id="batch_id",
            vector_store_id="vector_store_id",
        )
        assert_matches_type(SyncCursorPage[VectorStoreFile], file_batch, path=["response"])

    @parametrize
    def test_method_list_files_with_all_params(self, client: OpenAI) -> None:
        file_batch = client.vector_stores.file_batches.list_files(
            batch_id="batch_id",
            vector_store_id="vector_store_id",
            after="after",
            before="before",
            filter="in_progress",
            limit=0,
            order="asc",
        )
        assert_matches_type(SyncCursorPage[VectorStoreFile], file_batch, path=["response"])

    @parametrize
    def test_raw_response_list_files(self, client: OpenAI) -> None:
        response = client.vector_stores.file_batches.with_raw_response.list_files(
            batch_id="batch_id",
            vector_store_id="vector_store_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file_batch = response.parse()
        assert_matches_type(SyncCursorPage[VectorStoreFile], file_batch, path=["response"])

    @parametrize
    def test_streaming_response_list_files(self, client: OpenAI) -> None:
        with client.vector_stores.file_batches.with_streaming_response.list_files(
            batch_id="batch_id",
            vector_store_id="vector_store_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file_batch = response.parse()
            assert_matches_type(SyncCursorPage[VectorStoreFile], file_batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list_files(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vector_store_id` but received ''"):
            client.vector_stores.file_batches.with_raw_response.list_files(
                batch_id="batch_id",
                vector_store_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_id` but received ''"):
            client.vector_stores.file_batches.with_raw_response.list_files(
                batch_id="",
                vector_store_id="vector_store_id",
            )


class TestAsyncFileBatches:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        file_batch = await async_client.vector_stores.file_batches.create(
            vector_store_id="vs_abc123",
            file_ids=["string"],
        )
        assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        file_batch = await async_client.vector_stores.file_batches.create(
            vector_store_id="vs_abc123",
            file_ids=["string"],
            attributes={"foo": "string"},
            chunking_strategy={"type": "auto"},
        )
        assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.vector_stores.file_batches.with_raw_response.create(
            vector_store_id="vs_abc123",
            file_ids=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file_batch = response.parse()
        assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.vector_stores.file_batches.with_streaming_response.create(
            vector_store_id="vs_abc123",
            file_ids=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file_batch = await response.parse()
            assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vector_store_id` but received ''"):
            await async_client.vector_stores.file_batches.with_raw_response.create(
                vector_store_id="",
                file_ids=["string"],
            )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        file_batch = await async_client.vector_stores.file_batches.retrieve(
            batch_id="vsfb_abc123",
            vector_store_id="vs_abc123",
        )
        assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.vector_stores.file_batches.with_raw_response.retrieve(
            batch_id="vsfb_abc123",
            vector_store_id="vs_abc123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file_batch = response.parse()
        assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.vector_stores.file_batches.with_streaming_response.retrieve(
            batch_id="vsfb_abc123",
            vector_store_id="vs_abc123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file_batch = await response.parse()
            assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vector_store_id` but received ''"):
            await async_client.vector_stores.file_batches.with_raw_response.retrieve(
                batch_id="vsfb_abc123",
                vector_store_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_id` but received ''"):
            await async_client.vector_stores.file_batches.with_raw_response.retrieve(
                batch_id="",
                vector_store_id="vs_abc123",
            )

    @parametrize
    async def test_method_cancel(self, async_client: AsyncOpenAI) -> None:
        file_batch = await async_client.vector_stores.file_batches.cancel(
            batch_id="batch_id",
            vector_store_id="vector_store_id",
        )
        assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.vector_stores.file_batches.with_raw_response.cancel(
            batch_id="batch_id",
            vector_store_id="vector_store_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file_batch = response.parse()
        assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncOpenAI) -> None:
        async with async_client.vector_stores.file_batches.with_streaming_response.cancel(
            batch_id="batch_id",
            vector_store_id="vector_store_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file_batch = await response.parse()
            assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_cancel(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vector_store_id` but received ''"):
            await async_client.vector_stores.file_batches.with_raw_response.cancel(
                batch_id="batch_id",
                vector_store_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_id` but received ''"):
            await async_client.vector_stores.file_batches.with_raw_response.cancel(
                batch_id="",
                vector_store_id="vector_store_id",
            )

    @parametrize
    async def test_method_list_files(self, async_client: AsyncOpenAI) -> None:
        file_batch = await async_client.vector_stores.file_batches.list_files(
            batch_id="batch_id",
            vector_store_id="vector_store_id",
        )
        assert_matches_type(AsyncCursorPage[VectorStoreFile], file_batch, path=["response"])

    @parametrize
    async def test_method_list_files_with_all_params(self, async_client: AsyncOpenAI) -> None:
        file_batch = await async_client.vector_stores.file_batches.list_files(
            batch_id="batch_id",
            vector_store_id="vector_store_id",
            after="after",
            before="before",
            filter="in_progress",
            limit=0,
            order="asc",
        )
        assert_matches_type(AsyncCursorPage[VectorStoreFile], file_batch, path=["response"])

    @parametrize
    async def test_raw_response_list_files(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.vector_stores.file_batches.with_raw_response.list_files(
            batch_id="batch_id",
            vector_store_id="vector_store_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file_batch = response.parse()
        assert_matches_type(AsyncCursorPage[VectorStoreFile], file_batch, path=["response"])

    @parametrize
    async def test_streaming_response_list_files(self, async_client: AsyncOpenAI) -> None:
        async with async_client.vector_stores.file_batches.with_streaming_response.list_files(
            batch_id="batch_id",
            vector_store_id="vector_store_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file_batch = await response.parse()
            assert_matches_type(AsyncCursorPage[VectorStoreFile], file_batch, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list_files(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vector_store_id` but received ''"):
            await async_client.vector_stores.file_batches.with_raw_response.list_files(
                batch_id="batch_id",
                vector_store_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_id` but received ''"):
            await async_client.vector_stores.file_batches.with_raw_response.list_files(
                batch_id="",
                vector_store_id="vector_store_id",
            )
