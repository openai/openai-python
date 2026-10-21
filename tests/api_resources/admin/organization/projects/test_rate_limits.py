# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncConversationCursorPage, AsyncConversationCursorPage
from openai.types.admin.organization.projects import (
    ProjectRateLimit,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRateLimits:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list_rate_limits(self, client: OpenAI) -> None:
        rate_limit = client.admin.organization.projects.rate_limits.list_rate_limits(
            project_id="project_id",
        )
        assert_matches_type(SyncConversationCursorPage[ProjectRateLimit], rate_limit, path=["response"])

    @parametrize
    def test_method_list_rate_limits_with_all_params(self, client: OpenAI) -> None:
        rate_limit = client.admin.organization.projects.rate_limits.list_rate_limits(
            project_id="project_id",
            after="after",
            before="before",
            limit=0,
        )
        assert_matches_type(SyncConversationCursorPage[ProjectRateLimit], rate_limit, path=["response"])

    @parametrize
    def test_raw_response_list_rate_limits(self, client: OpenAI) -> None:
        response = client.admin.organization.projects.rate_limits.with_raw_response.list_rate_limits(
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rate_limit = response.parse()
        assert_matches_type(SyncConversationCursorPage[ProjectRateLimit], rate_limit, path=["response"])

    @parametrize
    def test_streaming_response_list_rate_limits(self, client: OpenAI) -> None:
        with client.admin.organization.projects.rate_limits.with_streaming_response.list_rate_limits(
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rate_limit = response.parse()
            assert_matches_type(SyncConversationCursorPage[ProjectRateLimit], rate_limit, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list_rate_limits(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.organization.projects.rate_limits.with_raw_response.list_rate_limits(
                project_id="",
            )

    @parametrize
    def test_method_update_rate_limit(self, client: OpenAI) -> None:
        rate_limit = client.admin.organization.projects.rate_limits.update_rate_limit(
            rate_limit_id="rate_limit_id",
            project_id="project_id",
        )
        assert_matches_type(ProjectRateLimit, rate_limit, path=["response"])

    @parametrize
    def test_method_update_rate_limit_with_all_params(self, client: OpenAI) -> None:
        rate_limit = client.admin.organization.projects.rate_limits.update_rate_limit(
            rate_limit_id="rate_limit_id",
            project_id="project_id",
            batch_1_day_max_input_tokens=0,
            max_audio_megabytes_per_1_minute=0,
            max_images_per_1_minute=0,
            max_requests_per_1_day=0,
            max_requests_per_1_minute=0,
            max_tokens_per_1_minute=0,
        )
        assert_matches_type(ProjectRateLimit, rate_limit, path=["response"])

    @parametrize
    def test_raw_response_update_rate_limit(self, client: OpenAI) -> None:
        response = client.admin.organization.projects.rate_limits.with_raw_response.update_rate_limit(
            rate_limit_id="rate_limit_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rate_limit = response.parse()
        assert_matches_type(ProjectRateLimit, rate_limit, path=["response"])

    @parametrize
    def test_streaming_response_update_rate_limit(self, client: OpenAI) -> None:
        with client.admin.organization.projects.rate_limits.with_streaming_response.update_rate_limit(
            rate_limit_id="rate_limit_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rate_limit = response.parse()
            assert_matches_type(ProjectRateLimit, rate_limit, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update_rate_limit(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.organization.projects.rate_limits.with_raw_response.update_rate_limit(
                rate_limit_id="rate_limit_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `rate_limit_id` but received ''"):
            client.admin.organization.projects.rate_limits.with_raw_response.update_rate_limit(
                rate_limit_id="",
                project_id="project_id",
            )


class TestAsyncRateLimits:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_list_rate_limits(self, async_client: AsyncOpenAI) -> None:
        rate_limit = await async_client.admin.organization.projects.rate_limits.list_rate_limits(
            project_id="project_id",
        )
        assert_matches_type(AsyncConversationCursorPage[ProjectRateLimit], rate_limit, path=["response"])

    @parametrize
    async def test_method_list_rate_limits_with_all_params(self, async_client: AsyncOpenAI) -> None:
        rate_limit = await async_client.admin.organization.projects.rate_limits.list_rate_limits(
            project_id="project_id",
            after="after",
            before="before",
            limit=0,
        )
        assert_matches_type(AsyncConversationCursorPage[ProjectRateLimit], rate_limit, path=["response"])

    @parametrize
    async def test_raw_response_list_rate_limits(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.projects.rate_limits.with_raw_response.list_rate_limits(
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rate_limit = response.parse()
        assert_matches_type(AsyncConversationCursorPage[ProjectRateLimit], rate_limit, path=["response"])

    @parametrize
    async def test_streaming_response_list_rate_limits(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.projects.rate_limits.with_streaming_response.list_rate_limits(
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rate_limit = await response.parse()
            assert_matches_type(AsyncConversationCursorPage[ProjectRateLimit], rate_limit, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list_rate_limits(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.organization.projects.rate_limits.with_raw_response.list_rate_limits(
                project_id="",
            )

    @parametrize
    async def test_method_update_rate_limit(self, async_client: AsyncOpenAI) -> None:
        rate_limit = await async_client.admin.organization.projects.rate_limits.update_rate_limit(
            rate_limit_id="rate_limit_id",
            project_id="project_id",
        )
        assert_matches_type(ProjectRateLimit, rate_limit, path=["response"])

    @parametrize
    async def test_method_update_rate_limit_with_all_params(self, async_client: AsyncOpenAI) -> None:
        rate_limit = await async_client.admin.organization.projects.rate_limits.update_rate_limit(
            rate_limit_id="rate_limit_id",
            project_id="project_id",
            batch_1_day_max_input_tokens=0,
            max_audio_megabytes_per_1_minute=0,
            max_images_per_1_minute=0,
            max_requests_per_1_day=0,
            max_requests_per_1_minute=0,
            max_tokens_per_1_minute=0,
        )
        assert_matches_type(ProjectRateLimit, rate_limit, path=["response"])

    @parametrize
    async def test_raw_response_update_rate_limit(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.projects.rate_limits.with_raw_response.update_rate_limit(
            rate_limit_id="rate_limit_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rate_limit = response.parse()
        assert_matches_type(ProjectRateLimit, rate_limit, path=["response"])

    @parametrize
    async def test_streaming_response_update_rate_limit(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.projects.rate_limits.with_streaming_response.update_rate_limit(
            rate_limit_id="rate_limit_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rate_limit = await response.parse()
            assert_matches_type(ProjectRateLimit, rate_limit, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update_rate_limit(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.organization.projects.rate_limits.with_raw_response.update_rate_limit(
                rate_limit_id="rate_limit_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `rate_limit_id` but received ''"):
            await async_client.admin.organization.projects.rate_limits.with_raw_response.update_rate_limit(
                rate_limit_id="",
                project_id="project_id",
            )
