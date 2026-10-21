# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types.admin.organization.projects import (
    ProjectModelPermissions,
    ProjectModelPermissionsDeleted,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestModelPermissions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        model_permission = client.admin.organization.projects.model_permissions.retrieve(
            "project_id",
        )
        assert_matches_type(ProjectModelPermissions, model_permission, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.admin.organization.projects.model_permissions.with_raw_response.retrieve(
            "project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model_permission = response.parse()
        assert_matches_type(ProjectModelPermissions, model_permission, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.admin.organization.projects.model_permissions.with_streaming_response.retrieve(
            "project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model_permission = response.parse()
            assert_matches_type(ProjectModelPermissions, model_permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.organization.projects.model_permissions.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_update(self, client: OpenAI) -> None:
        model_permission = client.admin.organization.projects.model_permissions.update(
            project_id="project_id",
            mode="allow_list",
            model_ids=["string"],
        )
        assert_matches_type(ProjectModelPermissions, model_permission, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: OpenAI) -> None:
        response = client.admin.organization.projects.model_permissions.with_raw_response.update(
            project_id="project_id",
            mode="allow_list",
            model_ids=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model_permission = response.parse()
        assert_matches_type(ProjectModelPermissions, model_permission, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: OpenAI) -> None:
        with client.admin.organization.projects.model_permissions.with_streaming_response.update(
            project_id="project_id",
            mode="allow_list",
            model_ids=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model_permission = response.parse()
            assert_matches_type(ProjectModelPermissions, model_permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.organization.projects.model_permissions.with_raw_response.update(
                project_id="",
                mode="allow_list",
                model_ids=["string"],
            )

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        model_permission = client.admin.organization.projects.model_permissions.delete(
            "project_id",
        )
        assert_matches_type(ProjectModelPermissionsDeleted, model_permission, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.admin.organization.projects.model_permissions.with_raw_response.delete(
            "project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model_permission = response.parse()
        assert_matches_type(ProjectModelPermissionsDeleted, model_permission, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.admin.organization.projects.model_permissions.with_streaming_response.delete(
            "project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model_permission = response.parse()
            assert_matches_type(ProjectModelPermissionsDeleted, model_permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.organization.projects.model_permissions.with_raw_response.delete(
                "",
            )


class TestAsyncModelPermissions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        model_permission = await async_client.admin.organization.projects.model_permissions.retrieve(
            "project_id",
        )
        assert_matches_type(ProjectModelPermissions, model_permission, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.projects.model_permissions.with_raw_response.retrieve(
            "project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model_permission = response.parse()
        assert_matches_type(ProjectModelPermissions, model_permission, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.projects.model_permissions.with_streaming_response.retrieve(
            "project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model_permission = await response.parse()
            assert_matches_type(ProjectModelPermissions, model_permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.organization.projects.model_permissions.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncOpenAI) -> None:
        model_permission = await async_client.admin.organization.projects.model_permissions.update(
            project_id="project_id",
            mode="allow_list",
            model_ids=["string"],
        )
        assert_matches_type(ProjectModelPermissions, model_permission, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.projects.model_permissions.with_raw_response.update(
            project_id="project_id",
            mode="allow_list",
            model_ids=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model_permission = response.parse()
        assert_matches_type(ProjectModelPermissions, model_permission, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.projects.model_permissions.with_streaming_response.update(
            project_id="project_id",
            mode="allow_list",
            model_ids=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model_permission = await response.parse()
            assert_matches_type(ProjectModelPermissions, model_permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.organization.projects.model_permissions.with_raw_response.update(
                project_id="",
                mode="allow_list",
                model_ids=["string"],
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        model_permission = await async_client.admin.organization.projects.model_permissions.delete(
            "project_id",
        )
        assert_matches_type(ProjectModelPermissionsDeleted, model_permission, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.projects.model_permissions.with_raw_response.delete(
            "project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model_permission = response.parse()
        assert_matches_type(ProjectModelPermissionsDeleted, model_permission, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.projects.model_permissions.with_streaming_response.delete(
            "project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model_permission = await response.parse()
            assert_matches_type(ProjectModelPermissionsDeleted, model_permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.organization.projects.model_permissions.with_raw_response.delete(
                "",
            )
