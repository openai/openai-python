# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types import Decision

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDecisions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        decision = client.decisions.create(
            input="string",
            model="model",
            questions=[
                {
                    "instructions": "instructions",
                    "type": "predicate",
                }
            ],
        )
        assert_matches_type(Decision, decision, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        decision = client.decisions.create(
            input="string",
            model="model",
            questions=[
                {
                    "instructions": "instructions",
                    "type": "predicate",
                    "name": "name",
                }
            ],
            safety_identifier="safety_identifier",
        )
        assert_matches_type(Decision, decision, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.decisions.with_raw_response.create(
            input="string",
            model="model",
            questions=[
                {
                    "instructions": "instructions",
                    "type": "predicate",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        decision = response.parse()
        assert_matches_type(Decision, decision, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.decisions.with_streaming_response.create(
            input="string",
            model="model",
            questions=[
                {
                    "instructions": "instructions",
                    "type": "predicate",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            decision = response.parse()
            assert_matches_type(Decision, decision, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDecisions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        decision = await async_client.decisions.create(
            input="string",
            model="model",
            questions=[
                {
                    "instructions": "instructions",
                    "type": "predicate",
                }
            ],
        )
        assert_matches_type(Decision, decision, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        decision = await async_client.decisions.create(
            input="string",
            model="model",
            questions=[
                {
                    "instructions": "instructions",
                    "type": "predicate",
                    "name": "name",
                }
            ],
            safety_identifier="safety_identifier",
        )
        assert_matches_type(Decision, decision, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.decisions.with_raw_response.create(
            input="string",
            model="model",
            questions=[
                {
                    "instructions": "instructions",
                    "type": "predicate",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        decision = response.parse()
        assert_matches_type(Decision, decision, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.decisions.with_streaming_response.create(
            input="string",
            model="model",
            questions=[
                {
                    "instructions": "instructions",
                    "type": "predicate",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            decision = await response.parse()
            assert_matches_type(Decision, decision, path=["response"])

        assert cast(Any, response.is_closed) is True
