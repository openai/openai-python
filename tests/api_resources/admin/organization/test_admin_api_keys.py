# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.admin.organization import (
    AdminAPIKey,
    AdminAPIKeyCreateResponse,
    AdminAPIKeyDeleteResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAdminAPIKeys:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        admin_api_key = client.admin.organization.admin_api_keys.create(
            name="New Admin Key",
        )
        assert_matches_type(AdminAPIKeyCreateResponse, admin_api_key, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.admin.organization.admin_api_keys.with_raw_response.create(
            name="New Admin Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        admin_api_key = response.parse()
        assert_matches_type(AdminAPIKeyCreateResponse, admin_api_key, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.admin.organization.admin_api_keys.with_streaming_response.create(
            name="New Admin Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            admin_api_key = response.parse()
            assert_matches_type(AdminAPIKeyCreateResponse, admin_api_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        admin_api_key = client.admin.organization.admin_api_keys.retrieve(
            "key_id",
        )
        assert_matches_type(AdminAPIKey, admin_api_key, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.admin.organization.admin_api_keys.with_raw_response.retrieve(
            "key_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        admin_api_key = response.parse()
        assert_matches_type(AdminAPIKey, admin_api_key, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.admin.organization.admin_api_keys.with_streaming_response.retrieve(
            "key_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            admin_api_key = response.parse()
            assert_matches_type(AdminAPIKey, admin_api_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `key_id` but received ''"):
            client.admin.organization.admin_api_keys.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        admin_api_key = client.admin.organization.admin_api_keys.list()
        assert_matches_type(SyncCursorPage[AdminAPIKey], admin_api_key, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        admin_api_key = client.admin.organization.admin_api_keys.list(
            after="after",
            limit=0,
            order="asc",
        )
        assert_matches_type(SyncCursorPage[AdminAPIKey], admin_api_key, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.admin.organization.admin_api_keys.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        admin_api_key = response.parse()
        assert_matches_type(SyncCursorPage[AdminAPIKey], admin_api_key, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.admin.organization.admin_api_keys.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            admin_api_key = response.parse()
            assert_matches_type(SyncCursorPage[AdminAPIKey], admin_api_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        admin_api_key = client.admin.organization.admin_api_keys.delete(
            "key_id",
        )
        assert_matches_type(AdminAPIKeyDeleteResponse, admin_api_key, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.admin.organization.admin_api_keys.with_raw_response.delete(
            "key_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        admin_api_key = response.parse()
        assert_matches_type(AdminAPIKeyDeleteResponse, admin_api_key, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.admin.organization.admin_api_keys.with_streaming_response.delete(
            "key_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            admin_api_key = response.parse()
            assert_matches_type(AdminAPIKeyDeleteResponse, admin_api_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `key_id` but received ''"):
            client.admin.organization.admin_api_keys.with_raw_response.delete(
                "",
            )


class TestAsyncAdminAPIKeys:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        admin_api_key = await async_client.admin.organization.admin_api_keys.create(
            name="New Admin Key",
        )
        assert_matches_type(AdminAPIKeyCreateResponse, admin_api_key, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.admin_api_keys.with_raw_response.create(
            name="New Admin Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        admin_api_key = response.parse()
        assert_matches_type(AdminAPIKeyCreateResponse, admin_api_key, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.admin_api_keys.with_streaming_response.create(
            name="New Admin Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            admin_api_key = await response.parse()
            assert_matches_type(AdminAPIKeyCreateResponse, admin_api_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        admin_api_key = await async_client.admin.organization.admin_api_keys.retrieve(
            "key_id",
        )
        assert_matches_type(AdminAPIKey, admin_api_key, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.admin_api_keys.with_raw_response.retrieve(
            "key_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        admin_api_key = response.parse()
        assert_matches_type(AdminAPIKey, admin_api_key, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.admin_api_keys.with_streaming_response.retrieve(
            "key_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            admin_api_key = await response.parse()
            assert_matches_type(AdminAPIKey, admin_api_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `key_id` but received ''"):
            await async_client.admin.organization.admin_api_keys.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        admin_api_key = await async_client.admin.organization.admin_api_keys.list()
        assert_matches_type(AsyncCursorPage[AdminAPIKey], admin_api_key, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        admin_api_key = await async_client.admin.organization.admin_api_keys.list(
            after="after",
            limit=0,
            order="asc",
        )
        assert_matches_type(AsyncCursorPage[AdminAPIKey], admin_api_key, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.admin_api_keys.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        admin_api_key = response.parse()
        assert_matches_type(AsyncCursorPage[AdminAPIKey], admin_api_key, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.admin_api_keys.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            admin_api_key = await response.parse()
            assert_matches_type(AsyncCursorPage[AdminAPIKey], admin_api_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        admin_api_key = await async_client.admin.organization.admin_api_keys.delete(
            "key_id",
        )
        assert_matches_type(AdminAPIKeyDeleteResponse, admin_api_key, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.admin_api_keys.with_raw_response.delete(
            "key_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        admin_api_key = response.parse()
        assert_matches_type(AdminAPIKeyDeleteResponse, admin_api_key, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.admin_api_keys.with_streaming_response.delete(
            "key_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            admin_api_key = await response.parse()
            assert_matches_type(AdminAPIKeyDeleteResponse, admin_api_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `key_id` but received ''"):
            await async_client.admin.organization.admin_api_keys.with_raw_response.delete(
                "",
            )
