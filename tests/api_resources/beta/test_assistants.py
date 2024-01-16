# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai._client import OpenAI, AsyncOpenAI
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.beta import (
    Assistant,
    AssistantDeleted,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
api_key = "My API Key"


class TestAssistants:
    strict_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        assistant = client.beta.assistants.create(
            model="string",
        )
        assert_matches_type(Assistant, assistant, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        assistant = client.beta.assistants.create(
            model="string",
            description="string",
            file_ids=["string", "string", "string"],
            instructions="string",
            metadata={},
            name="string",
            tools=[{"type": "code_interpreter"}, {"type": "code_interpreter"}, {"type": "code_interpreter"}],
        )
        assert_matches_type(Assistant, assistant, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.beta.assistants.with_raw_response.create(
            model="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assistant = response.parse()
        assert_matches_type(Assistant, assistant, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.beta.assistants.with_streaming_response.create(
            model="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assistant = response.parse()
            assert_matches_type(Assistant, assistant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        assistant = client.beta.assistants.retrieve(
            "string",
        )
        assert_matches_type(Assistant, assistant, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.beta.assistants.with_raw_response.retrieve(
            "string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assistant = response.parse()
        assert_matches_type(Assistant, assistant, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.beta.assistants.with_streaming_response.retrieve(
            "string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assistant = response.parse()
            assert_matches_type(Assistant, assistant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `assistant_id` but received ''"):
            client.beta.assistants.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_update(self, client: OpenAI) -> None:
        assistant = client.beta.assistants.update(
            "string",
        )
        assert_matches_type(Assistant, assistant, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: OpenAI) -> None:
        assistant = client.beta.assistants.update(
            "string",
            description="string",
            file_ids=["string", "string", "string"],
            instructions="string",
            metadata={},
            model="string",
            name="string",
            tools=[{"type": "code_interpreter"}, {"type": "code_interpreter"}, {"type": "code_interpreter"}],
        )
        assert_matches_type(Assistant, assistant, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: OpenAI) -> None:
        response = client.beta.assistants.with_raw_response.update(
            "string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assistant = response.parse()
        assert_matches_type(Assistant, assistant, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: OpenAI) -> None:
        with client.beta.assistants.with_streaming_response.update(
            "string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assistant = response.parse()
            assert_matches_type(Assistant, assistant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `assistant_id` but received ''"):
            client.beta.assistants.with_raw_response.update(
                "",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        assistant = client.beta.assistants.list()
        assert_matches_type(SyncCursorPage[Assistant], assistant, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        assistant = client.beta.assistants.list(
            after="string",
            before="string",
            limit=0,
            order="asc",
        )
        assert_matches_type(SyncCursorPage[Assistant], assistant, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.beta.assistants.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assistant = response.parse()
        assert_matches_type(SyncCursorPage[Assistant], assistant, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.beta.assistants.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assistant = response.parse()
            assert_matches_type(SyncCursorPage[Assistant], assistant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        assistant = client.beta.assistants.delete(
            "string",
        )
        assert_matches_type(AssistantDeleted, assistant, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.beta.assistants.with_raw_response.delete(
            "string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assistant = response.parse()
        assert_matches_type(AssistantDeleted, assistant, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.beta.assistants.with_streaming_response.delete(
            "string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assistant = response.parse()
            assert_matches_type(AssistantDeleted, assistant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `assistant_id` but received ''"):
            client.beta.assistants.with_raw_response.delete(
                "",
            )


class TestAsyncAssistants:
    strict_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    async def test_method_create(self, client: AsyncOpenAI) -> None:
        assistant = await client.beta.assistants.create(
            model="string",
        )
        assert_matches_type(Assistant, assistant, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, client: AsyncOpenAI) -> None:
        assistant = await client.beta.assistants.create(
            model="string",
            description="string",
            file_ids=["string", "string", "string"],
            instructions="string",
            metadata={},
            name="string",
            tools=[{"type": "code_interpreter"}, {"type": "code_interpreter"}, {"type": "code_interpreter"}],
        )
        assert_matches_type(Assistant, assistant, path=["response"])

    @parametrize
    async def test_raw_response_create(self, client: AsyncOpenAI) -> None:
        response = await client.beta.assistants.with_raw_response.create(
            model="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assistant = response.parse()
        assert_matches_type(Assistant, assistant, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, client: AsyncOpenAI) -> None:
        async with client.beta.assistants.with_streaming_response.create(
            model="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assistant = await response.parse()
            assert_matches_type(Assistant, assistant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, client: AsyncOpenAI) -> None:
        assistant = await client.beta.assistants.retrieve(
            "string",
        )
        assert_matches_type(Assistant, assistant, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, client: AsyncOpenAI) -> None:
        response = await client.beta.assistants.with_raw_response.retrieve(
            "string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assistant = response.parse()
        assert_matches_type(Assistant, assistant, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, client: AsyncOpenAI) -> None:
        async with client.beta.assistants.with_streaming_response.retrieve(
            "string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assistant = await response.parse()
            assert_matches_type(Assistant, assistant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `assistant_id` but received ''"):
            await client.beta.assistants.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_update(self, client: AsyncOpenAI) -> None:
        assistant = await client.beta.assistants.update(
            "string",
        )
        assert_matches_type(Assistant, assistant, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, client: AsyncOpenAI) -> None:
        assistant = await client.beta.assistants.update(
            "string",
            description="string",
            file_ids=["string", "string", "string"],
            instructions="string",
            metadata={},
            model="string",
            name="string",
            tools=[{"type": "code_interpreter"}, {"type": "code_interpreter"}, {"type": "code_interpreter"}],
        )
        assert_matches_type(Assistant, assistant, path=["response"])

    @parametrize
    async def test_raw_response_update(self, client: AsyncOpenAI) -> None:
        response = await client.beta.assistants.with_raw_response.update(
            "string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assistant = response.parse()
        assert_matches_type(Assistant, assistant, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, client: AsyncOpenAI) -> None:
        async with client.beta.assistants.with_streaming_response.update(
            "string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assistant = await response.parse()
            assert_matches_type(Assistant, assistant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `assistant_id` but received ''"):
            await client.beta.assistants.with_raw_response.update(
                "",
            )

    @parametrize
    async def test_method_list(self, client: AsyncOpenAI) -> None:
        assistant = await client.beta.assistants.list()
        assert_matches_type(AsyncCursorPage[Assistant], assistant, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, client: AsyncOpenAI) -> None:
        assistant = await client.beta.assistants.list(
            after="string",
            before="string",
            limit=0,
            order="asc",
        )
        assert_matches_type(AsyncCursorPage[Assistant], assistant, path=["response"])

    @parametrize
    async def test_raw_response_list(self, client: AsyncOpenAI) -> None:
        response = await client.beta.assistants.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assistant = response.parse()
        assert_matches_type(AsyncCursorPage[Assistant], assistant, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, client: AsyncOpenAI) -> None:
        async with client.beta.assistants.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assistant = await response.parse()
            assert_matches_type(AsyncCursorPage[Assistant], assistant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, client: AsyncOpenAI) -> None:
        assistant = await client.beta.assistants.delete(
            "string",
        )
        assert_matches_type(AssistantDeleted, assistant, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, client: AsyncOpenAI) -> None:
        response = await client.beta.assistants.with_raw_response.delete(
            "string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        assistant = response.parse()
        assert_matches_type(AssistantDeleted, assistant, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, client: AsyncOpenAI) -> None:
        async with client.beta.assistants.with_streaming_response.delete(
            "string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            assistant = await response.parse()
            assert_matches_type(AssistantDeleted, assistant, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `assistant_id` but received ''"):
            await client.beta.assistants.with_raw_response.delete(
                "",
            )
