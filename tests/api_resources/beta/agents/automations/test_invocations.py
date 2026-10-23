# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.beta.agents.automations import AutomationInvocation

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestInvocations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        invocation = client.beta.agents.automations.invocations.create(
            "automation_id",
        )
        assert_matches_type(AutomationInvocation, invocation, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.beta.agents.automations.invocations.with_raw_response.create(
            "automation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        invocation = response.parse()
        assert_matches_type(AutomationInvocation, invocation, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.beta.agents.automations.invocations.with_streaming_response.create(
            "automation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            invocation = response.parse()
            assert_matches_type(AutomationInvocation, invocation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `automation_id` but received ''"):
            client.beta.agents.automations.invocations.with_raw_response.create(
                "",
            )

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        invocation = client.beta.agents.automations.invocations.retrieve(
            invocation_id="invocation_id",
            automation_id="automation_id",
        )
        assert_matches_type(AutomationInvocation, invocation, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.beta.agents.automations.invocations.with_raw_response.retrieve(
            invocation_id="invocation_id",
            automation_id="automation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        invocation = response.parse()
        assert_matches_type(AutomationInvocation, invocation, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.beta.agents.automations.invocations.with_streaming_response.retrieve(
            invocation_id="invocation_id",
            automation_id="automation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            invocation = response.parse()
            assert_matches_type(AutomationInvocation, invocation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `automation_id` but received ''"):
            client.beta.agents.automations.invocations.with_raw_response.retrieve(
                invocation_id="invocation_id",
                automation_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `invocation_id` but received ''"):
            client.beta.agents.automations.invocations.with_raw_response.retrieve(
                invocation_id="",
                automation_id="automation_id",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        invocation = client.beta.agents.automations.invocations.list(
            automation_id="automation_id",
        )
        assert_matches_type(SyncCursorPage[AutomationInvocation], invocation, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        invocation = client.beta.agents.automations.invocations.list(
            automation_id="automation_id",
            after="after",
            limit=1,
            order="asc",
        )
        assert_matches_type(SyncCursorPage[AutomationInvocation], invocation, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.beta.agents.automations.invocations.with_raw_response.list(
            automation_id="automation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        invocation = response.parse()
        assert_matches_type(SyncCursorPage[AutomationInvocation], invocation, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.beta.agents.automations.invocations.with_streaming_response.list(
            automation_id="automation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            invocation = response.parse()
            assert_matches_type(SyncCursorPage[AutomationInvocation], invocation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `automation_id` but received ''"):
            client.beta.agents.automations.invocations.with_raw_response.list(
                automation_id="",
            )


class TestAsyncInvocations:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        invocation = await async_client.beta.agents.automations.invocations.create(
            "automation_id",
        )
        assert_matches_type(AutomationInvocation, invocation, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.automations.invocations.with_raw_response.create(
            "automation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        invocation = response.parse()
        assert_matches_type(AutomationInvocation, invocation, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.automations.invocations.with_streaming_response.create(
            "automation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            invocation = await response.parse()
            assert_matches_type(AutomationInvocation, invocation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `automation_id` but received ''"):
            await async_client.beta.agents.automations.invocations.with_raw_response.create(
                "",
            )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        invocation = await async_client.beta.agents.automations.invocations.retrieve(
            invocation_id="invocation_id",
            automation_id="automation_id",
        )
        assert_matches_type(AutomationInvocation, invocation, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.automations.invocations.with_raw_response.retrieve(
            invocation_id="invocation_id",
            automation_id="automation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        invocation = response.parse()
        assert_matches_type(AutomationInvocation, invocation, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.automations.invocations.with_streaming_response.retrieve(
            invocation_id="invocation_id",
            automation_id="automation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            invocation = await response.parse()
            assert_matches_type(AutomationInvocation, invocation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `automation_id` but received ''"):
            await async_client.beta.agents.automations.invocations.with_raw_response.retrieve(
                invocation_id="invocation_id",
                automation_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `invocation_id` but received ''"):
            await async_client.beta.agents.automations.invocations.with_raw_response.retrieve(
                invocation_id="",
                automation_id="automation_id",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        invocation = await async_client.beta.agents.automations.invocations.list(
            automation_id="automation_id",
        )
        assert_matches_type(AsyncCursorPage[AutomationInvocation], invocation, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        invocation = await async_client.beta.agents.automations.invocations.list(
            automation_id="automation_id",
            after="after",
            limit=1,
            order="asc",
        )
        assert_matches_type(AsyncCursorPage[AutomationInvocation], invocation, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.automations.invocations.with_raw_response.list(
            automation_id="automation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        invocation = response.parse()
        assert_matches_type(AsyncCursorPage[AutomationInvocation], invocation, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.automations.invocations.with_streaming_response.list(
            automation_id="automation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            invocation = await response.parse()
            assert_matches_type(AsyncCursorPage[AutomationInvocation], invocation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `automation_id` but received ''"):
            await async_client.beta.agents.automations.invocations.with_raw_response.list(
                automation_id="",
            )
