# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncNextCursorPage, AsyncNextCursorPage
from openai.types.admin.organization.projects import (
    ProjectGroup,
    GroupDeleteResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestGroups:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        group = client.admin.organization.projects.groups.create(
            project_id="project_id",
            group_id="group_id",
            role="role",
        )
        assert_matches_type(ProjectGroup, group, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.admin.organization.projects.groups.with_raw_response.create(
            project_id="project_id",
            group_id="group_id",
            role="role",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        group = response.parse()
        assert_matches_type(ProjectGroup, group, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.admin.organization.projects.groups.with_streaming_response.create(
            project_id="project_id",
            group_id="group_id",
            role="role",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            group = response.parse()
            assert_matches_type(ProjectGroup, group, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.organization.projects.groups.with_raw_response.create(
                project_id="",
                group_id="group_id",
                role="role",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        group = client.admin.organization.projects.groups.list(
            project_id="project_id",
        )
        assert_matches_type(SyncNextCursorPage[ProjectGroup], group, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        group = client.admin.organization.projects.groups.list(
            project_id="project_id",
            after="after",
            limit=0,
            order="asc",
        )
        assert_matches_type(SyncNextCursorPage[ProjectGroup], group, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.admin.organization.projects.groups.with_raw_response.list(
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        group = response.parse()
        assert_matches_type(SyncNextCursorPage[ProjectGroup], group, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.admin.organization.projects.groups.with_streaming_response.list(
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            group = response.parse()
            assert_matches_type(SyncNextCursorPage[ProjectGroup], group, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.organization.projects.groups.with_raw_response.list(
                project_id="",
            )

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        group = client.admin.organization.projects.groups.delete(
            group_id="group_id",
            project_id="project_id",
        )
        assert_matches_type(GroupDeleteResponse, group, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.admin.organization.projects.groups.with_raw_response.delete(
            group_id="group_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        group = response.parse()
        assert_matches_type(GroupDeleteResponse, group, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.admin.organization.projects.groups.with_streaming_response.delete(
            group_id="group_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            group = response.parse()
            assert_matches_type(GroupDeleteResponse, group, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.organization.projects.groups.with_raw_response.delete(
                group_id="group_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `group_id` but received ''"):
            client.admin.organization.projects.groups.with_raw_response.delete(
                group_id="",
                project_id="project_id",
            )


class TestAsyncGroups:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        group = await async_client.admin.organization.projects.groups.create(
            project_id="project_id",
            group_id="group_id",
            role="role",
        )
        assert_matches_type(ProjectGroup, group, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.projects.groups.with_raw_response.create(
            project_id="project_id",
            group_id="group_id",
            role="role",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        group = response.parse()
        assert_matches_type(ProjectGroup, group, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.projects.groups.with_streaming_response.create(
            project_id="project_id",
            group_id="group_id",
            role="role",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            group = await response.parse()
            assert_matches_type(ProjectGroup, group, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.organization.projects.groups.with_raw_response.create(
                project_id="",
                group_id="group_id",
                role="role",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        group = await async_client.admin.organization.projects.groups.list(
            project_id="project_id",
        )
        assert_matches_type(AsyncNextCursorPage[ProjectGroup], group, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        group = await async_client.admin.organization.projects.groups.list(
            project_id="project_id",
            after="after",
            limit=0,
            order="asc",
        )
        assert_matches_type(AsyncNextCursorPage[ProjectGroup], group, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.projects.groups.with_raw_response.list(
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        group = response.parse()
        assert_matches_type(AsyncNextCursorPage[ProjectGroup], group, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.projects.groups.with_streaming_response.list(
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            group = await response.parse()
            assert_matches_type(AsyncNextCursorPage[ProjectGroup], group, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.organization.projects.groups.with_raw_response.list(
                project_id="",
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        group = await async_client.admin.organization.projects.groups.delete(
            group_id="group_id",
            project_id="project_id",
        )
        assert_matches_type(GroupDeleteResponse, group, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.projects.groups.with_raw_response.delete(
            group_id="group_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        group = response.parse()
        assert_matches_type(GroupDeleteResponse, group, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.projects.groups.with_streaming_response.delete(
            group_id="group_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            group = await response.parse()
            assert_matches_type(GroupDeleteResponse, group, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.organization.projects.groups.with_raw_response.delete(
                group_id="group_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `group_id` but received ''"):
            await async_client.admin.organization.projects.groups.with_raw_response.delete(
                group_id="",
                project_id="project_id",
            )
