# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai._client import OpenAI, AsyncOpenAI
from openai.types.beta import (
    Thread,
    ThreadDeleted,
)
from openai.types.beta.threads import Run

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
api_key = "My API Key"


class TestThreads:
    strict_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        thread = client.beta.threads.create()
        assert_matches_type(Thread, thread, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": "x",
                    "file_ids": ["string"],
                    "metadata": {},
                },
                {
                    "role": "user",
                    "content": "x",
                    "file_ids": ["string"],
                    "metadata": {},
                },
                {
                    "role": "user",
                    "content": "x",
                    "file_ids": ["string"],
                    "metadata": {},
                },
            ],
            metadata={},
        )
        assert_matches_type(Thread, thread, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.beta.threads.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        thread = response.parse()
        assert_matches_type(Thread, thread, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.beta.threads.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            thread = response.parse()
            assert_matches_type(Thread, thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        thread = client.beta.threads.retrieve(
            "string",
        )
        assert_matches_type(Thread, thread, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.beta.threads.with_raw_response.retrieve(
            "string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        thread = response.parse()
        assert_matches_type(Thread, thread, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.beta.threads.with_streaming_response.retrieve(
            "string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            thread = response.parse()
            assert_matches_type(Thread, thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.beta.threads.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_update(self, client: OpenAI) -> None:
        thread = client.beta.threads.update(
            "string",
        )
        assert_matches_type(Thread, thread, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: OpenAI) -> None:
        thread = client.beta.threads.update(
            "string",
            metadata={},
        )
        assert_matches_type(Thread, thread, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: OpenAI) -> None:
        response = client.beta.threads.with_raw_response.update(
            "string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        thread = response.parse()
        assert_matches_type(Thread, thread, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: OpenAI) -> None:
        with client.beta.threads.with_streaming_response.update(
            "string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            thread = response.parse()
            assert_matches_type(Thread, thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.beta.threads.with_raw_response.update(
                "",
            )

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        thread = client.beta.threads.delete(
            "string",
        )
        assert_matches_type(ThreadDeleted, thread, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.beta.threads.with_raw_response.delete(
            "string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        thread = response.parse()
        assert_matches_type(ThreadDeleted, thread, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.beta.threads.with_streaming_response.delete(
            "string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            thread = response.parse()
            assert_matches_type(ThreadDeleted, thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.beta.threads.with_raw_response.delete(
                "",
            )

    @parametrize
    def test_method_create_and_run(self, client: OpenAI) -> None:
        thread = client.beta.threads.create_and_run(
            assistant_id="string",
        )
        assert_matches_type(Run, thread, path=["response"])

    @parametrize
    def test_method_create_and_run_with_all_params(self, client: OpenAI) -> None:
        thread = client.beta.threads.create_and_run(
            assistant_id="string",
            instructions="string",
            metadata={},
            model="string",
            thread={
                "messages": [
                    {
                        "role": "user",
                        "content": "x",
                        "file_ids": ["string"],
                        "metadata": {},
                    },
                    {
                        "role": "user",
                        "content": "x",
                        "file_ids": ["string"],
                        "metadata": {},
                    },
                    {
                        "role": "user",
                        "content": "x",
                        "file_ids": ["string"],
                        "metadata": {},
                    },
                ],
                "metadata": {},
            },
            tools=[{"type": "code_interpreter"}, {"type": "code_interpreter"}, {"type": "code_interpreter"}],
        )
        assert_matches_type(Run, thread, path=["response"])

    @parametrize
    def test_raw_response_create_and_run(self, client: OpenAI) -> None:
        response = client.beta.threads.with_raw_response.create_and_run(
            assistant_id="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        thread = response.parse()
        assert_matches_type(Run, thread, path=["response"])

    @parametrize
    def test_streaming_response_create_and_run(self, client: OpenAI) -> None:
        with client.beta.threads.with_streaming_response.create_and_run(
            assistant_id="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            thread = response.parse()
            assert_matches_type(Run, thread, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncThreads:
    strict_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    async def test_method_create(self, client: AsyncOpenAI) -> None:
        thread = await client.beta.threads.create()
        assert_matches_type(Thread, thread, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, client: AsyncOpenAI) -> None:
        thread = await client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": "x",
                    "file_ids": ["string"],
                    "metadata": {},
                },
                {
                    "role": "user",
                    "content": "x",
                    "file_ids": ["string"],
                    "metadata": {},
                },
                {
                    "role": "user",
                    "content": "x",
                    "file_ids": ["string"],
                    "metadata": {},
                },
            ],
            metadata={},
        )
        assert_matches_type(Thread, thread, path=["response"])

    @parametrize
    async def test_raw_response_create(self, client: AsyncOpenAI) -> None:
        response = await client.beta.threads.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        thread = response.parse()
        assert_matches_type(Thread, thread, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, client: AsyncOpenAI) -> None:
        async with client.beta.threads.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            thread = await response.parse()
            assert_matches_type(Thread, thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, client: AsyncOpenAI) -> None:
        thread = await client.beta.threads.retrieve(
            "string",
        )
        assert_matches_type(Thread, thread, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, client: AsyncOpenAI) -> None:
        response = await client.beta.threads.with_raw_response.retrieve(
            "string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        thread = response.parse()
        assert_matches_type(Thread, thread, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, client: AsyncOpenAI) -> None:
        async with client.beta.threads.with_streaming_response.retrieve(
            "string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            thread = await response.parse()
            assert_matches_type(Thread, thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await client.beta.threads.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_update(self, client: AsyncOpenAI) -> None:
        thread = await client.beta.threads.update(
            "string",
        )
        assert_matches_type(Thread, thread, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, client: AsyncOpenAI) -> None:
        thread = await client.beta.threads.update(
            "string",
            metadata={},
        )
        assert_matches_type(Thread, thread, path=["response"])

    @parametrize
    async def test_raw_response_update(self, client: AsyncOpenAI) -> None:
        response = await client.beta.threads.with_raw_response.update(
            "string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        thread = response.parse()
        assert_matches_type(Thread, thread, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, client: AsyncOpenAI) -> None:
        async with client.beta.threads.with_streaming_response.update(
            "string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            thread = await response.parse()
            assert_matches_type(Thread, thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await client.beta.threads.with_raw_response.update(
                "",
            )

    @parametrize
    async def test_method_delete(self, client: AsyncOpenAI) -> None:
        thread = await client.beta.threads.delete(
            "string",
        )
        assert_matches_type(ThreadDeleted, thread, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, client: AsyncOpenAI) -> None:
        response = await client.beta.threads.with_raw_response.delete(
            "string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        thread = response.parse()
        assert_matches_type(ThreadDeleted, thread, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, client: AsyncOpenAI) -> None:
        async with client.beta.threads.with_streaming_response.delete(
            "string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            thread = await response.parse()
            assert_matches_type(ThreadDeleted, thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await client.beta.threads.with_raw_response.delete(
                "",
            )

    @parametrize
    async def test_method_create_and_run(self, client: AsyncOpenAI) -> None:
        thread = await client.beta.threads.create_and_run(
            assistant_id="string",
        )
        assert_matches_type(Run, thread, path=["response"])

    @parametrize
    async def test_method_create_and_run_with_all_params(self, client: AsyncOpenAI) -> None:
        thread = await client.beta.threads.create_and_run(
            assistant_id="string",
            instructions="string",
            metadata={},
            model="string",
            thread={
                "messages": [
                    {
                        "role": "user",
                        "content": "x",
                        "file_ids": ["string"],
                        "metadata": {},
                    },
                    {
                        "role": "user",
                        "content": "x",
                        "file_ids": ["string"],
                        "metadata": {},
                    },
                    {
                        "role": "user",
                        "content": "x",
                        "file_ids": ["string"],
                        "metadata": {},
                    },
                ],
                "metadata": {},
            },
            tools=[{"type": "code_interpreter"}, {"type": "code_interpreter"}, {"type": "code_interpreter"}],
        )
        assert_matches_type(Run, thread, path=["response"])

    @parametrize
    async def test_raw_response_create_and_run(self, client: AsyncOpenAI) -> None:
        response = await client.beta.threads.with_raw_response.create_and_run(
            assistant_id="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        thread = response.parse()
        assert_matches_type(Run, thread, path=["response"])

    @parametrize
    async def test_streaming_response_create_and_run(self, client: AsyncOpenAI) -> None:
        async with client.beta.threads.with_streaming_response.create_and_run(
            assistant_id="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            thread = await response.parse()
            assert_matches_type(Run, thread, path=["response"])

        assert cast(Any, response.is_closed) is True
