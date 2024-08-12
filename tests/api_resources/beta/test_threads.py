# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types.beta import (
    Thread,
    ThreadDeleted,
)
from openai.types.beta.threads import Run

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestThreads:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        thread = client.beta.threads.create()
        assert_matches_type(Thread, thread, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        thread = client.beta.threads.create(
            messages=[
                {
                    "content": "string",
                    "role": "user",
                    "attachments": [
                        {
                            "file_id": "string",
                            "tools": [
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                            ],
                        },
                        {
                            "file_id": "string",
                            "tools": [
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                            ],
                        },
                        {
                            "file_id": "string",
                            "tools": [
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                            ],
                        },
                    ],
                    "metadata": {},
                },
                {
                    "content": "string",
                    "role": "user",
                    "attachments": [
                        {
                            "file_id": "string",
                            "tools": [
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                            ],
                        },
                        {
                            "file_id": "string",
                            "tools": [
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                            ],
                        },
                        {
                            "file_id": "string",
                            "tools": [
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                            ],
                        },
                    ],
                    "metadata": {},
                },
                {
                    "content": "string",
                    "role": "user",
                    "attachments": [
                        {
                            "file_id": "string",
                            "tools": [
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                            ],
                        },
                        {
                            "file_id": "string",
                            "tools": [
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                            ],
                        },
                        {
                            "file_id": "string",
                            "tools": [
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                            ],
                        },
                    ],
                    "metadata": {},
                },
            ],
            metadata={},
            tool_resources={
                "code_interpreter": {"file_ids": ["string", "string", "string"]},
                "file_search": {
                    "vector_store_ids": ["string"],
                    "vector_stores": [
                        {
                            "chunking_strategy": {"type": "auto"},
                            "file_ids": ["string", "string", "string"],
                            "metadata": {},
                        }
                    ],
                },
            },
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
            tool_resources={
                "code_interpreter": {"file_ids": ["string", "string", "string"]},
                "file_search": {"vector_store_ids": ["string"]},
            },
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
    def test_method_create_and_run_overload_1(self, client: OpenAI) -> None:
        thread = client.beta.threads.create_and_run(
            assistant_id="string",
        )
        assert_matches_type(Run, thread, path=["response"])

    @parametrize
    def test_method_create_and_run_with_all_params_overload_1(self, client: OpenAI) -> None:
        thread = client.beta.threads.create_and_run(
            assistant_id="string",
            instructions="string",
            max_completion_tokens=256,
            max_prompt_tokens=256,
            metadata={},
            model="gpt-4o",
            parallel_tool_calls=True,
            response_format="auto",
            stream=False,
            temperature=1,
            thread={
                "messages": [
                    {
                        "content": "string",
                        "role": "user",
                        "attachments": [
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                        ],
                        "metadata": {},
                    },
                    {
                        "content": "string",
                        "role": "user",
                        "attachments": [
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                        ],
                        "metadata": {},
                    },
                    {
                        "content": "string",
                        "role": "user",
                        "attachments": [
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                        ],
                        "metadata": {},
                    },
                ],
                "metadata": {},
                "tool_resources": {
                    "code_interpreter": {"file_ids": ["string", "string", "string"]},
                    "file_search": {
                        "vector_store_ids": ["string"],
                        "vector_stores": [
                            {
                                "chunking_strategy": {"type": "auto"},
                                "file_ids": ["string", "string", "string"],
                                "metadata": {},
                            }
                        ],
                    },
                },
            },
            tool_choice="none",
            tool_resources={
                "code_interpreter": {"file_ids": ["string", "string", "string"]},
                "file_search": {"vector_store_ids": ["string"]},
            },
            tools=[{"type": "code_interpreter"}, {"type": "code_interpreter"}, {"type": "code_interpreter"}],
            top_p=1,
            truncation_strategy={
                "type": "auto",
                "last_messages": 1,
            },
        )
        assert_matches_type(Run, thread, path=["response"])

    @parametrize
    def test_raw_response_create_and_run_overload_1(self, client: OpenAI) -> None:
        response = client.beta.threads.with_raw_response.create_and_run(
            assistant_id="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        thread = response.parse()
        assert_matches_type(Run, thread, path=["response"])

    @parametrize
    def test_streaming_response_create_and_run_overload_1(self, client: OpenAI) -> None:
        with client.beta.threads.with_streaming_response.create_and_run(
            assistant_id="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            thread = response.parse()
            assert_matches_type(Run, thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_create_and_run_overload_2(self, client: OpenAI) -> None:
        thread_stream = client.beta.threads.create_and_run(
            assistant_id="string",
            stream=True,
        )
        thread_stream.response.close()

    @parametrize
    def test_method_create_and_run_with_all_params_overload_2(self, client: OpenAI) -> None:
        thread_stream = client.beta.threads.create_and_run(
            assistant_id="string",
            stream=True,
            instructions="string",
            max_completion_tokens=256,
            max_prompt_tokens=256,
            metadata={},
            model="gpt-4o",
            parallel_tool_calls=True,
            response_format="auto",
            temperature=1,
            thread={
                "messages": [
                    {
                        "content": "string",
                        "role": "user",
                        "attachments": [
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                        ],
                        "metadata": {},
                    },
                    {
                        "content": "string",
                        "role": "user",
                        "attachments": [
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                        ],
                        "metadata": {},
                    },
                    {
                        "content": "string",
                        "role": "user",
                        "attachments": [
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                        ],
                        "metadata": {},
                    },
                ],
                "metadata": {},
                "tool_resources": {
                    "code_interpreter": {"file_ids": ["string", "string", "string"]},
                    "file_search": {
                        "vector_store_ids": ["string"],
                        "vector_stores": [
                            {
                                "chunking_strategy": {"type": "auto"},
                                "file_ids": ["string", "string", "string"],
                                "metadata": {},
                            }
                        ],
                    },
                },
            },
            tool_choice="none",
            tool_resources={
                "code_interpreter": {"file_ids": ["string", "string", "string"]},
                "file_search": {"vector_store_ids": ["string"]},
            },
            tools=[{"type": "code_interpreter"}, {"type": "code_interpreter"}, {"type": "code_interpreter"}],
            top_p=1,
            truncation_strategy={
                "type": "auto",
                "last_messages": 1,
            },
        )
        thread_stream.response.close()

    @parametrize
    def test_raw_response_create_and_run_overload_2(self, client: OpenAI) -> None:
        response = client.beta.threads.with_raw_response.create_and_run(
            assistant_id="string",
            stream=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        stream.close()

    @parametrize
    def test_streaming_response_create_and_run_overload_2(self, client: OpenAI) -> None:
        with client.beta.threads.with_streaming_response.create_and_run(
            assistant_id="string",
            stream=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = response.parse()
            stream.close()

        assert cast(Any, response.is_closed) is True


class TestAsyncThreads:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        thread = await async_client.beta.threads.create()
        assert_matches_type(Thread, thread, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        thread = await async_client.beta.threads.create(
            messages=[
                {
                    "content": "string",
                    "role": "user",
                    "attachments": [
                        {
                            "file_id": "string",
                            "tools": [
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                            ],
                        },
                        {
                            "file_id": "string",
                            "tools": [
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                            ],
                        },
                        {
                            "file_id": "string",
                            "tools": [
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                            ],
                        },
                    ],
                    "metadata": {},
                },
                {
                    "content": "string",
                    "role": "user",
                    "attachments": [
                        {
                            "file_id": "string",
                            "tools": [
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                            ],
                        },
                        {
                            "file_id": "string",
                            "tools": [
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                            ],
                        },
                        {
                            "file_id": "string",
                            "tools": [
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                            ],
                        },
                    ],
                    "metadata": {},
                },
                {
                    "content": "string",
                    "role": "user",
                    "attachments": [
                        {
                            "file_id": "string",
                            "tools": [
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                            ],
                        },
                        {
                            "file_id": "string",
                            "tools": [
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                            ],
                        },
                        {
                            "file_id": "string",
                            "tools": [
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                                {"type": "code_interpreter"},
                            ],
                        },
                    ],
                    "metadata": {},
                },
            ],
            metadata={},
            tool_resources={
                "code_interpreter": {"file_ids": ["string", "string", "string"]},
                "file_search": {
                    "vector_store_ids": ["string"],
                    "vector_stores": [
                        {
                            "chunking_strategy": {"type": "auto"},
                            "file_ids": ["string", "string", "string"],
                            "metadata": {},
                        }
                    ],
                },
            },
        )
        assert_matches_type(Thread, thread, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.threads.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        thread = response.parse()
        assert_matches_type(Thread, thread, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.threads.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            thread = await response.parse()
            assert_matches_type(Thread, thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        thread = await async_client.beta.threads.retrieve(
            "string",
        )
        assert_matches_type(Thread, thread, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.threads.with_raw_response.retrieve(
            "string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        thread = response.parse()
        assert_matches_type(Thread, thread, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.threads.with_streaming_response.retrieve(
            "string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            thread = await response.parse()
            assert_matches_type(Thread, thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.beta.threads.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncOpenAI) -> None:
        thread = await async_client.beta.threads.update(
            "string",
        )
        assert_matches_type(Thread, thread, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncOpenAI) -> None:
        thread = await async_client.beta.threads.update(
            "string",
            metadata={},
            tool_resources={
                "code_interpreter": {"file_ids": ["string", "string", "string"]},
                "file_search": {"vector_store_ids": ["string"]},
            },
        )
        assert_matches_type(Thread, thread, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.threads.with_raw_response.update(
            "string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        thread = response.parse()
        assert_matches_type(Thread, thread, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.threads.with_streaming_response.update(
            "string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            thread = await response.parse()
            assert_matches_type(Thread, thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.beta.threads.with_raw_response.update(
                "",
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        thread = await async_client.beta.threads.delete(
            "string",
        )
        assert_matches_type(ThreadDeleted, thread, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.threads.with_raw_response.delete(
            "string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        thread = response.parse()
        assert_matches_type(ThreadDeleted, thread, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.threads.with_streaming_response.delete(
            "string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            thread = await response.parse()
            assert_matches_type(ThreadDeleted, thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.beta.threads.with_raw_response.delete(
                "",
            )

    @parametrize
    async def test_method_create_and_run_overload_1(self, async_client: AsyncOpenAI) -> None:
        thread = await async_client.beta.threads.create_and_run(
            assistant_id="string",
        )
        assert_matches_type(Run, thread, path=["response"])

    @parametrize
    async def test_method_create_and_run_with_all_params_overload_1(self, async_client: AsyncOpenAI) -> None:
        thread = await async_client.beta.threads.create_and_run(
            assistant_id="string",
            instructions="string",
            max_completion_tokens=256,
            max_prompt_tokens=256,
            metadata={},
            model="gpt-4o",
            parallel_tool_calls=True,
            response_format="auto",
            stream=False,
            temperature=1,
            thread={
                "messages": [
                    {
                        "content": "string",
                        "role": "user",
                        "attachments": [
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                        ],
                        "metadata": {},
                    },
                    {
                        "content": "string",
                        "role": "user",
                        "attachments": [
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                        ],
                        "metadata": {},
                    },
                    {
                        "content": "string",
                        "role": "user",
                        "attachments": [
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                        ],
                        "metadata": {},
                    },
                ],
                "metadata": {},
                "tool_resources": {
                    "code_interpreter": {"file_ids": ["string", "string", "string"]},
                    "file_search": {
                        "vector_store_ids": ["string"],
                        "vector_stores": [
                            {
                                "chunking_strategy": {"type": "auto"},
                                "file_ids": ["string", "string", "string"],
                                "metadata": {},
                            }
                        ],
                    },
                },
            },
            tool_choice="none",
            tool_resources={
                "code_interpreter": {"file_ids": ["string", "string", "string"]},
                "file_search": {"vector_store_ids": ["string"]},
            },
            tools=[{"type": "code_interpreter"}, {"type": "code_interpreter"}, {"type": "code_interpreter"}],
            top_p=1,
            truncation_strategy={
                "type": "auto",
                "last_messages": 1,
            },
        )
        assert_matches_type(Run, thread, path=["response"])

    @parametrize
    async def test_raw_response_create_and_run_overload_1(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.threads.with_raw_response.create_and_run(
            assistant_id="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        thread = response.parse()
        assert_matches_type(Run, thread, path=["response"])

    @parametrize
    async def test_streaming_response_create_and_run_overload_1(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.threads.with_streaming_response.create_and_run(
            assistant_id="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            thread = await response.parse()
            assert_matches_type(Run, thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_create_and_run_overload_2(self, async_client: AsyncOpenAI) -> None:
        thread_stream = await async_client.beta.threads.create_and_run(
            assistant_id="string",
            stream=True,
        )
        await thread_stream.response.aclose()

    @parametrize
    async def test_method_create_and_run_with_all_params_overload_2(self, async_client: AsyncOpenAI) -> None:
        thread_stream = await async_client.beta.threads.create_and_run(
            assistant_id="string",
            stream=True,
            instructions="string",
            max_completion_tokens=256,
            max_prompt_tokens=256,
            metadata={},
            model="gpt-4o",
            parallel_tool_calls=True,
            response_format="auto",
            temperature=1,
            thread={
                "messages": [
                    {
                        "content": "string",
                        "role": "user",
                        "attachments": [
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                        ],
                        "metadata": {},
                    },
                    {
                        "content": "string",
                        "role": "user",
                        "attachments": [
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                        ],
                        "metadata": {},
                    },
                    {
                        "content": "string",
                        "role": "user",
                        "attachments": [
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                            {
                                "file_id": "string",
                                "tools": [
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                    {"type": "code_interpreter"},
                                ],
                            },
                        ],
                        "metadata": {},
                    },
                ],
                "metadata": {},
                "tool_resources": {
                    "code_interpreter": {"file_ids": ["string", "string", "string"]},
                    "file_search": {
                        "vector_store_ids": ["string"],
                        "vector_stores": [
                            {
                                "chunking_strategy": {"type": "auto"},
                                "file_ids": ["string", "string", "string"],
                                "metadata": {},
                            }
                        ],
                    },
                },
            },
            tool_choice="none",
            tool_resources={
                "code_interpreter": {"file_ids": ["string", "string", "string"]},
                "file_search": {"vector_store_ids": ["string"]},
            },
            tools=[{"type": "code_interpreter"}, {"type": "code_interpreter"}, {"type": "code_interpreter"}],
            top_p=1,
            truncation_strategy={
                "type": "auto",
                "last_messages": 1,
            },
        )
        await thread_stream.response.aclose()

    @parametrize
    async def test_raw_response_create_and_run_overload_2(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.threads.with_raw_response.create_and_run(
            assistant_id="string",
            stream=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        await stream.close()

    @parametrize
    async def test_streaming_response_create_and_run_overload_2(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.threads.with_streaming_response.create_and_run(
            assistant_id="string",
            stream=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = await response.parse()
            await stream.close()

        assert cast(Any, response.is_closed) is True
