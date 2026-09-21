# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types.webhooks import WebhookEventTypeList

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEventTypes:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        event_type = client.webhooks.event_types.list()
        assert_matches_type(WebhookEventTypeList, event_type, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.webhooks.event_types.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        event_type = response.parse()
        assert_matches_type(WebhookEventTypeList, event_type, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.webhooks.event_types.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            event_type = response.parse()
            assert_matches_type(WebhookEventTypeList, event_type, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncEventTypes:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        event_type = await async_client.webhooks.event_types.list()
        assert_matches_type(WebhookEventTypeList, event_type, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.webhooks.event_types.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        event_type = response.parse()
        assert_matches_type(WebhookEventTypeList, event_type, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.webhooks.event_types.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            event_type = await response.parse()
            assert_matches_type(WebhookEventTypeList, event_type, path=["response"])

        assert cast(Any, response.is_closed) is True
