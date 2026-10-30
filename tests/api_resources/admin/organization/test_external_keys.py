# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.admin.organization import (
    ExternalKey,
    ExternalKeyValidateResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestExternalKeys:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create_overload_1(self, client: OpenAI) -> None:
        external_key = client.admin.organization.external_keys.create(
            external_id="external_id",
            kms_arn="kms_arn",
            name="name",
            role_arn="arn:aws:iam::123456789012:role/example-role",
            type="aws",
        )
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    def test_method_create_with_all_params_overload_1(self, client: OpenAI) -> None:
        external_key = client.admin.organization.external_keys.create(
            external_id="external_id",
            kms_arn="kms_arn",
            name="name",
            role_arn="arn:aws:iam::123456789012:role/example-role",
            type="aws",
            purpose="ekm",
        )
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    def test_raw_response_create_overload_1(self, client: OpenAI) -> None:
        response = client.admin.organization.external_keys.with_raw_response.create(
            external_id="external_id",
            kms_arn="kms_arn",
            name="name",
            role_arn="arn:aws:iam::123456789012:role/example-role",
            type="aws",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_key = response.parse()
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    def test_streaming_response_create_overload_1(self, client: OpenAI) -> None:
        with client.admin.organization.external_keys.with_streaming_response.create(
            external_id="external_id",
            kms_arn="kms_arn",
            name="name",
            role_arn="arn:aws:iam::123456789012:role/example-role",
            type="aws",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_key = response.parse()
            assert_matches_type(ExternalKey, external_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_create_overload_2(self, client: OpenAI) -> None:
        external_key = client.admin.organization.external_keys.create(
            audience="audience",
            kms_key_location="kms_key_location",
            kms_key_name="kms_key_name",
            kms_key_ring_name="kms_key_ring_name",
            kms_project_id="kms_project_id",
            name="name",
            type="gcp",
            workload_identity_pool_id="workload_identity_pool_id",
            workload_identity_project_number="workload_identity_project_number",
            workload_identity_provider_id="workload_identity_provider_id",
        )
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    def test_method_create_with_all_params_overload_2(self, client: OpenAI) -> None:
        external_key = client.admin.organization.external_keys.create(
            audience="audience",
            kms_key_location="kms_key_location",
            kms_key_name="kms_key_name",
            kms_key_ring_name="kms_key_ring_name",
            kms_project_id="kms_project_id",
            name="name",
            type="gcp",
            workload_identity_pool_id="workload_identity_pool_id",
            workload_identity_project_number="workload_identity_project_number",
            workload_identity_provider_id="workload_identity_provider_id",
            kms_key_version="kms_key_version",
            purpose="ekm",
        )
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    def test_raw_response_create_overload_2(self, client: OpenAI) -> None:
        response = client.admin.organization.external_keys.with_raw_response.create(
            audience="audience",
            kms_key_location="kms_key_location",
            kms_key_name="kms_key_name",
            kms_key_ring_name="kms_key_ring_name",
            kms_project_id="kms_project_id",
            name="name",
            type="gcp",
            workload_identity_pool_id="workload_identity_pool_id",
            workload_identity_project_number="workload_identity_project_number",
            workload_identity_provider_id="workload_identity_provider_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_key = response.parse()
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    def test_streaming_response_create_overload_2(self, client: OpenAI) -> None:
        with client.admin.organization.external_keys.with_streaming_response.create(
            audience="audience",
            kms_key_location="kms_key_location",
            kms_key_name="kms_key_name",
            kms_key_ring_name="kms_key_ring_name",
            kms_project_id="kms_project_id",
            name="name",
            type="gcp",
            workload_identity_pool_id="workload_identity_pool_id",
            workload_identity_project_number="workload_identity_project_number",
            workload_identity_provider_id="workload_identity_provider_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_key = response.parse()
            assert_matches_type(ExternalKey, external_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_create_overload_3(self, client: OpenAI) -> None:
        external_key = client.admin.organization.external_keys.create(
            key_name="key_name",
            name="name",
            tenant_id="tenant_id",
            type="azure",
            vault_uri="vault_uri",
        )
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    def test_method_create_with_all_params_overload_3(self, client: OpenAI) -> None:
        external_key = client.admin.organization.external_keys.create(
            key_name="key_name",
            name="name",
            tenant_id="tenant_id",
            type="azure",
            vault_uri="vault_uri",
            key_version="key_version",
            purpose="ekm",
        )
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    def test_raw_response_create_overload_3(self, client: OpenAI) -> None:
        response = client.admin.organization.external_keys.with_raw_response.create(
            key_name="key_name",
            name="name",
            tenant_id="tenant_id",
            type="azure",
            vault_uri="vault_uri",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_key = response.parse()
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    def test_streaming_response_create_overload_3(self, client: OpenAI) -> None:
        with client.admin.organization.external_keys.with_streaming_response.create(
            key_name="key_name",
            name="name",
            tenant_id="tenant_id",
            type="azure",
            vault_uri="vault_uri",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_key = response.parse()
            assert_matches_type(ExternalKey, external_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        external_key = client.admin.organization.external_keys.retrieve(
            "external_key_id",
        )
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.admin.organization.external_keys.with_raw_response.retrieve(
            "external_key_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_key = response.parse()
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.admin.organization.external_keys.with_streaming_response.retrieve(
            "external_key_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_key = response.parse()
            assert_matches_type(ExternalKey, external_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `external_key_id` but received ''"):
            client.admin.organization.external_keys.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        external_key = client.admin.organization.external_keys.list()
        assert_matches_type(SyncCursorPage[ExternalKey], external_key, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        external_key = client.admin.organization.external_keys.list(
            after="after",
            limit=0,
            order="asc",
            purpose="ekm",
        )
        assert_matches_type(SyncCursorPage[ExternalKey], external_key, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.admin.organization.external_keys.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_key = response.parse()
        assert_matches_type(SyncCursorPage[ExternalKey], external_key, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.admin.organization.external_keys.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_key = response.parse()
            assert_matches_type(SyncCursorPage[ExternalKey], external_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        external_key = client.admin.organization.external_keys.delete(
            "external_key_id",
        )
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.admin.organization.external_keys.with_raw_response.delete(
            "external_key_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_key = response.parse()
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.admin.organization.external_keys.with_streaming_response.delete(
            "external_key_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_key = response.parse()
            assert_matches_type(ExternalKey, external_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `external_key_id` but received ''"):
            client.admin.organization.external_keys.with_raw_response.delete(
                "",
            )

    @parametrize
    def test_method_validate(self, client: OpenAI) -> None:
        external_key = client.admin.organization.external_keys.validate(
            "external_key_id",
        )
        assert_matches_type(ExternalKeyValidateResponse, external_key, path=["response"])

    @parametrize
    def test_raw_response_validate(self, client: OpenAI) -> None:
        response = client.admin.organization.external_keys.with_raw_response.validate(
            "external_key_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_key = response.parse()
        assert_matches_type(ExternalKeyValidateResponse, external_key, path=["response"])

    @parametrize
    def test_streaming_response_validate(self, client: OpenAI) -> None:
        with client.admin.organization.external_keys.with_streaming_response.validate(
            "external_key_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_key = response.parse()
            assert_matches_type(ExternalKeyValidateResponse, external_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_validate(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `external_key_id` but received ''"):
            client.admin.organization.external_keys.with_raw_response.validate(
                "",
            )


class TestAsyncExternalKeys:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        external_key = await async_client.admin.organization.external_keys.create(
            external_id="external_id",
            kms_arn="kms_arn",
            name="name",
            role_arn="arn:aws:iam::123456789012:role/example-role",
            type="aws",
        )
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    async def test_method_create_with_all_params_overload_1(self, async_client: AsyncOpenAI) -> None:
        external_key = await async_client.admin.organization.external_keys.create(
            external_id="external_id",
            kms_arn="kms_arn",
            name="name",
            role_arn="arn:aws:iam::123456789012:role/example-role",
            type="aws",
            purpose="ekm",
        )
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    async def test_raw_response_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.external_keys.with_raw_response.create(
            external_id="external_id",
            kms_arn="kms_arn",
            name="name",
            role_arn="arn:aws:iam::123456789012:role/example-role",
            type="aws",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_key = response.parse()
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    async def test_streaming_response_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.external_keys.with_streaming_response.create(
            external_id="external_id",
            kms_arn="kms_arn",
            name="name",
            role_arn="arn:aws:iam::123456789012:role/example-role",
            type="aws",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_key = await response.parse()
            assert_matches_type(ExternalKey, external_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_create_overload_2(self, async_client: AsyncOpenAI) -> None:
        external_key = await async_client.admin.organization.external_keys.create(
            audience="audience",
            kms_key_location="kms_key_location",
            kms_key_name="kms_key_name",
            kms_key_ring_name="kms_key_ring_name",
            kms_project_id="kms_project_id",
            name="name",
            type="gcp",
            workload_identity_pool_id="workload_identity_pool_id",
            workload_identity_project_number="workload_identity_project_number",
            workload_identity_provider_id="workload_identity_provider_id",
        )
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    async def test_method_create_with_all_params_overload_2(self, async_client: AsyncOpenAI) -> None:
        external_key = await async_client.admin.organization.external_keys.create(
            audience="audience",
            kms_key_location="kms_key_location",
            kms_key_name="kms_key_name",
            kms_key_ring_name="kms_key_ring_name",
            kms_project_id="kms_project_id",
            name="name",
            type="gcp",
            workload_identity_pool_id="workload_identity_pool_id",
            workload_identity_project_number="workload_identity_project_number",
            workload_identity_provider_id="workload_identity_provider_id",
            kms_key_version="kms_key_version",
            purpose="ekm",
        )
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    async def test_raw_response_create_overload_2(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.external_keys.with_raw_response.create(
            audience="audience",
            kms_key_location="kms_key_location",
            kms_key_name="kms_key_name",
            kms_key_ring_name="kms_key_ring_name",
            kms_project_id="kms_project_id",
            name="name",
            type="gcp",
            workload_identity_pool_id="workload_identity_pool_id",
            workload_identity_project_number="workload_identity_project_number",
            workload_identity_provider_id="workload_identity_provider_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_key = response.parse()
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    async def test_streaming_response_create_overload_2(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.external_keys.with_streaming_response.create(
            audience="audience",
            kms_key_location="kms_key_location",
            kms_key_name="kms_key_name",
            kms_key_ring_name="kms_key_ring_name",
            kms_project_id="kms_project_id",
            name="name",
            type="gcp",
            workload_identity_pool_id="workload_identity_pool_id",
            workload_identity_project_number="workload_identity_project_number",
            workload_identity_provider_id="workload_identity_provider_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_key = await response.parse()
            assert_matches_type(ExternalKey, external_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_create_overload_3(self, async_client: AsyncOpenAI) -> None:
        external_key = await async_client.admin.organization.external_keys.create(
            key_name="key_name",
            name="name",
            tenant_id="tenant_id",
            type="azure",
            vault_uri="vault_uri",
        )
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    async def test_method_create_with_all_params_overload_3(self, async_client: AsyncOpenAI) -> None:
        external_key = await async_client.admin.organization.external_keys.create(
            key_name="key_name",
            name="name",
            tenant_id="tenant_id",
            type="azure",
            vault_uri="vault_uri",
            key_version="key_version",
            purpose="ekm",
        )
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    async def test_raw_response_create_overload_3(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.external_keys.with_raw_response.create(
            key_name="key_name",
            name="name",
            tenant_id="tenant_id",
            type="azure",
            vault_uri="vault_uri",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_key = response.parse()
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    async def test_streaming_response_create_overload_3(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.external_keys.with_streaming_response.create(
            key_name="key_name",
            name="name",
            tenant_id="tenant_id",
            type="azure",
            vault_uri="vault_uri",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_key = await response.parse()
            assert_matches_type(ExternalKey, external_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        external_key = await async_client.admin.organization.external_keys.retrieve(
            "external_key_id",
        )
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.external_keys.with_raw_response.retrieve(
            "external_key_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_key = response.parse()
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.external_keys.with_streaming_response.retrieve(
            "external_key_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_key = await response.parse()
            assert_matches_type(ExternalKey, external_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `external_key_id` but received ''"):
            await async_client.admin.organization.external_keys.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        external_key = await async_client.admin.organization.external_keys.list()
        assert_matches_type(AsyncCursorPage[ExternalKey], external_key, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        external_key = await async_client.admin.organization.external_keys.list(
            after="after",
            limit=0,
            order="asc",
            purpose="ekm",
        )
        assert_matches_type(AsyncCursorPage[ExternalKey], external_key, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.external_keys.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_key = response.parse()
        assert_matches_type(AsyncCursorPage[ExternalKey], external_key, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.external_keys.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_key = await response.parse()
            assert_matches_type(AsyncCursorPage[ExternalKey], external_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        external_key = await async_client.admin.organization.external_keys.delete(
            "external_key_id",
        )
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.external_keys.with_raw_response.delete(
            "external_key_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_key = response.parse()
        assert_matches_type(ExternalKey, external_key, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.external_keys.with_streaming_response.delete(
            "external_key_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_key = await response.parse()
            assert_matches_type(ExternalKey, external_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `external_key_id` but received ''"):
            await async_client.admin.organization.external_keys.with_raw_response.delete(
                "",
            )

    @parametrize
    async def test_method_validate(self, async_client: AsyncOpenAI) -> None:
        external_key = await async_client.admin.organization.external_keys.validate(
            "external_key_id",
        )
        assert_matches_type(ExternalKeyValidateResponse, external_key, path=["response"])

    @parametrize
    async def test_raw_response_validate(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.external_keys.with_raw_response.validate(
            "external_key_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        external_key = response.parse()
        assert_matches_type(ExternalKeyValidateResponse, external_key, path=["response"])

    @parametrize
    async def test_streaming_response_validate(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.external_keys.with_streaming_response.validate(
            "external_key_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            external_key = await response.parse()
            assert_matches_type(ExternalKeyValidateResponse, external_key, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_validate(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `external_key_id` but received ''"):
            await async_client.admin.organization.external_keys.with_raw_response.validate(
                "",
            )
