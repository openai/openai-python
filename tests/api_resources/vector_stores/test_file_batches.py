# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import httpx
import pytest

from openai import OpenAI, AsyncOpenAI, APIResponseValidationError
from tests.utils import assert_matches_type
from openai._utils import assert_signatures_in_sync
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
        )
        assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        file_batch = client.vector_stores.file_batches.create(
            vector_store_id="vs_abc123",
            attributes={"foo": "string"},
            chunking_strategy={"type": "auto"},
            file_ids=["string"],
            files=[
                {
                    "file_id": "file_id",
                    "attributes": {"foo": "string"},
                    "chunking_strategy": {"type": "auto"},
                }
            ],
        )
        assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.vector_stores.file_batches.with_raw_response.create(
            vector_store_id="vs_abc123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file_batch = response.parse()
        assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.vector_stores.file_batches.with_streaming_response.create(
            vector_store_id="vs_abc123",
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
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        file_batch = await async_client.vector_stores.file_batches.create(
            vector_store_id="vs_abc123",
        )
        assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        file_batch = await async_client.vector_stores.file_batches.create(
            vector_store_id="vs_abc123",
            attributes={"foo": "string"},
            chunking_strategy={"type": "auto"},
            file_ids=["string"],
            files=[
                {
                    "file_id": "file_id",
                    "attributes": {"foo": "string"},
                    "chunking_strategy": {"type": "auto"},
                }
            ],
        )
        assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.vector_stores.file_batches.with_raw_response.create(
            vector_store_id="vs_abc123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file_batch = response.parse()
        assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.vector_stores.file_batches.with_streaming_response.create(
            vector_store_id="vs_abc123",
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


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_create_and_poll_method_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    # ensure helpers do not drift from generated spec
    assert_signatures_in_sync(
        checking_client.vector_stores.file_batches.create,
        checking_client.vector_stores.file_batches.create_and_poll,
    )


def _completed_vector_store_response() -> dict[str, object]:
    return {
        "id": "vs_abc123",
        "created_at": 1761991501,
        "file_counts": {
            "cancelled": 0,
            "completed": 1,
            "failed": 0,
            "in_progress": 0,
            "total": 1,
        },
        "object": "vector_store",
        "status": "completed",
        "vector_store_id": None,
    }


def test_poll_coerces_completed_vector_store_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/vector_stores/vs_abc123/file_batches/vsfb_abc123"
        return httpx.Response(200, json=_completed_vector_store_response())

    with OpenAI(
        api_key="My API Key",
        base_url=base_url,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        _strict_response_validation=True,
    ) as client:
        file_batch = client.vector_stores.file_batches.poll(batch_id="vsfb_abc123", vector_store_id="vs_abc123")

    assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])
    assert file_batch.id == "vsfb_abc123"
    assert file_batch.vector_store_id == "vs_abc123"


async def test_async_poll_coerces_completed_vector_store_response() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/vector_stores/vs_abc123/file_batches/vsfb_abc123"
        return httpx.Response(200, json=_completed_vector_store_response())

    async with AsyncOpenAI(
        api_key="My API Key",
        base_url=base_url,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        _strict_response_validation=True,
    ) as async_client:
        file_batch = await async_client.vector_stores.file_batches.poll(
            batch_id="vsfb_abc123", vector_store_id="vs_abc123"
        )

    assert_matches_type(VectorStoreFileBatch, file_batch, path=["response"])
    assert file_batch.id == "vsfb_abc123"
    assert file_batch.vector_store_id == "vs_abc123"


def test_poll_preserves_strict_validation_for_coerced_vector_store_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        data = _completed_vector_store_response()
        data["created_at"] = "invalid"
        return httpx.Response(200, json=data)

    with OpenAI(
        api_key="My API Key",
        base_url=base_url,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        _strict_response_validation=True,
    ) as client:
        with pytest.raises(APIResponseValidationError):
            client.vector_stores.file_batches.poll(batch_id="vsfb_abc123", vector_store_id="vs_abc123")


async def test_async_poll_preserves_strict_validation_for_coerced_vector_store_response() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        data = _completed_vector_store_response()
        data["created_at"] = "invalid"
        return httpx.Response(200, json=data)

    async with AsyncOpenAI(
        api_key="My API Key",
        base_url=base_url,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        _strict_response_validation=True,
    ) as async_client:
        with pytest.raises(APIResponseValidationError):
            await async_client.vector_stores.file_batches.poll(
                batch_id="vsfb_abc123", vector_store_id="vs_abc123"
            )
