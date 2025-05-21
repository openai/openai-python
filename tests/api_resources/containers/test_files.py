# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.containers import (
    FileListResponse,
    FileCreateResponse,
    FileRetrieveResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFiles:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        file = client.containers.files.create(
            container_id="container_id",
        )
        assert_matches_type(FileCreateResponse, file, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        file = client.containers.files.create(
            container_id="container_id",
            file=b"raw file contents",
            file_id="file_id",
        )
        assert_matches_type(FileCreateResponse, file, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.containers.files.with_raw_response.create(
            container_id="container_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(FileCreateResponse, file, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.containers.files.with_streaming_response.create(
            container_id="container_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(FileCreateResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `container_id` but received ''"):
            client.containers.files.with_raw_response.create(
                container_id="",
            )

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        file = client.containers.files.retrieve(
            file_id="file_id",
            container_id="container_id",
        )
        assert_matches_type(FileRetrieveResponse, file, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.containers.files.with_raw_response.retrieve(
            file_id="file_id",
            container_id="container_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(FileRetrieveResponse, file, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.containers.files.with_streaming_response.retrieve(
            file_id="file_id",
            container_id="container_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(FileRetrieveResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `container_id` but received ''"):
            client.containers.files.with_raw_response.retrieve(
                file_id="file_id",
                container_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_id` but received ''"):
            client.containers.files.with_raw_response.retrieve(
                file_id="",
                container_id="container_id",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        file = client.containers.files.list(
            container_id="container_id",
        )
        assert_matches_type(SyncCursorPage[FileListResponse], file, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        file = client.containers.files.list(
            container_id="container_id",
            after="after",
            limit=0,
            order="asc",
        )
        assert_matches_type(SyncCursorPage[FileListResponse], file, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.containers.files.with_raw_response.list(
            container_id="container_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(SyncCursorPage[FileListResponse], file, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.containers.files.with_streaming_response.list(
            container_id="container_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(SyncCursorPage[FileListResponse], file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `container_id` but received ''"):
            client.containers.files.with_raw_response.list(
                container_id="",
            )

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        file = client.containers.files.delete(
            file_id="file_id",
            container_id="container_id",
        )
        assert file is None

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.containers.files.with_raw_response.delete(
            file_id="file_id",
            container_id="container_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert file is None

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.containers.files.with_streaming_response.delete(
            file_id="file_id",
            container_id="container_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert file is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `container_id` but received ''"):
            client.containers.files.with_raw_response.delete(
                file_id="file_id",
                container_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_id` but received ''"):
            client.containers.files.with_raw_response.delete(
                file_id="",
                container_id="container_id",
            )


class TestAsyncFiles:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        file = await async_client.containers.files.create(
            container_id="container_id",
        )
        assert_matches_type(FileCreateResponse, file, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        file = await async_client.containers.files.create(
            container_id="container_id",
            file=b"raw file contents",
            file_id="file_id",
        )
        assert_matches_type(FileCreateResponse, file, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.containers.files.with_raw_response.create(
            container_id="container_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(FileCreateResponse, file, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.containers.files.with_streaming_response.create(
            container_id="container_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(FileCreateResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `container_id` but received ''"):
            await async_client.containers.files.with_raw_response.create(
                container_id="",
            )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        file = await async_client.containers.files.retrieve(
            file_id="file_id",
            container_id="container_id",
        )
        assert_matches_type(FileRetrieveResponse, file, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.containers.files.with_raw_response.retrieve(
            file_id="file_id",
            container_id="container_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(FileRetrieveResponse, file, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.containers.files.with_streaming_response.retrieve(
            file_id="file_id",
            container_id="container_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(FileRetrieveResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `container_id` but received ''"):
            await async_client.containers.files.with_raw_response.retrieve(
                file_id="file_id",
                container_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_id` but received ''"):
            await async_client.containers.files.with_raw_response.retrieve(
                file_id="",
                container_id="container_id",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        file = await async_client.containers.files.list(
            container_id="container_id",
        )
        assert_matches_type(AsyncCursorPage[FileListResponse], file, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        file = await async_client.containers.files.list(
            container_id="container_id",
            after="after",
            limit=0,
            order="asc",
        )
        assert_matches_type(AsyncCursorPage[FileListResponse], file, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.containers.files.with_raw_response.list(
            container_id="container_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(AsyncCursorPage[FileListResponse], file, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.containers.files.with_streaming_response.list(
            container_id="container_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(AsyncCursorPage[FileListResponse], file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `container_id` but received ''"):
            await async_client.containers.files.with_raw_response.list(
                container_id="",
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        file = await async_client.containers.files.delete(
            file_id="file_id",
            container_id="container_id",
        )
        assert file is None

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.containers.files.with_raw_response.delete(
            file_id="file_id",
            container_id="container_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert file is None

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.containers.files.with_streaming_response.delete(
            file_id="file_id",
            container_id="container_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert file is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `container_id` but received ''"):
            await async_client.containers.files.with_raw_response.delete(
                file_id="file_id",
                container_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_id` but received ''"):
            await async_client.containers.files.with_raw_response.delete(
                file_id="",
                container_id="container_id",
            )
