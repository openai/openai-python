# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.admin.organization import (
    ExternalStorageDeleted,
    ExternalStorageConfiguration,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestExternalStorage:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        external_storage = client.admin.organization.external_storage.create(
            project_id="proj_123",
            provider={
                "bucket": "bucket",
                "role_arn": "role_arn",
                "type": "aws",
            },
        )
        assert_matches_type(ExternalStorageConfiguration, external_storage, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.admin.organization.external_storage.with_raw_response.create(
            project_id="proj_123",
            provider={
                "bucket": "bucket",
                "role_arn": "role_arn",
                "type": "aws",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_storage = response.parse()
        assert_matches_type(ExternalStorageConfiguration, external_storage, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.admin.organization.external_storage.with_streaming_response.create(
            project_id="proj_123",
            provider={
                "bucket": "bucket",
                "role_arn": "role_arn",
                "type": "aws",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_storage = response.parse()
            assert_matches_type(ExternalStorageConfiguration, external_storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        external_storage = client.admin.organization.external_storage.retrieve(
            "extstorage_123",
        )
        assert_matches_type(ExternalStorageConfiguration, external_storage, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.admin.organization.external_storage.with_raw_response.retrieve(
            "extstorage_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_storage = response.parse()
        assert_matches_type(ExternalStorageConfiguration, external_storage, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.admin.organization.external_storage.with_streaming_response.retrieve(
            "extstorage_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_storage = response.parse()
            assert_matches_type(ExternalStorageConfiguration, external_storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `external_storage_id` but received ''"):
            client.admin.organization.external_storage.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        external_storage = client.admin.organization.external_storage.list()
        assert_matches_type(SyncCursorPage[ExternalStorageConfiguration], external_storage, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        external_storage = client.admin.organization.external_storage.list(
            after="after",
            limit=1,
            order="asc",
            project_id="proj_123",
        )
        assert_matches_type(SyncCursorPage[ExternalStorageConfiguration], external_storage, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.admin.organization.external_storage.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_storage = response.parse()
        assert_matches_type(SyncCursorPage[ExternalStorageConfiguration], external_storage, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.admin.organization.external_storage.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_storage = response.parse()
            assert_matches_type(SyncCursorPage[ExternalStorageConfiguration], external_storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        external_storage = client.admin.organization.external_storage.delete(
            "extstorage_123",
        )
        assert_matches_type(ExternalStorageDeleted, external_storage, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.admin.organization.external_storage.with_raw_response.delete(
            "extstorage_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_storage = response.parse()
        assert_matches_type(ExternalStorageDeleted, external_storage, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.admin.organization.external_storage.with_streaming_response.delete(
            "extstorage_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_storage = response.parse()
            assert_matches_type(ExternalStorageDeleted, external_storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `external_storage_id` but received ''"):
            client.admin.organization.external_storage.with_raw_response.delete(
                "",
            )

    @parametrize
    def test_method_validate(self, client: OpenAI) -> None:
        external_storage = client.admin.organization.external_storage.validate(
            "extstorage_123",
        )
        assert_matches_type(ExternalStorageConfiguration, external_storage, path=["response"])

    @parametrize
    def test_raw_response_validate(self, client: OpenAI) -> None:
        response = client.admin.organization.external_storage.with_raw_response.validate(
            "extstorage_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_storage = response.parse()
        assert_matches_type(ExternalStorageConfiguration, external_storage, path=["response"])

    @parametrize
    def test_streaming_response_validate(self, client: OpenAI) -> None:
        with client.admin.organization.external_storage.with_streaming_response.validate(
            "extstorage_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_storage = response.parse()
            assert_matches_type(ExternalStorageConfiguration, external_storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_validate(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `external_storage_id` but received ''"):
            client.admin.organization.external_storage.with_raw_response.validate(
                "",
            )


class TestAsyncExternalStorage:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        external_storage = await async_client.admin.organization.external_storage.create(
            project_id="proj_123",
            provider={
                "bucket": "bucket",
                "role_arn": "role_arn",
                "type": "aws",
            },
        )
        assert_matches_type(ExternalStorageConfiguration, external_storage, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.external_storage.with_raw_response.create(
            project_id="proj_123",
            provider={
                "bucket": "bucket",
                "role_arn": "role_arn",
                "type": "aws",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_storage = response.parse()
        assert_matches_type(ExternalStorageConfiguration, external_storage, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.external_storage.with_streaming_response.create(
            project_id="proj_123",
            provider={
                "bucket": "bucket",
                "role_arn": "role_arn",
                "type": "aws",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_storage = await response.parse()
            assert_matches_type(ExternalStorageConfiguration, external_storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        external_storage = await async_client.admin.organization.external_storage.retrieve(
            "extstorage_123",
        )
        assert_matches_type(ExternalStorageConfiguration, external_storage, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.external_storage.with_raw_response.retrieve(
            "extstorage_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_storage = response.parse()
        assert_matches_type(ExternalStorageConfiguration, external_storage, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.external_storage.with_streaming_response.retrieve(
            "extstorage_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_storage = await response.parse()
            assert_matches_type(ExternalStorageConfiguration, external_storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `external_storage_id` but received ''"):
            await async_client.admin.organization.external_storage.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        external_storage = await async_client.admin.organization.external_storage.list()
        assert_matches_type(AsyncCursorPage[ExternalStorageConfiguration], external_storage, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        external_storage = await async_client.admin.organization.external_storage.list(
            after="after",
            limit=1,
            order="asc",
            project_id="proj_123",
        )
        assert_matches_type(AsyncCursorPage[ExternalStorageConfiguration], external_storage, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.external_storage.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_storage = response.parse()
        assert_matches_type(AsyncCursorPage[ExternalStorageConfiguration], external_storage, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.external_storage.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_storage = await response.parse()
            assert_matches_type(AsyncCursorPage[ExternalStorageConfiguration], external_storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        external_storage = await async_client.admin.organization.external_storage.delete(
            "extstorage_123",
        )
        assert_matches_type(ExternalStorageDeleted, external_storage, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.external_storage.with_raw_response.delete(
            "extstorage_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_storage = response.parse()
        assert_matches_type(ExternalStorageDeleted, external_storage, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.external_storage.with_streaming_response.delete(
            "extstorage_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_storage = await response.parse()
            assert_matches_type(ExternalStorageDeleted, external_storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `external_storage_id` but received ''"):
            await async_client.admin.organization.external_storage.with_raw_response.delete(
                "",
            )

    @parametrize
    async def test_method_validate(self, async_client: AsyncOpenAI) -> None:
        external_storage = await async_client.admin.organization.external_storage.validate(
            "extstorage_123",
        )
        assert_matches_type(ExternalStorageConfiguration, external_storage, path=["response"])

    @parametrize
    async def test_raw_response_validate(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.external_storage.with_raw_response.validate(
            "extstorage_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_storage = response.parse()
        assert_matches_type(ExternalStorageConfiguration, external_storage, path=["response"])

    @parametrize
    async def test_streaming_response_validate(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.external_storage.with_streaming_response.validate(
            "extstorage_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_storage = await response.parse()
            assert_matches_type(ExternalStorageConfiguration, external_storage, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_validate(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `external_storage_id` but received ''"):
            await async_client.admin.organization.external_storage.with_raw_response.validate(
                "",
            )
