# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types.admin.organization.projects import ProjectDataRetention

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDataRetention:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        data_retention = client.admin.organization.projects.data_retention.retrieve(
            "project_id",
        )
        assert_matches_type(ProjectDataRetention, data_retention, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.admin.organization.projects.data_retention.with_raw_response.retrieve(
            "project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data_retention = response.parse()
        assert_matches_type(ProjectDataRetention, data_retention, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.admin.organization.projects.data_retention.with_streaming_response.retrieve(
            "project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data_retention = response.parse()
            assert_matches_type(ProjectDataRetention, data_retention, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.organization.projects.data_retention.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_update(self, client: OpenAI) -> None:
        data_retention = client.admin.organization.projects.data_retention.update(
            project_id="project_id",
            retention_type="organization_default",
        )
        assert_matches_type(ProjectDataRetention, data_retention, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: OpenAI) -> None:
        response = client.admin.organization.projects.data_retention.with_raw_response.update(
            project_id="project_id",
            retention_type="organization_default",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data_retention = response.parse()
        assert_matches_type(ProjectDataRetention, data_retention, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: OpenAI) -> None:
        with client.admin.organization.projects.data_retention.with_streaming_response.update(
            project_id="project_id",
            retention_type="organization_default",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data_retention = response.parse()
            assert_matches_type(ProjectDataRetention, data_retention, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.organization.projects.data_retention.with_raw_response.update(
                project_id="",
                retention_type="organization_default",
            )


class TestAsyncDataRetention:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        data_retention = await async_client.admin.organization.projects.data_retention.retrieve(
            "project_id",
        )
        assert_matches_type(ProjectDataRetention, data_retention, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.projects.data_retention.with_raw_response.retrieve(
            "project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data_retention = response.parse()
        assert_matches_type(ProjectDataRetention, data_retention, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.projects.data_retention.with_streaming_response.retrieve(
            "project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data_retention = await response.parse()
            assert_matches_type(ProjectDataRetention, data_retention, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.organization.projects.data_retention.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncOpenAI) -> None:
        data_retention = await async_client.admin.organization.projects.data_retention.update(
            project_id="project_id",
            retention_type="organization_default",
        )
        assert_matches_type(ProjectDataRetention, data_retention, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.projects.data_retention.with_raw_response.update(
            project_id="project_id",
            retention_type="organization_default",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data_retention = response.parse()
        assert_matches_type(ProjectDataRetention, data_retention, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.projects.data_retention.with_streaming_response.update(
            project_id="project_id",
            retention_type="organization_default",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data_retention = await response.parse()
            assert_matches_type(ProjectDataRetention, data_retention, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.organization.projects.data_retention.with_raw_response.update(
                project_id="",
                retention_type="organization_default",
            )
