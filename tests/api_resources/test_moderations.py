# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types import ModerationCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestModerations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        moderation = client.moderations.create(
            input="I want to kill them.",
        )
        assert_matches_type(ModerationCreateResponse, moderation, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        moderation = client.moderations.create(
            input="I want to kill them.",
            model="text-moderation-stable",
        )
        assert_matches_type(ModerationCreateResponse, moderation, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.moderations.with_raw_response.create(
            input="I want to kill them.",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        moderation = response.parse()
        assert_matches_type(ModerationCreateResponse, moderation, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.moderations.with_streaming_response.create(
            input="I want to kill them.",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            moderation = response.parse()
            assert_matches_type(ModerationCreateResponse, moderation, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncModerations:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        moderation = await async_client.moderations.create(
            input="I want to kill them.",
        )
        assert_matches_type(ModerationCreateResponse, moderation, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        moderation = await async_client.moderations.create(
            input="I want to kill them.",
            model="text-moderation-stable",
        )
        assert_matches_type(ModerationCreateResponse, moderation, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.moderations.with_raw_response.create(
            input="I want to kill them.",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        moderation = response.parse()
        assert_matches_type(ModerationCreateResponse, moderation, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.moderations.with_streaming_response.create(
            input="I want to kill them.",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            moderation = await response.parse()
            assert_matches_type(ModerationCreateResponse, moderation, path=["response"])

        assert cast(Any, response.is_closed) is True
