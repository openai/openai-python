# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.admin.organization.groups import (
    RoleListResponse,
    RoleCreateResponse,
    RoleDeleteResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRoles:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        role = client.admin.organization.groups.roles.create(
            group_id="group_id",
            role_id="role_id",
        )
        assert_matches_type(RoleCreateResponse, role, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.admin.organization.groups.roles.with_raw_response.create(
            group_id="group_id",
            role_id="role_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = response.parse()
        assert_matches_type(RoleCreateResponse, role, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.admin.organization.groups.roles.with_streaming_response.create(
            group_id="group_id",
            role_id="role_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = response.parse()
            assert_matches_type(RoleCreateResponse, role, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `group_id` but received ''"):
            client.admin.organization.groups.roles.with_raw_response.create(
                group_id="",
                role_id="role_id",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        role = client.admin.organization.groups.roles.list(
            group_id="group_id",
        )
        assert_matches_type(SyncCursorPage[RoleListResponse], role, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        role = client.admin.organization.groups.roles.list(
            group_id="group_id",
            after="after",
            limit=0,
            order="asc",
        )
        assert_matches_type(SyncCursorPage[RoleListResponse], role, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.admin.organization.groups.roles.with_raw_response.list(
            group_id="group_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = response.parse()
        assert_matches_type(SyncCursorPage[RoleListResponse], role, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.admin.organization.groups.roles.with_streaming_response.list(
            group_id="group_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = response.parse()
            assert_matches_type(SyncCursorPage[RoleListResponse], role, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `group_id` but received ''"):
            client.admin.organization.groups.roles.with_raw_response.list(
                group_id="",
            )

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        role = client.admin.organization.groups.roles.delete(
            role_id="role_id",
            group_id="group_id",
        )
        assert_matches_type(RoleDeleteResponse, role, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.admin.organization.groups.roles.with_raw_response.delete(
            role_id="role_id",
            group_id="group_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = response.parse()
        assert_matches_type(RoleDeleteResponse, role, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.admin.organization.groups.roles.with_streaming_response.delete(
            role_id="role_id",
            group_id="group_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = response.parse()
            assert_matches_type(RoleDeleteResponse, role, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `group_id` but received ''"):
            client.admin.organization.groups.roles.with_raw_response.delete(
                role_id="role_id",
                group_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `role_id` but received ''"):
            client.admin.organization.groups.roles.with_raw_response.delete(
                role_id="",
                group_id="group_id",
            )


class TestAsyncRoles:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        role = await async_client.admin.organization.groups.roles.create(
            group_id="group_id",
            role_id="role_id",
        )
        assert_matches_type(RoleCreateResponse, role, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.groups.roles.with_raw_response.create(
            group_id="group_id",
            role_id="role_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = response.parse()
        assert_matches_type(RoleCreateResponse, role, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.groups.roles.with_streaming_response.create(
            group_id="group_id",
            role_id="role_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = await response.parse()
            assert_matches_type(RoleCreateResponse, role, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `group_id` but received ''"):
            await async_client.admin.organization.groups.roles.with_raw_response.create(
                group_id="",
                role_id="role_id",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        role = await async_client.admin.organization.groups.roles.list(
            group_id="group_id",
        )
        assert_matches_type(AsyncCursorPage[RoleListResponse], role, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        role = await async_client.admin.organization.groups.roles.list(
            group_id="group_id",
            after="after",
            limit=0,
            order="asc",
        )
        assert_matches_type(AsyncCursorPage[RoleListResponse], role, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.groups.roles.with_raw_response.list(
            group_id="group_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = response.parse()
        assert_matches_type(AsyncCursorPage[RoleListResponse], role, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.groups.roles.with_streaming_response.list(
            group_id="group_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = await response.parse()
            assert_matches_type(AsyncCursorPage[RoleListResponse], role, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `group_id` but received ''"):
            await async_client.admin.organization.groups.roles.with_raw_response.list(
                group_id="",
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        role = await async_client.admin.organization.groups.roles.delete(
            role_id="role_id",
            group_id="group_id",
        )
        assert_matches_type(RoleDeleteResponse, role, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.groups.roles.with_raw_response.delete(
            role_id="role_id",
            group_id="group_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        role = response.parse()
        assert_matches_type(RoleDeleteResponse, role, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.groups.roles.with_streaming_response.delete(
            role_id="role_id",
            group_id="group_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            role = await response.parse()
            assert_matches_type(RoleDeleteResponse, role, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `group_id` but received ''"):
            await async_client.admin.organization.groups.roles.with_raw_response.delete(
                role_id="role_id",
                group_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `role_id` but received ''"):
            await async_client.admin.organization.groups.roles.with_raw_response.delete(
                role_id="",
                group_id="group_id",
            )
