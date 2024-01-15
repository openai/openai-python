# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai._client import OpenAI, AsyncOpenAI
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.beta.threads.runs import RunStep

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
api_key = "My API Key"


class TestSteps:
    strict_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        step = client.beta.threads.runs.steps.retrieve(
            "string",
            thread_id="string",
            run_id="string",
        )
        assert_matches_type(RunStep, step, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.beta.threads.runs.steps.with_raw_response.retrieve(
            "string",
            thread_id="string",
            run_id="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        step = response.parse()
        assert_matches_type(RunStep, step, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.beta.threads.runs.steps.with_streaming_response.retrieve(
            "string",
            thread_id="string",
            run_id="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            step = response.parse()
            assert_matches_type(RunStep, step, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        step = client.beta.threads.runs.steps.list(
            "string",
            thread_id="string",
        )
        assert_matches_type(SyncCursorPage[RunStep], step, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        step = client.beta.threads.runs.steps.list(
            "string",
            thread_id="string",
            after="string",
            before="string",
            limit=0,
            order="asc",
        )
        assert_matches_type(SyncCursorPage[RunStep], step, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.beta.threads.runs.steps.with_raw_response.list(
            "string",
            thread_id="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        step = response.parse()
        assert_matches_type(SyncCursorPage[RunStep], step, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.beta.threads.runs.steps.with_streaming_response.list(
            "string",
            thread_id="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            step = response.parse()
            assert_matches_type(SyncCursorPage[RunStep], step, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSteps:
    strict_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    async def test_method_retrieve(self, client: AsyncOpenAI) -> None:
        step = await client.beta.threads.runs.steps.retrieve(
            "string",
            thread_id="string",
            run_id="string",
        )
        assert_matches_type(RunStep, step, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, client: AsyncOpenAI) -> None:
        response = await client.beta.threads.runs.steps.with_raw_response.retrieve(
            "string",
            thread_id="string",
            run_id="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        step = response.parse()
        assert_matches_type(RunStep, step, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, client: AsyncOpenAI) -> None:
        async with client.beta.threads.runs.steps.with_streaming_response.retrieve(
            "string",
            thread_id="string",
            run_id="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            step = await response.parse()
            assert_matches_type(RunStep, step, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list(self, client: AsyncOpenAI) -> None:
        step = await client.beta.threads.runs.steps.list(
            "string",
            thread_id="string",
        )
        assert_matches_type(AsyncCursorPage[RunStep], step, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, client: AsyncOpenAI) -> None:
        step = await client.beta.threads.runs.steps.list(
            "string",
            thread_id="string",
            after="string",
            before="string",
            limit=0,
            order="asc",
        )
        assert_matches_type(AsyncCursorPage[RunStep], step, path=["response"])

    @parametrize
    async def test_raw_response_list(self, client: AsyncOpenAI) -> None:
        response = await client.beta.threads.runs.steps.with_raw_response.list(
            "string",
            thread_id="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        step = response.parse()
        assert_matches_type(AsyncCursorPage[RunStep], step, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, client: AsyncOpenAI) -> None:
        async with client.beta.threads.runs.steps.with_streaming_response.list(
            "string",
            thread_id="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            step = await response.parse()
            assert_matches_type(AsyncCursorPage[RunStep], step, path=["response"])

        assert cast(Any, response.is_closed) is True
