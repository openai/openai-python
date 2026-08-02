# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types.admin.organization.projects import (
    ProjectSpendLimit,
    ProjectSpendLimitDeleted,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSpendLimit:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        spend_limit = client.admin.organization.projects.spend_limit.retrieve(
            "proj_123",
        )
        assert_matches_type(ProjectSpendLimit, spend_limit, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.admin.organization.projects.spend_limit.with_raw_response.retrieve(
            "proj_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        spend_limit = response.parse()
        assert_matches_type(ProjectSpendLimit, spend_limit, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.admin.organization.projects.spend_limit.with_streaming_response.retrieve(
            "proj_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            spend_limit = response.parse()
            assert_matches_type(ProjectSpendLimit, spend_limit, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.organization.projects.spend_limit.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_update(self, client: OpenAI) -> None:
        spend_limit = client.admin.organization.projects.spend_limit.update(
            project_id="proj_123",
            currency="USD",
            interval="month",
            threshold_amount=1,
        )
        assert_matches_type(ProjectSpendLimit, spend_limit, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: OpenAI) -> None:
        response = client.admin.organization.projects.spend_limit.with_raw_response.update(
            project_id="proj_123",
            currency="USD",
            interval="month",
            threshold_amount=1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        spend_limit = response.parse()
        assert_matches_type(ProjectSpendLimit, spend_limit, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: OpenAI) -> None:
        with client.admin.organization.projects.spend_limit.with_streaming_response.update(
            project_id="proj_123",
            currency="USD",
            interval="month",
            threshold_amount=1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            spend_limit = response.parse()
            assert_matches_type(ProjectSpendLimit, spend_limit, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.organization.projects.spend_limit.with_raw_response.update(
                project_id="",
                currency="USD",
                interval="month",
                threshold_amount=1,
            )

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        spend_limit = client.admin.organization.projects.spend_limit.delete(
            "proj_123",
        )
        assert_matches_type(ProjectSpendLimitDeleted, spend_limit, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.admin.organization.projects.spend_limit.with_raw_response.delete(
            "proj_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        spend_limit = response.parse()
        assert_matches_type(ProjectSpendLimitDeleted, spend_limit, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.admin.organization.projects.spend_limit.with_streaming_response.delete(
            "proj_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            spend_limit = response.parse()
            assert_matches_type(ProjectSpendLimitDeleted, spend_limit, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.organization.projects.spend_limit.with_raw_response.delete(
                "",
            )


class TestAsyncSpendLimit:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        spend_limit = await async_client.admin.organization.projects.spend_limit.retrieve(
            "proj_123",
        )
        assert_matches_type(ProjectSpendLimit, spend_limit, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.projects.spend_limit.with_raw_response.retrieve(
            "proj_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        spend_limit = response.parse()
        assert_matches_type(ProjectSpendLimit, spend_limit, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.projects.spend_limit.with_streaming_response.retrieve(
            "proj_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            spend_limit = await response.parse()
            assert_matches_type(ProjectSpendLimit, spend_limit, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.organization.projects.spend_limit.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncOpenAI) -> None:
        spend_limit = await async_client.admin.organization.projects.spend_limit.update(
            project_id="proj_123",
            currency="USD",
            interval="month",
            threshold_amount=1,
        )
        assert_matches_type(ProjectSpendLimit, spend_limit, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.projects.spend_limit.with_raw_response.update(
            project_id="proj_123",
            currency="USD",
            interval="month",
            threshold_amount=1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        spend_limit = response.parse()
        assert_matches_type(ProjectSpendLimit, spend_limit, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.projects.spend_limit.with_streaming_response.update(
            project_id="proj_123",
            currency="USD",
            interval="month",
            threshold_amount=1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            spend_limit = await response.parse()
            assert_matches_type(ProjectSpendLimit, spend_limit, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.organization.projects.spend_limit.with_raw_response.update(
                project_id="",
                currency="USD",
                interval="month",
                threshold_amount=1,
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        spend_limit = await async_client.admin.organization.projects.spend_limit.delete(
            "proj_123",
        )
        assert_matches_type(ProjectSpendLimitDeleted, spend_limit, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.projects.spend_limit.with_raw_response.delete(
            "proj_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        spend_limit = response.parse()
        assert_matches_type(ProjectSpendLimitDeleted, spend_limit, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.projects.spend_limit.with_streaming_response.delete(
            "proj_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            spend_limit = await response.parse()
            assert_matches_type(ProjectSpendLimitDeleted, spend_limit, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.organization.projects.spend_limit.with_raw_response.delete(
                "",
            )
