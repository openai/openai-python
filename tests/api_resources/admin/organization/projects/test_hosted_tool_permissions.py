# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types.admin.organization.projects import ProjectHostedToolPermissions

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestHostedToolPermissions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        hosted_tool_permission = client.admin.organization.projects.hosted_tool_permissions.retrieve(
            "project_id",
        )
        assert_matches_type(ProjectHostedToolPermissions, hosted_tool_permission, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.admin.organization.projects.hosted_tool_permissions.with_raw_response.retrieve(
            "project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hosted_tool_permission = response.parse()
        assert_matches_type(ProjectHostedToolPermissions, hosted_tool_permission, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.admin.organization.projects.hosted_tool_permissions.with_streaming_response.retrieve(
            "project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hosted_tool_permission = response.parse()
            assert_matches_type(ProjectHostedToolPermissions, hosted_tool_permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.organization.projects.hosted_tool_permissions.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_update(self, client: OpenAI) -> None:
        hosted_tool_permission = client.admin.organization.projects.hosted_tool_permissions.update(
            project_id="project_id",
        )
        assert_matches_type(ProjectHostedToolPermissions, hosted_tool_permission, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: OpenAI) -> None:
        hosted_tool_permission = client.admin.organization.projects.hosted_tool_permissions.update(
            project_id="project_id",
            code_interpreter={"enabled": True},
            file_search={"enabled": True},
            image_generation={"enabled": True},
            mcp={"enabled": True},
            web_search={"enabled": True},
        )
        assert_matches_type(ProjectHostedToolPermissions, hosted_tool_permission, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: OpenAI) -> None:
        response = client.admin.organization.projects.hosted_tool_permissions.with_raw_response.update(
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hosted_tool_permission = response.parse()
        assert_matches_type(ProjectHostedToolPermissions, hosted_tool_permission, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: OpenAI) -> None:
        with client.admin.organization.projects.hosted_tool_permissions.with_streaming_response.update(
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hosted_tool_permission = response.parse()
            assert_matches_type(ProjectHostedToolPermissions, hosted_tool_permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.organization.projects.hosted_tool_permissions.with_raw_response.update(
                project_id="",
            )


class TestAsyncHostedToolPermissions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        hosted_tool_permission = await async_client.admin.organization.projects.hosted_tool_permissions.retrieve(
            "project_id",
        )
        assert_matches_type(ProjectHostedToolPermissions, hosted_tool_permission, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.projects.hosted_tool_permissions.with_raw_response.retrieve(
            "project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hosted_tool_permission = response.parse()
        assert_matches_type(ProjectHostedToolPermissions, hosted_tool_permission, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.projects.hosted_tool_permissions.with_streaming_response.retrieve(
            "project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hosted_tool_permission = await response.parse()
            assert_matches_type(ProjectHostedToolPermissions, hosted_tool_permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.organization.projects.hosted_tool_permissions.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncOpenAI) -> None:
        hosted_tool_permission = await async_client.admin.organization.projects.hosted_tool_permissions.update(
            project_id="project_id",
        )
        assert_matches_type(ProjectHostedToolPermissions, hosted_tool_permission, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncOpenAI) -> None:
        hosted_tool_permission = await async_client.admin.organization.projects.hosted_tool_permissions.update(
            project_id="project_id",
            code_interpreter={"enabled": True},
            file_search={"enabled": True},
            image_generation={"enabled": True},
            mcp={"enabled": True},
            web_search={"enabled": True},
        )
        assert_matches_type(ProjectHostedToolPermissions, hosted_tool_permission, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.projects.hosted_tool_permissions.with_raw_response.update(
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hosted_tool_permission = response.parse()
        assert_matches_type(ProjectHostedToolPermissions, hosted_tool_permission, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.projects.hosted_tool_permissions.with_streaming_response.update(
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hosted_tool_permission = await response.parse()
            assert_matches_type(ProjectHostedToolPermissions, hosted_tool_permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.organization.projects.hosted_tool_permissions.with_raw_response.update(
                project_id="",
            )
