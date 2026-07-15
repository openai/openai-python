# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types.admin.organization.projects.service_accounts import APIKeyCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAPIKeys:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        api_key = client.admin.organization.projects.service_accounts.api_keys.create(
            service_account_id="service_account_id",
            project_id="project_id",
        )
        assert_matches_type(APIKeyCreateResponse, api_key, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        api_key = client.admin.organization.projects.service_accounts.api_keys.create(
            service_account_id="service_account_id",
            project_id="project_id",
            name="name",
            scopes=["string"],
        )
        assert_matches_type(APIKeyCreateResponse, api_key, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.admin.organization.projects.service_accounts.api_keys.with_raw_response.create(
            service_account_id="service_account_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api_key = response.parse()
        assert_matches_type(APIKeyCreateResponse, api_key, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.admin.organization.projects.service_accounts.api_keys.with_streaming_response.create(
            service_account_id="service_account_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api_key = response.parse()
            assert_matches_type(APIKeyCreateResponse, api_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.organization.projects.service_accounts.api_keys.with_raw_response.create(
                service_account_id="service_account_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `service_account_id` but received ''"):
            client.admin.organization.projects.service_accounts.api_keys.with_raw_response.create(
                service_account_id="",
                project_id="project_id",
            )


class TestAsyncAPIKeys:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        api_key = await async_client.admin.organization.projects.service_accounts.api_keys.create(
            service_account_id="service_account_id",
            project_id="project_id",
        )
        assert_matches_type(APIKeyCreateResponse, api_key, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        api_key = await async_client.admin.organization.projects.service_accounts.api_keys.create(
            service_account_id="service_account_id",
            project_id="project_id",
            name="name",
            scopes=["string"],
        )
        assert_matches_type(APIKeyCreateResponse, api_key, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.projects.service_accounts.api_keys.with_raw_response.create(
            service_account_id="service_account_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        api_key = response.parse()
        assert_matches_type(APIKeyCreateResponse, api_key, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.projects.service_accounts.api_keys.with_streaming_response.create(
            service_account_id="service_account_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            api_key = await response.parse()
            assert_matches_type(APIKeyCreateResponse, api_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.organization.projects.service_accounts.api_keys.with_raw_response.create(
                service_account_id="service_account_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `service_account_id` but received ''"):
            await async_client.admin.organization.projects.service_accounts.api_keys.with_raw_response.create(
                service_account_id="",
                project_id="project_id",
            )
