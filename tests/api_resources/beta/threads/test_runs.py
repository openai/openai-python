# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

import os

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai._client import OpenAI, AsyncOpenAI
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.beta.threads import (
    Run,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
api_key = "My API Key"


class TestRuns:
    strict_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        run = client.beta.threads.runs.create(
            "string",
            assistant_id="string",
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        run = client.beta.threads.runs.create(
            "string",
            assistant_id="string",
            additional_instructions="string",
            instructions="string",
            metadata={},
            model="string",
            tools=[{"type": "code_interpreter"}, {"type": "code_interpreter"}, {"type": "code_interpreter"}],
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.beta.threads.runs.with_raw_response.create(
            "string",
            assistant_id="string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        run = client.beta.threads.runs.retrieve(
            "string",
            thread_id="string",
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.beta.threads.runs.with_raw_response.retrieve(
            "string",
            thread_id="string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    def test_method_update(self, client: OpenAI) -> None:
        run = client.beta.threads.runs.update(
            "string",
            thread_id="string",
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: OpenAI) -> None:
        run = client.beta.threads.runs.update(
            "string",
            thread_id="string",
            metadata={},
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: OpenAI) -> None:
        response = client.beta.threads.runs.with_raw_response.update(
            "string",
            thread_id="string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        run = client.beta.threads.runs.list(
            "string",
        )
        assert_matches_type(SyncCursorPage[Run], run, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        run = client.beta.threads.runs.list(
            "string",
            after="string",
            before="string",
            limit=0,
            order="asc",
        )
        assert_matches_type(SyncCursorPage[Run], run, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.beta.threads.runs.with_raw_response.list(
            "string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(SyncCursorPage[Run], run, path=["response"])

    @parametrize
    def test_method_cancel(self, client: OpenAI) -> None:
        run = client.beta.threads.runs.cancel(
            "string",
            thread_id="string",
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    def test_raw_response_cancel(self, client: OpenAI) -> None:
        response = client.beta.threads.runs.with_raw_response.cancel(
            "string",
            thread_id="string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    def test_method_submit_tool_outputs(self, client: OpenAI) -> None:
        run = client.beta.threads.runs.submit_tool_outputs(
            "string",
            thread_id="string",
            tool_outputs=[{}, {}, {}],
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    def test_raw_response_submit_tool_outputs(self, client: OpenAI) -> None:
        response = client.beta.threads.runs.with_raw_response.submit_tool_outputs(
            "string",
            thread_id="string",
            tool_outputs=[{}, {}, {}],
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(Run, run, path=["response"])


class TestAsyncRuns:
    strict_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    async def test_method_create(self, client: AsyncOpenAI) -> None:
        run = await client.beta.threads.runs.create(
            "string",
            assistant_id="string",
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, client: AsyncOpenAI) -> None:
        run = await client.beta.threads.runs.create(
            "string",
            assistant_id="string",
            additional_instructions="string",
            instructions="string",
            metadata={},
            model="string",
            tools=[{"type": "code_interpreter"}, {"type": "code_interpreter"}, {"type": "code_interpreter"}],
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_raw_response_create(self, client: AsyncOpenAI) -> None:
        response = await client.beta.threads.runs.with_raw_response.create(
            "string",
            assistant_id="string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_method_retrieve(self, client: AsyncOpenAI) -> None:
        run = await client.beta.threads.runs.retrieve(
            "string",
            thread_id="string",
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, client: AsyncOpenAI) -> None:
        response = await client.beta.threads.runs.with_raw_response.retrieve(
            "string",
            thread_id="string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_method_update(self, client: AsyncOpenAI) -> None:
        run = await client.beta.threads.runs.update(
            "string",
            thread_id="string",
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, client: AsyncOpenAI) -> None:
        run = await client.beta.threads.runs.update(
            "string",
            thread_id="string",
            metadata={},
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_raw_response_update(self, client: AsyncOpenAI) -> None:
        response = await client.beta.threads.runs.with_raw_response.update(
            "string",
            thread_id="string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_method_list(self, client: AsyncOpenAI) -> None:
        run = await client.beta.threads.runs.list(
            "string",
        )
        assert_matches_type(AsyncCursorPage[Run], run, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, client: AsyncOpenAI) -> None:
        run = await client.beta.threads.runs.list(
            "string",
            after="string",
            before="string",
            limit=0,
            order="asc",
        )
        assert_matches_type(AsyncCursorPage[Run], run, path=["response"])

    @parametrize
    async def test_raw_response_list(self, client: AsyncOpenAI) -> None:
        response = await client.beta.threads.runs.with_raw_response.list(
            "string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(AsyncCursorPage[Run], run, path=["response"])

    @parametrize
    async def test_method_cancel(self, client: AsyncOpenAI) -> None:
        run = await client.beta.threads.runs.cancel(
            "string",
            thread_id="string",
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_raw_response_cancel(self, client: AsyncOpenAI) -> None:
        response = await client.beta.threads.runs.with_raw_response.cancel(
            "string",
            thread_id="string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_method_submit_tool_outputs(self, client: AsyncOpenAI) -> None:
        run = await client.beta.threads.runs.submit_tool_outputs(
            "string",
            thread_id="string",
            tool_outputs=[{}, {}, {}],
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_raw_response_submit_tool_outputs(self, client: AsyncOpenAI) -> None:
        response = await client.beta.threads.runs.with_raw_response.submit_tool_outputs(
            "string",
            thread_id="string",
            tool_outputs=[{}, {}, {}],
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(Run, run, path=["response"])
