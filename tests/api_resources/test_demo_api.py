# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types import DemoWidget, DemoAPIListResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDemoAPI:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        demo_api = client.demo_api.create(
            configuration={
                "priority": 0,
                "region": "us-east",
            },
            name="name",
        )
        assert_matches_type(DemoWidget, demo_api, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        demo_api = client.demo_api.create(
            configuration={
                "priority": 0,
                "region": "us-east",
                "labels": {"foo": "string"},
            },
            name="name",
            metadata={"foo": "string"},
        )
        assert_matches_type(DemoWidget, demo_api, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.demo_api.with_raw_response.create(
            configuration={
                "priority": 0,
                "region": "us-east",
            },
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        demo_api = response.parse()
        assert_matches_type(DemoWidget, demo_api, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.demo_api.with_streaming_response.create(
            configuration={
                "priority": 0,
                "region": "us-east",
            },
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            demo_api = response.parse()
            assert_matches_type(DemoWidget, demo_api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        demo_api = client.demo_api.retrieve(
            widget_id="widget_id",
        )
        assert_matches_type(DemoWidget, demo_api, path=["response"])

    @parametrize
    def test_method_retrieve_with_all_params(self, client: OpenAI) -> None:
        demo_api = client.demo_api.retrieve(
            widget_id="widget_id",
            include_history=True,
        )
        assert_matches_type(DemoWidget, demo_api, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.demo_api.with_raw_response.retrieve(
            widget_id="widget_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        demo_api = response.parse()
        assert_matches_type(DemoWidget, demo_api, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.demo_api.with_streaming_response.retrieve(
            widget_id="widget_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            demo_api = response.parse()
            assert_matches_type(DemoWidget, demo_api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `widget_id` but received ''"):
            client.demo_api.with_raw_response.retrieve(
                widget_id="",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        demo_api = client.demo_api.list()
        assert_matches_type(DemoAPIListResponse, demo_api, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        demo_api = client.demo_api.list(
            limit=1,
            status="pending",
        )
        assert_matches_type(DemoAPIListResponse, demo_api, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.demo_api.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        demo_api = response.parse()
        assert_matches_type(DemoAPIListResponse, demo_api, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.demo_api.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            demo_api = response.parse()
            assert_matches_type(DemoAPIListResponse, demo_api, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDemoAPI:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        demo_api = await async_client.demo_api.create(
            configuration={
                "priority": 0,
                "region": "us-east",
            },
            name="name",
        )
        assert_matches_type(DemoWidget, demo_api, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        demo_api = await async_client.demo_api.create(
            configuration={
                "priority": 0,
                "region": "us-east",
                "labels": {"foo": "string"},
            },
            name="name",
            metadata={"foo": "string"},
        )
        assert_matches_type(DemoWidget, demo_api, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.demo_api.with_raw_response.create(
            configuration={
                "priority": 0,
                "region": "us-east",
            },
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        demo_api = response.parse()
        assert_matches_type(DemoWidget, demo_api, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.demo_api.with_streaming_response.create(
            configuration={
                "priority": 0,
                "region": "us-east",
            },
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            demo_api = await response.parse()
            assert_matches_type(DemoWidget, demo_api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        demo_api = await async_client.demo_api.retrieve(
            widget_id="widget_id",
        )
        assert_matches_type(DemoWidget, demo_api, path=["response"])

    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncOpenAI) -> None:
        demo_api = await async_client.demo_api.retrieve(
            widget_id="widget_id",
            include_history=True,
        )
        assert_matches_type(DemoWidget, demo_api, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.demo_api.with_raw_response.retrieve(
            widget_id="widget_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        demo_api = response.parse()
        assert_matches_type(DemoWidget, demo_api, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.demo_api.with_streaming_response.retrieve(
            widget_id="widget_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            demo_api = await response.parse()
            assert_matches_type(DemoWidget, demo_api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `widget_id` but received ''"):
            await async_client.demo_api.with_raw_response.retrieve(
                widget_id="",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        demo_api = await async_client.demo_api.list()
        assert_matches_type(DemoAPIListResponse, demo_api, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        demo_api = await async_client.demo_api.list(
            limit=1,
            status="pending",
        )
        assert_matches_type(DemoAPIListResponse, demo_api, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.demo_api.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        demo_api = response.parse()
        assert_matches_type(DemoAPIListResponse, demo_api, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.demo_api.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            demo_api = await response.parse()
            assert_matches_type(DemoAPIListResponse, demo_api, path=["response"])

        assert cast(Any, response.is_closed) is True
