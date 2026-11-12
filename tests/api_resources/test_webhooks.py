# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.webhooks import (
    WebhookEndpoint,
    DeletedWebhookEndpoint,
    WebhookEndpointTestResult,
    WebhookEndpointWithSecret,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestWebhooks:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        webhook = client.webhooks.create(
            event_types=["batch.completed"],
            name="x",
            url="https://",
        )
        assert_matches_type(WebhookEndpointWithSecret, webhook, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.webhooks.with_raw_response.create(
            event_types=["batch.completed"],
            name="x",
            url="https://",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = response.parse()
        assert_matches_type(WebhookEndpointWithSecret, webhook, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.webhooks.with_streaming_response.create(
            event_types=["batch.completed"],
            name="x",
            url="https://",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = response.parse()
            assert_matches_type(WebhookEndpointWithSecret, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        webhook = client.webhooks.retrieve(
            "whe_123",
        )
        assert_matches_type(WebhookEndpoint, webhook, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.webhooks.with_raw_response.retrieve(
            "whe_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = response.parse()
        assert_matches_type(WebhookEndpoint, webhook, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.webhooks.with_streaming_response.retrieve(
            "whe_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = response.parse()
            assert_matches_type(WebhookEndpoint, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `webhook_endpoint_id` but received ''"):
            client.webhooks.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_update(self, client: OpenAI) -> None:
        webhook = client.webhooks.update(
            webhook_endpoint_id="whe_123",
        )
        assert_matches_type(WebhookEndpoint, webhook, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: OpenAI) -> None:
        webhook = client.webhooks.update(
            webhook_endpoint_id="whe_123",
            event_types=["batch.completed"],
            name="x",
            url="https://",
        )
        assert_matches_type(WebhookEndpoint, webhook, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: OpenAI) -> None:
        response = client.webhooks.with_raw_response.update(
            webhook_endpoint_id="whe_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = response.parse()
        assert_matches_type(WebhookEndpoint, webhook, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: OpenAI) -> None:
        with client.webhooks.with_streaming_response.update(
            webhook_endpoint_id="whe_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = response.parse()
            assert_matches_type(WebhookEndpoint, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `webhook_endpoint_id` but received ''"):
            client.webhooks.with_raw_response.update(
                webhook_endpoint_id="",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        webhook = client.webhooks.list()
        assert_matches_type(SyncCursorPage[WebhookEndpoint], webhook, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        webhook = client.webhooks.list(
            after="whe_123",
            limit=1,
        )
        assert_matches_type(SyncCursorPage[WebhookEndpoint], webhook, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.webhooks.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = response.parse()
        assert_matches_type(SyncCursorPage[WebhookEndpoint], webhook, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.webhooks.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = response.parse()
            assert_matches_type(SyncCursorPage[WebhookEndpoint], webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        webhook = client.webhooks.delete(
            "whe_123",
        )
        assert_matches_type(DeletedWebhookEndpoint, webhook, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.webhooks.with_raw_response.delete(
            "whe_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = response.parse()
        assert_matches_type(DeletedWebhookEndpoint, webhook, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.webhooks.with_streaming_response.delete(
            "whe_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = response.parse()
            assert_matches_type(DeletedWebhookEndpoint, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `webhook_endpoint_id` but received ''"):
            client.webhooks.with_raw_response.delete(
                "",
            )

    @parametrize
    def test_method_rotate_secret(self, client: OpenAI) -> None:
        webhook = client.webhooks.rotate_secret(
            webhook_endpoint_id="whe_123",
        )
        assert_matches_type(WebhookEndpointWithSecret, webhook, path=["response"])

    @parametrize
    def test_method_rotate_secret_with_all_params(self, client: OpenAI) -> None:
        webhook = client.webhooks.rotate_secret(
            webhook_endpoint_id="whe_123",
            keep_old_secret_active_for_24_hours=True,
        )
        assert_matches_type(WebhookEndpointWithSecret, webhook, path=["response"])

    @parametrize
    def test_raw_response_rotate_secret(self, client: OpenAI) -> None:
        response = client.webhooks.with_raw_response.rotate_secret(
            webhook_endpoint_id="whe_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = response.parse()
        assert_matches_type(WebhookEndpointWithSecret, webhook, path=["response"])

    @parametrize
    def test_streaming_response_rotate_secret(self, client: OpenAI) -> None:
        with client.webhooks.with_streaming_response.rotate_secret(
            webhook_endpoint_id="whe_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = response.parse()
            assert_matches_type(WebhookEndpointWithSecret, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_rotate_secret(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `webhook_endpoint_id` but received ''"):
            client.webhooks.with_raw_response.rotate_secret(
                webhook_endpoint_id="",
            )

    @parametrize
    def test_method_test(self, client: OpenAI) -> None:
        webhook = client.webhooks.test(
            webhook_endpoint_id="whe_123",
            event_type="batch.completed",
        )
        assert_matches_type(WebhookEndpointTestResult, webhook, path=["response"])

    @parametrize
    def test_raw_response_test(self, client: OpenAI) -> None:
        response = client.webhooks.with_raw_response.test(
            webhook_endpoint_id="whe_123",
            event_type="batch.completed",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = response.parse()
        assert_matches_type(WebhookEndpointTestResult, webhook, path=["response"])

    @parametrize
    def test_streaming_response_test(self, client: OpenAI) -> None:
        with client.webhooks.with_streaming_response.test(
            webhook_endpoint_id="whe_123",
            event_type="batch.completed",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = response.parse()
            assert_matches_type(WebhookEndpointTestResult, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_test(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `webhook_endpoint_id` but received ''"):
            client.webhooks.with_raw_response.test(
                webhook_endpoint_id="",
                event_type="batch.completed",
            )


class TestAsyncWebhooks:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        webhook = await async_client.webhooks.create(
            event_types=["batch.completed"],
            name="x",
            url="https://",
        )
        assert_matches_type(WebhookEndpointWithSecret, webhook, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.webhooks.with_raw_response.create(
            event_types=["batch.completed"],
            name="x",
            url="https://",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = response.parse()
        assert_matches_type(WebhookEndpointWithSecret, webhook, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.webhooks.with_streaming_response.create(
            event_types=["batch.completed"],
            name="x",
            url="https://",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = await response.parse()
            assert_matches_type(WebhookEndpointWithSecret, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        webhook = await async_client.webhooks.retrieve(
            "whe_123",
        )
        assert_matches_type(WebhookEndpoint, webhook, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.webhooks.with_raw_response.retrieve(
            "whe_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = response.parse()
        assert_matches_type(WebhookEndpoint, webhook, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.webhooks.with_streaming_response.retrieve(
            "whe_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = await response.parse()
            assert_matches_type(WebhookEndpoint, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `webhook_endpoint_id` but received ''"):
            await async_client.webhooks.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncOpenAI) -> None:
        webhook = await async_client.webhooks.update(
            webhook_endpoint_id="whe_123",
        )
        assert_matches_type(WebhookEndpoint, webhook, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncOpenAI) -> None:
        webhook = await async_client.webhooks.update(
            webhook_endpoint_id="whe_123",
            event_types=["batch.completed"],
            name="x",
            url="https://",
        )
        assert_matches_type(WebhookEndpoint, webhook, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.webhooks.with_raw_response.update(
            webhook_endpoint_id="whe_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = response.parse()
        assert_matches_type(WebhookEndpoint, webhook, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncOpenAI) -> None:
        async with async_client.webhooks.with_streaming_response.update(
            webhook_endpoint_id="whe_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = await response.parse()
            assert_matches_type(WebhookEndpoint, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `webhook_endpoint_id` but received ''"):
            await async_client.webhooks.with_raw_response.update(
                webhook_endpoint_id="",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        webhook = await async_client.webhooks.list()
        assert_matches_type(AsyncCursorPage[WebhookEndpoint], webhook, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        webhook = await async_client.webhooks.list(
            after="whe_123",
            limit=1,
        )
        assert_matches_type(AsyncCursorPage[WebhookEndpoint], webhook, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.webhooks.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = response.parse()
        assert_matches_type(AsyncCursorPage[WebhookEndpoint], webhook, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.webhooks.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = await response.parse()
            assert_matches_type(AsyncCursorPage[WebhookEndpoint], webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        webhook = await async_client.webhooks.delete(
            "whe_123",
        )
        assert_matches_type(DeletedWebhookEndpoint, webhook, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.webhooks.with_raw_response.delete(
            "whe_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = response.parse()
        assert_matches_type(DeletedWebhookEndpoint, webhook, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.webhooks.with_streaming_response.delete(
            "whe_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = await response.parse()
            assert_matches_type(DeletedWebhookEndpoint, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `webhook_endpoint_id` but received ''"):
            await async_client.webhooks.with_raw_response.delete(
                "",
            )

    @parametrize
    async def test_method_rotate_secret(self, async_client: AsyncOpenAI) -> None:
        webhook = await async_client.webhooks.rotate_secret(
            webhook_endpoint_id="whe_123",
        )
        assert_matches_type(WebhookEndpointWithSecret, webhook, path=["response"])

    @parametrize
    async def test_method_rotate_secret_with_all_params(self, async_client: AsyncOpenAI) -> None:
        webhook = await async_client.webhooks.rotate_secret(
            webhook_endpoint_id="whe_123",
            keep_old_secret_active_for_24_hours=True,
        )
        assert_matches_type(WebhookEndpointWithSecret, webhook, path=["response"])

    @parametrize
    async def test_raw_response_rotate_secret(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.webhooks.with_raw_response.rotate_secret(
            webhook_endpoint_id="whe_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = response.parse()
        assert_matches_type(WebhookEndpointWithSecret, webhook, path=["response"])

    @parametrize
    async def test_streaming_response_rotate_secret(self, async_client: AsyncOpenAI) -> None:
        async with async_client.webhooks.with_streaming_response.rotate_secret(
            webhook_endpoint_id="whe_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = await response.parse()
            assert_matches_type(WebhookEndpointWithSecret, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_rotate_secret(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `webhook_endpoint_id` but received ''"):
            await async_client.webhooks.with_raw_response.rotate_secret(
                webhook_endpoint_id="",
            )

    @parametrize
    async def test_method_test(self, async_client: AsyncOpenAI) -> None:
        webhook = await async_client.webhooks.test(
            webhook_endpoint_id="whe_123",
            event_type="batch.completed",
        )
        assert_matches_type(WebhookEndpointTestResult, webhook, path=["response"])

    @parametrize
    async def test_raw_response_test(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.webhooks.with_raw_response.test(
            webhook_endpoint_id="whe_123",
            event_type="batch.completed",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = response.parse()
        assert_matches_type(WebhookEndpointTestResult, webhook, path=["response"])

    @parametrize
    async def test_streaming_response_test(self, async_client: AsyncOpenAI) -> None:
        async with async_client.webhooks.with_streaming_response.test(
            webhook_endpoint_id="whe_123",
            event_type="batch.completed",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = await response.parse()
            assert_matches_type(WebhookEndpointTestResult, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_test(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `webhook_endpoint_id` but received ''"):
            await async_client.webhooks.with_raw_response.test(
                webhook_endpoint_id="",
                event_type="batch.completed",
            )
