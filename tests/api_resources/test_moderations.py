# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

import os

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types import ModerationCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
api_key = os.environ.get("API_KEY", "something1234")


class TestModerations:
    strict_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

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


class TestAsyncModerations:
    strict_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    async def test_method_create(self, client: AsyncOpenAI) -> None:
        moderation = await client.moderations.create(
            input="I want to kill them.",
        )
        assert_matches_type(ModerationCreateResponse, moderation, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, client: AsyncOpenAI) -> None:
        moderation = await client.moderations.create(
            input="I want to kill them.",
            model="text-moderation-stable",
        )
        assert_matches_type(ModerationCreateResponse, moderation, path=["response"])
