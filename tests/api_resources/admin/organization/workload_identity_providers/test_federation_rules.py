# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.admin.organization.workload_identity_providers import (
    FederationRule,
    FederationRuleDeleted,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFederationRules:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        federation_rule = client.admin.organization.workload_identity_providers.federation_rules.create(
            workload_identity_provider_id="x",
            attribute_matchers={"foo": "string"},
            project_id="x",
            service_account_id="x",
        )
        assert_matches_type(FederationRule, federation_rule, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        federation_rule = client.admin.organization.workload_identity_providers.federation_rules.create(
            workload_identity_provider_id="x",
            attribute_matchers={"foo": "string"},
            project_id="x",
            service_account_id="x",
            description="description",
            enabled=True,
            name="name",
            permissions={"type": "service_account_default"},
        )
        assert_matches_type(FederationRule, federation_rule, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.create(
            workload_identity_provider_id="x",
            attribute_matchers={"foo": "string"},
            project_id="x",
            service_account_id="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        federation_rule = response.parse()
        assert_matches_type(FederationRule, federation_rule, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.admin.organization.workload_identity_providers.federation_rules.with_streaming_response.create(
            workload_identity_provider_id="x",
            attribute_matchers={"foo": "string"},
            project_id="x",
            service_account_id="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            federation_rule = response.parse()
            assert_matches_type(FederationRule, federation_rule, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: OpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `workload_identity_provider_id` but received ''"
        ):
            client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.create(
                workload_identity_provider_id="",
                attribute_matchers={"foo": "string"},
                project_id="x",
                service_account_id="x",
            )

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        federation_rule = client.admin.organization.workload_identity_providers.federation_rules.retrieve(
            workload_identity_federation_rule_id="x",
            workload_identity_provider_id="x",
        )
        assert_matches_type(FederationRule, federation_rule, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.retrieve(
            workload_identity_federation_rule_id="x",
            workload_identity_provider_id="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        federation_rule = response.parse()
        assert_matches_type(FederationRule, federation_rule, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.admin.organization.workload_identity_providers.federation_rules.with_streaming_response.retrieve(
            workload_identity_federation_rule_id="x",
            workload_identity_provider_id="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            federation_rule = response.parse()
            assert_matches_type(FederationRule, federation_rule, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `workload_identity_provider_id` but received ''"
        ):
            client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.retrieve(
                workload_identity_federation_rule_id="x",
                workload_identity_provider_id="",
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `workload_identity_federation_rule_id` but received ''"
        ):
            client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.retrieve(
                workload_identity_federation_rule_id="",
                workload_identity_provider_id="x",
            )

    @parametrize
    def test_method_update(self, client: OpenAI) -> None:
        federation_rule = client.admin.organization.workload_identity_providers.federation_rules.update(
            workload_identity_federation_rule_id="x",
            workload_identity_provider_id="x",
        )
        assert_matches_type(FederationRule, federation_rule, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: OpenAI) -> None:
        federation_rule = client.admin.organization.workload_identity_providers.federation_rules.update(
            workload_identity_federation_rule_id="x",
            workload_identity_provider_id="x",
            attribute_matchers={"foo": "string"},
            description="description",
            enabled=True,
            name="name",
            permissions={"type": "service_account_default"},
        )
        assert_matches_type(FederationRule, federation_rule, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: OpenAI) -> None:
        response = client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.update(
            workload_identity_federation_rule_id="x",
            workload_identity_provider_id="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        federation_rule = response.parse()
        assert_matches_type(FederationRule, federation_rule, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: OpenAI) -> None:
        with client.admin.organization.workload_identity_providers.federation_rules.with_streaming_response.update(
            workload_identity_federation_rule_id="x",
            workload_identity_provider_id="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            federation_rule = response.parse()
            assert_matches_type(FederationRule, federation_rule, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: OpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `workload_identity_provider_id` but received ''"
        ):
            client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.update(
                workload_identity_federation_rule_id="x",
                workload_identity_provider_id="",
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `workload_identity_federation_rule_id` but received ''"
        ):
            client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.update(
                workload_identity_federation_rule_id="",
                workload_identity_provider_id="x",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        federation_rule = client.admin.organization.workload_identity_providers.federation_rules.list(
            workload_identity_provider_id="x",
        )
        assert_matches_type(SyncCursorPage[FederationRule], federation_rule, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        federation_rule = client.admin.organization.workload_identity_providers.federation_rules.list(
            workload_identity_provider_id="x",
            after="x",
            limit=1,
            order="asc",
            service_account_id="x",
        )
        assert_matches_type(SyncCursorPage[FederationRule], federation_rule, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.list(
            workload_identity_provider_id="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        federation_rule = response.parse()
        assert_matches_type(SyncCursorPage[FederationRule], federation_rule, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.admin.organization.workload_identity_providers.federation_rules.with_streaming_response.list(
            workload_identity_provider_id="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            federation_rule = response.parse()
            assert_matches_type(SyncCursorPage[FederationRule], federation_rule, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: OpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `workload_identity_provider_id` but received ''"
        ):
            client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.list(
                workload_identity_provider_id="",
            )

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        federation_rule = client.admin.organization.workload_identity_providers.federation_rules.delete(
            workload_identity_federation_rule_id="x",
            workload_identity_provider_id="x",
        )
        assert_matches_type(FederationRuleDeleted, federation_rule, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.delete(
            workload_identity_federation_rule_id="x",
            workload_identity_provider_id="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        federation_rule = response.parse()
        assert_matches_type(FederationRuleDeleted, federation_rule, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.admin.organization.workload_identity_providers.federation_rules.with_streaming_response.delete(
            workload_identity_federation_rule_id="x",
            workload_identity_provider_id="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            federation_rule = response.parse()
            assert_matches_type(FederationRuleDeleted, federation_rule, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `workload_identity_provider_id` but received ''"
        ):
            client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.delete(
                workload_identity_federation_rule_id="x",
                workload_identity_provider_id="",
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `workload_identity_federation_rule_id` but received ''"
        ):
            client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.delete(
                workload_identity_federation_rule_id="",
                workload_identity_provider_id="x",
            )


class TestAsyncFederationRules:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        federation_rule = await async_client.admin.organization.workload_identity_providers.federation_rules.create(
            workload_identity_provider_id="x",
            attribute_matchers={"foo": "string"},
            project_id="x",
            service_account_id="x",
        )
        assert_matches_type(FederationRule, federation_rule, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        federation_rule = await async_client.admin.organization.workload_identity_providers.federation_rules.create(
            workload_identity_provider_id="x",
            attribute_matchers={"foo": "string"},
            project_id="x",
            service_account_id="x",
            description="description",
            enabled=True,
            name="name",
            permissions={"type": "service_account_default"},
        )
        assert_matches_type(FederationRule, federation_rule, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = (
            await async_client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.create(
                workload_identity_provider_id="x",
                attribute_matchers={"foo": "string"},
                project_id="x",
                service_account_id="x",
            )
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        federation_rule = response.parse()
        assert_matches_type(FederationRule, federation_rule, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with (
            async_client.admin.organization.workload_identity_providers.federation_rules.with_streaming_response.create(
                workload_identity_provider_id="x",
                attribute_matchers={"foo": "string"},
                project_id="x",
                service_account_id="x",
            ) as response
        ):
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            federation_rule = await response.parse()
            assert_matches_type(FederationRule, federation_rule, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `workload_identity_provider_id` but received ''"
        ):
            await async_client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.create(
                workload_identity_provider_id="",
                attribute_matchers={"foo": "string"},
                project_id="x",
                service_account_id="x",
            )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        federation_rule = await async_client.admin.organization.workload_identity_providers.federation_rules.retrieve(
            workload_identity_federation_rule_id="x",
            workload_identity_provider_id="x",
        )
        assert_matches_type(FederationRule, federation_rule, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.retrieve(
            workload_identity_federation_rule_id="x",
            workload_identity_provider_id="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        federation_rule = response.parse()
        assert_matches_type(FederationRule, federation_rule, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with (
            async_client.admin.organization.workload_identity_providers.federation_rules.with_streaming_response.retrieve(
                workload_identity_federation_rule_id="x",
                workload_identity_provider_id="x",
            ) as response
        ):
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            federation_rule = await response.parse()
            assert_matches_type(FederationRule, federation_rule, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `workload_identity_provider_id` but received ''"
        ):
            await (
                async_client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.retrieve(
                    workload_identity_federation_rule_id="x",
                    workload_identity_provider_id="",
                )
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `workload_identity_federation_rule_id` but received ''"
        ):
            await (
                async_client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.retrieve(
                    workload_identity_federation_rule_id="",
                    workload_identity_provider_id="x",
                )
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncOpenAI) -> None:
        federation_rule = await async_client.admin.organization.workload_identity_providers.federation_rules.update(
            workload_identity_federation_rule_id="x",
            workload_identity_provider_id="x",
        )
        assert_matches_type(FederationRule, federation_rule, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncOpenAI) -> None:
        federation_rule = await async_client.admin.organization.workload_identity_providers.federation_rules.update(
            workload_identity_federation_rule_id="x",
            workload_identity_provider_id="x",
            attribute_matchers={"foo": "string"},
            description="description",
            enabled=True,
            name="name",
            permissions={"type": "service_account_default"},
        )
        assert_matches_type(FederationRule, federation_rule, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncOpenAI) -> None:
        response = (
            await async_client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.update(
                workload_identity_federation_rule_id="x",
                workload_identity_provider_id="x",
            )
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        federation_rule = response.parse()
        assert_matches_type(FederationRule, federation_rule, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncOpenAI) -> None:
        async with (
            async_client.admin.organization.workload_identity_providers.federation_rules.with_streaming_response.update(
                workload_identity_federation_rule_id="x",
                workload_identity_provider_id="x",
            ) as response
        ):
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            federation_rule = await response.parse()
            assert_matches_type(FederationRule, federation_rule, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `workload_identity_provider_id` but received ''"
        ):
            await async_client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.update(
                workload_identity_federation_rule_id="x",
                workload_identity_provider_id="",
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `workload_identity_federation_rule_id` but received ''"
        ):
            await async_client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.update(
                workload_identity_federation_rule_id="",
                workload_identity_provider_id="x",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        federation_rule = await async_client.admin.organization.workload_identity_providers.federation_rules.list(
            workload_identity_provider_id="x",
        )
        assert_matches_type(AsyncCursorPage[FederationRule], federation_rule, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        federation_rule = await async_client.admin.organization.workload_identity_providers.federation_rules.list(
            workload_identity_provider_id="x",
            after="x",
            limit=1,
            order="asc",
            service_account_id="x",
        )
        assert_matches_type(AsyncCursorPage[FederationRule], federation_rule, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = (
            await async_client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.list(
                workload_identity_provider_id="x",
            )
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        federation_rule = response.parse()
        assert_matches_type(AsyncCursorPage[FederationRule], federation_rule, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with (
            async_client.admin.organization.workload_identity_providers.federation_rules.with_streaming_response.list(
                workload_identity_provider_id="x",
            ) as response
        ):
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            federation_rule = await response.parse()
            assert_matches_type(AsyncCursorPage[FederationRule], federation_rule, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `workload_identity_provider_id` but received ''"
        ):
            await async_client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.list(
                workload_identity_provider_id="",
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        federation_rule = await async_client.admin.organization.workload_identity_providers.federation_rules.delete(
            workload_identity_federation_rule_id="x",
            workload_identity_provider_id="x",
        )
        assert_matches_type(FederationRuleDeleted, federation_rule, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = (
            await async_client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.delete(
                workload_identity_federation_rule_id="x",
                workload_identity_provider_id="x",
            )
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        federation_rule = response.parse()
        assert_matches_type(FederationRuleDeleted, federation_rule, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with (
            async_client.admin.organization.workload_identity_providers.federation_rules.with_streaming_response.delete(
                workload_identity_federation_rule_id="x",
                workload_identity_provider_id="x",
            ) as response
        ):
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            federation_rule = await response.parse()
            assert_matches_type(FederationRuleDeleted, federation_rule, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `workload_identity_provider_id` but received ''"
        ):
            await async_client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.delete(
                workload_identity_federation_rule_id="x",
                workload_identity_provider_id="",
            )

        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `workload_identity_federation_rule_id` but received ''"
        ):
            await async_client.admin.organization.workload_identity_providers.federation_rules.with_raw_response.delete(
                workload_identity_federation_rule_id="",
                workload_identity_provider_id="x",
            )
