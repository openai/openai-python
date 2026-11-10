# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.admin.organization import (
    WorkloadIdentityProvider,
    WorkloadIdentityProviderDeleted,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestWorkloadIdentityProviders:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        workload_identity_provider = client.admin.organization.workload_identity_providers.create(
            audience="x",
            issuer="x",
            name="x",
            type="oidc",
        )
        assert_matches_type(WorkloadIdentityProvider, workload_identity_provider, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        workload_identity_provider = client.admin.organization.workload_identity_providers.create(
            audience="x",
            issuer="x",
            name="x",
            type="oidc",
            attribute_transformations=[
                {
                    "attribute": "x",
                    "expression": "x",
                }
            ],
            description="description",
            enabled=True,
            verification={
                "discovery_url": "discovery_url",
                "type": "discovery",
            },
        )
        assert_matches_type(WorkloadIdentityProvider, workload_identity_provider, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.admin.organization.workload_identity_providers.with_raw_response.create(
            audience="x",
            issuer="x",
            name="x",
            type="oidc",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workload_identity_provider = response.parse()
        assert_matches_type(WorkloadIdentityProvider, workload_identity_provider, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.admin.organization.workload_identity_providers.with_streaming_response.create(
            audience="x",
            issuer="x",
            name="x",
            type="oidc",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workload_identity_provider = response.parse()
            assert_matches_type(WorkloadIdentityProvider, workload_identity_provider, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        workload_identity_provider = client.admin.organization.workload_identity_providers.retrieve(
            "x",
        )
        assert_matches_type(WorkloadIdentityProvider, workload_identity_provider, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.admin.organization.workload_identity_providers.with_raw_response.retrieve(
            "x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workload_identity_provider = response.parse()
        assert_matches_type(WorkloadIdentityProvider, workload_identity_provider, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.admin.organization.workload_identity_providers.with_streaming_response.retrieve(
            "x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workload_identity_provider = response.parse()
            assert_matches_type(WorkloadIdentityProvider, workload_identity_provider, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `workload_identity_provider_id` but received ''"
        ):
            client.admin.organization.workload_identity_providers.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_update(self, client: OpenAI) -> None:
        workload_identity_provider = client.admin.organization.workload_identity_providers.update(
            workload_identity_provider_id="x",
        )
        assert_matches_type(WorkloadIdentityProvider, workload_identity_provider, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: OpenAI) -> None:
        workload_identity_provider = client.admin.organization.workload_identity_providers.update(
            workload_identity_provider_id="x",
            attribute_transformations=[
                {
                    "attribute": "x",
                    "expression": "x",
                }
            ],
            audience="x",
            description="description",
            enabled=True,
            issuer="x",
            name="x",
            verification={
                "discovery_url": "discovery_url",
                "type": "discovery",
            },
        )
        assert_matches_type(WorkloadIdentityProvider, workload_identity_provider, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: OpenAI) -> None:
        response = client.admin.organization.workload_identity_providers.with_raw_response.update(
            workload_identity_provider_id="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workload_identity_provider = response.parse()
        assert_matches_type(WorkloadIdentityProvider, workload_identity_provider, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: OpenAI) -> None:
        with client.admin.organization.workload_identity_providers.with_streaming_response.update(
            workload_identity_provider_id="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workload_identity_provider = response.parse()
            assert_matches_type(WorkloadIdentityProvider, workload_identity_provider, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: OpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `workload_identity_provider_id` but received ''"
        ):
            client.admin.organization.workload_identity_providers.with_raw_response.update(
                workload_identity_provider_id="",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        workload_identity_provider = client.admin.organization.workload_identity_providers.list()
        assert_matches_type(SyncCursorPage[WorkloadIdentityProvider], workload_identity_provider, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        workload_identity_provider = client.admin.organization.workload_identity_providers.list(
            after="x",
            limit=1,
            order="asc",
        )
        assert_matches_type(SyncCursorPage[WorkloadIdentityProvider], workload_identity_provider, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.admin.organization.workload_identity_providers.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workload_identity_provider = response.parse()
        assert_matches_type(SyncCursorPage[WorkloadIdentityProvider], workload_identity_provider, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.admin.organization.workload_identity_providers.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workload_identity_provider = response.parse()
            assert_matches_type(SyncCursorPage[WorkloadIdentityProvider], workload_identity_provider, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        workload_identity_provider = client.admin.organization.workload_identity_providers.delete(
            "x",
        )
        assert_matches_type(WorkloadIdentityProviderDeleted, workload_identity_provider, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.admin.organization.workload_identity_providers.with_raw_response.delete(
            "x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workload_identity_provider = response.parse()
        assert_matches_type(WorkloadIdentityProviderDeleted, workload_identity_provider, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.admin.organization.workload_identity_providers.with_streaming_response.delete(
            "x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workload_identity_provider = response.parse()
            assert_matches_type(WorkloadIdentityProviderDeleted, workload_identity_provider, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `workload_identity_provider_id` but received ''"
        ):
            client.admin.organization.workload_identity_providers.with_raw_response.delete(
                "",
            )


class TestAsyncWorkloadIdentityProviders:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        workload_identity_provider = await async_client.admin.organization.workload_identity_providers.create(
            audience="x",
            issuer="x",
            name="x",
            type="oidc",
        )
        assert_matches_type(WorkloadIdentityProvider, workload_identity_provider, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        workload_identity_provider = await async_client.admin.organization.workload_identity_providers.create(
            audience="x",
            issuer="x",
            name="x",
            type="oidc",
            attribute_transformations=[
                {
                    "attribute": "x",
                    "expression": "x",
                }
            ],
            description="description",
            enabled=True,
            verification={
                "discovery_url": "discovery_url",
                "type": "discovery",
            },
        )
        assert_matches_type(WorkloadIdentityProvider, workload_identity_provider, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.workload_identity_providers.with_raw_response.create(
            audience="x",
            issuer="x",
            name="x",
            type="oidc",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workload_identity_provider = response.parse()
        assert_matches_type(WorkloadIdentityProvider, workload_identity_provider, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.workload_identity_providers.with_streaming_response.create(
            audience="x",
            issuer="x",
            name="x",
            type="oidc",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workload_identity_provider = await response.parse()
            assert_matches_type(WorkloadIdentityProvider, workload_identity_provider, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        workload_identity_provider = await async_client.admin.organization.workload_identity_providers.retrieve(
            "x",
        )
        assert_matches_type(WorkloadIdentityProvider, workload_identity_provider, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.workload_identity_providers.with_raw_response.retrieve(
            "x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workload_identity_provider = response.parse()
        assert_matches_type(WorkloadIdentityProvider, workload_identity_provider, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.workload_identity_providers.with_streaming_response.retrieve(
            "x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workload_identity_provider = await response.parse()
            assert_matches_type(WorkloadIdentityProvider, workload_identity_provider, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `workload_identity_provider_id` but received ''"
        ):
            await async_client.admin.organization.workload_identity_providers.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncOpenAI) -> None:
        workload_identity_provider = await async_client.admin.organization.workload_identity_providers.update(
            workload_identity_provider_id="x",
        )
        assert_matches_type(WorkloadIdentityProvider, workload_identity_provider, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncOpenAI) -> None:
        workload_identity_provider = await async_client.admin.organization.workload_identity_providers.update(
            workload_identity_provider_id="x",
            attribute_transformations=[
                {
                    "attribute": "x",
                    "expression": "x",
                }
            ],
            audience="x",
            description="description",
            enabled=True,
            issuer="x",
            name="x",
            verification={
                "discovery_url": "discovery_url",
                "type": "discovery",
            },
        )
        assert_matches_type(WorkloadIdentityProvider, workload_identity_provider, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.workload_identity_providers.with_raw_response.update(
            workload_identity_provider_id="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workload_identity_provider = response.parse()
        assert_matches_type(WorkloadIdentityProvider, workload_identity_provider, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.workload_identity_providers.with_streaming_response.update(
            workload_identity_provider_id="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workload_identity_provider = await response.parse()
            assert_matches_type(WorkloadIdentityProvider, workload_identity_provider, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `workload_identity_provider_id` but received ''"
        ):
            await async_client.admin.organization.workload_identity_providers.with_raw_response.update(
                workload_identity_provider_id="",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        workload_identity_provider = await async_client.admin.organization.workload_identity_providers.list()
        assert_matches_type(AsyncCursorPage[WorkloadIdentityProvider], workload_identity_provider, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        workload_identity_provider = await async_client.admin.organization.workload_identity_providers.list(
            after="x",
            limit=1,
            order="asc",
        )
        assert_matches_type(AsyncCursorPage[WorkloadIdentityProvider], workload_identity_provider, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.workload_identity_providers.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workload_identity_provider = response.parse()
        assert_matches_type(AsyncCursorPage[WorkloadIdentityProvider], workload_identity_provider, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with (
            async_client.admin.organization.workload_identity_providers.with_streaming_response.list() as response
        ):
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workload_identity_provider = await response.parse()
            assert_matches_type(
                AsyncCursorPage[WorkloadIdentityProvider], workload_identity_provider, path=["response"]
            )

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        workload_identity_provider = await async_client.admin.organization.workload_identity_providers.delete(
            "x",
        )
        assert_matches_type(WorkloadIdentityProviderDeleted, workload_identity_provider, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.workload_identity_providers.with_raw_response.delete(
            "x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        workload_identity_provider = response.parse()
        assert_matches_type(WorkloadIdentityProviderDeleted, workload_identity_provider, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.workload_identity_providers.with_streaming_response.delete(
            "x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            workload_identity_provider = await response.parse()
            assert_matches_type(WorkloadIdentityProviderDeleted, workload_identity_provider, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `workload_identity_provider_id` but received ''"
        ):
            await async_client.admin.organization.workload_identity_providers.with_raw_response.delete(
                "",
            )
