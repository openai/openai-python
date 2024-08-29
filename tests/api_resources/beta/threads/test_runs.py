# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.beta.threads import (
    Run,
)

# pyright: reportDeprecated=false

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRuns:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create_overload_1(self, client: OpenAI) -> None:
        run = client.beta.threads.runs.create(
            "string",
            assistant_id="string",
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    def test_method_create_with_all_params_overload_1(self, client: OpenAI) -> None:
        run = client.beta.threads.runs.create(
            thread_id="thread_id",
            assistant_id="assistant_id",
            include=["step_details.tool_calls[*].file_search.results[*].content"],
            additional_instructions="additional_instructions",
            additional_messages=[
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
            instructions="string",
            max_completion_tokens=256,
            max_prompt_tokens=256,
            metadata={},
            model="gpt-4o",
            parallel_tool_calls=True,
            response_format="auto",
            stream=False,
            temperature=1,
            tool_choice="none",
            tools=[{"type": "code_interpreter"}, {"type": "code_interpreter"}, {"type": "code_interpreter"}],
            top_p=1,
            truncation_strategy={
                "type": "auto",
                "last_messages": 1,
            },
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    def test_raw_response_create_overload_1(self, client: OpenAI) -> None:
        response = client.beta.threads.runs.with_raw_response.create(
            "string",
            assistant_id="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    def test_streaming_response_create_overload_1(self, client: OpenAI) -> None:
        with client.beta.threads.runs.with_streaming_response.create(
            "string",
            assistant_id="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = response.parse()
            assert_matches_type(Run, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create_overload_1(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.beta.threads.runs.with_raw_response.create(
                "",
                assistant_id="string",
            )

    @parametrize
    def test_method_create_overload_2(self, client: OpenAI) -> None:
        run_stream = client.beta.threads.runs.create(
            "string",
            assistant_id="string",
            stream=True,
        )
        run_stream.response.close()

    @parametrize
    def test_method_create_with_all_params_overload_2(self, client: OpenAI) -> None:
        run_stream = client.beta.threads.runs.create(
            "string",
            assistant_id="string",
            stream=True,
            include=["step_details.tool_calls[*].file_search.results[*].content"],
            additional_instructions="additional_instructions",
            additional_messages=[
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
            instructions="string",
            max_completion_tokens=256,
            max_prompt_tokens=256,
            metadata={},
            model="gpt-4o",
            parallel_tool_calls=True,
            response_format="auto",
            temperature=1,
            tool_choice="none",
            tools=[{"type": "code_interpreter"}, {"type": "code_interpreter"}, {"type": "code_interpreter"}],
            top_p=1,
            truncation_strategy={
                "type": "auto",
                "last_messages": 1,
            },
        )
        run_stream.response.close()

    @parametrize
    def test_raw_response_create_overload_2(self, client: OpenAI) -> None:
        response = client.beta.threads.runs.with_raw_response.create(
            "string",
            assistant_id="string",
            stream=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        stream.close()

    @parametrize
    def test_streaming_response_create_overload_2(self, client: OpenAI) -> None:
        with client.beta.threads.runs.with_streaming_response.create(
            "string",
            assistant_id="string",
            stream=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = response.parse()
            stream.close()

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create_overload_2(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.beta.threads.runs.with_raw_response.create(
                "",
                assistant_id="string",
                stream=True,
            )

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

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.beta.threads.runs.with_streaming_response.retrieve(
            "string",
            thread_id="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = response.parse()
            assert_matches_type(Run, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.beta.threads.runs.with_raw_response.retrieve(
                "string",
                thread_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `run_id` but received ''"):
            client.beta.threads.runs.with_raw_response.retrieve(
                "",
                thread_id="string",
            )

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

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: OpenAI) -> None:
        with client.beta.threads.runs.with_streaming_response.update(
            "string",
            thread_id="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = response.parse()
            assert_matches_type(Run, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.beta.threads.runs.with_raw_response.update(
                "string",
                thread_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `run_id` but received ''"):
            client.beta.threads.runs.with_raw_response.update(
                "",
                thread_id="string",
            )

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

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(SyncCursorPage[Run], run, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.beta.threads.runs.with_streaming_response.list(
            "string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = response.parse()
            assert_matches_type(SyncCursorPage[Run], run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.beta.threads.runs.with_raw_response.list(
                "",
            )

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

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    def test_streaming_response_cancel(self, client: OpenAI) -> None:
        with client.beta.threads.runs.with_streaming_response.cancel(
            "string",
            thread_id="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = response.parse()
            assert_matches_type(Run, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_cancel(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.beta.threads.runs.with_raw_response.cancel(
                "string",
                thread_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `run_id` but received ''"):
            client.beta.threads.runs.with_raw_response.cancel(
                "",
                thread_id="string",
            )

    @parametrize
    def test_method_submit_tool_outputs_overload_1(self, client: OpenAI) -> None:
        run = client.beta.threads.runs.submit_tool_outputs(
            "string",
            thread_id="string",
            tool_outputs=[{}, {}, {}],
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    def test_method_submit_tool_outputs_with_all_params_overload_1(self, client: OpenAI) -> None:
        run = client.beta.threads.runs.submit_tool_outputs(
            "string",
            thread_id="string",
            tool_outputs=[
                {
                    "output": "output",
                    "tool_call_id": "tool_call_id",
                },
                {
                    "output": "output",
                    "tool_call_id": "tool_call_id",
                },
                {
                    "output": "output",
                    "tool_call_id": "tool_call_id",
                },
            ],
            stream=False,
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    def test_raw_response_submit_tool_outputs_overload_1(self, client: OpenAI) -> None:
        response = client.beta.threads.runs.with_raw_response.submit_tool_outputs(
            "string",
            thread_id="string",
            tool_outputs=[{}, {}, {}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    def test_streaming_response_submit_tool_outputs_overload_1(self, client: OpenAI) -> None:
        with client.beta.threads.runs.with_streaming_response.submit_tool_outputs(
            "string",
            thread_id="string",
            tool_outputs=[{}, {}, {}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = response.parse()
            assert_matches_type(Run, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_submit_tool_outputs_overload_1(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.beta.threads.runs.with_raw_response.submit_tool_outputs(
                "string",
                thread_id="",
                tool_outputs=[{}, {}, {}],
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `run_id` but received ''"):
            client.beta.threads.runs.with_raw_response.submit_tool_outputs(
                "",
                thread_id="string",
                tool_outputs=[{}, {}, {}],
            )

    @parametrize
    def test_method_submit_tool_outputs_overload_2(self, client: OpenAI) -> None:
        run_stream = client.beta.threads.runs.submit_tool_outputs(
            "string",
            thread_id="string",
            stream=True,
            tool_outputs=[{}, {}, {}],
        )
        run_stream.response.close()

    @parametrize
    def test_raw_response_submit_tool_outputs_overload_2(self, client: OpenAI) -> None:
        response = client.beta.threads.runs.with_raw_response.submit_tool_outputs(
            "string",
            thread_id="string",
            stream=True,
            tool_outputs=[{}, {}, {}],
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        stream.close()

    @parametrize
    def test_streaming_response_submit_tool_outputs_overload_2(self, client: OpenAI) -> None:
        with client.beta.threads.runs.with_streaming_response.submit_tool_outputs(
            "string",
            thread_id="string",
            stream=True,
            tool_outputs=[{}, {}, {}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = response.parse()
            stream.close()

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_submit_tool_outputs_overload_2(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.beta.threads.runs.with_raw_response.submit_tool_outputs(
                "string",
                thread_id="",
                stream=True,
                tool_outputs=[{}, {}, {}],
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `run_id` but received ''"):
            client.beta.threads.runs.with_raw_response.submit_tool_outputs(
                "",
                thread_id="string",
                stream=True,
                tool_outputs=[{}, {}, {}],
            )


class TestAsyncRuns:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        run = await async_client.beta.threads.runs.create(
            "string",
            assistant_id="string",
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_method_create_with_all_params_overload_1(self, async_client: AsyncOpenAI) -> None:
        run = await async_client.beta.threads.runs.create(
            thread_id="thread_id",
            assistant_id="assistant_id",
            include=["step_details.tool_calls[*].file_search.results[*].content"],
            additional_instructions="additional_instructions",
            additional_messages=[
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
            instructions="string",
            max_completion_tokens=256,
            max_prompt_tokens=256,
            metadata={},
            model="gpt-4o",
            parallel_tool_calls=True,
            response_format="auto",
            stream=False,
            temperature=1,
            tool_choice="none",
            tools=[{"type": "code_interpreter"}, {"type": "code_interpreter"}, {"type": "code_interpreter"}],
            top_p=1,
            truncation_strategy={
                "type": "auto",
                "last_messages": 1,
            },
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_raw_response_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.threads.runs.with_raw_response.create(
            "string",
            assistant_id="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_streaming_response_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.threads.runs.with_streaming_response.create(
            "string",
            assistant_id="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = await response.parse()
            assert_matches_type(Run, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.beta.threads.runs.with_raw_response.create(
                "",
                assistant_id="string",
            )

    @parametrize
    async def test_method_create_overload_2(self, async_client: AsyncOpenAI) -> None:
        run_stream = await async_client.beta.threads.runs.create(
            "string",
            assistant_id="string",
            stream=True,
        )
        await run_stream.response.aclose()

    @parametrize
    async def test_method_create_with_all_params_overload_2(self, async_client: AsyncOpenAI) -> None:
        run_stream = await async_client.beta.threads.runs.create(
            "string",
            assistant_id="string",
            stream=True,
            include=["step_details.tool_calls[*].file_search.results[*].content"],
            additional_instructions="additional_instructions",
            additional_messages=[
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
            instructions="string",
            max_completion_tokens=256,
            max_prompt_tokens=256,
            metadata={},
            model="gpt-4o",
            parallel_tool_calls=True,
            response_format="auto",
            temperature=1,
            tool_choice="none",
            tools=[{"type": "code_interpreter"}, {"type": "code_interpreter"}, {"type": "code_interpreter"}],
            top_p=1,
            truncation_strategy={
                "type": "auto",
                "last_messages": 1,
            },
        )
        await run_stream.response.aclose()

    @parametrize
    async def test_raw_response_create_overload_2(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.threads.runs.with_raw_response.create(
            "string",
            assistant_id="string",
            stream=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        await stream.close()

    @parametrize
    async def test_streaming_response_create_overload_2(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.threads.runs.with_streaming_response.create(
            "string",
            assistant_id="string",
            stream=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = await response.parse()
            await stream.close()

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create_overload_2(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.beta.threads.runs.with_raw_response.create(
                "",
                assistant_id="string",
                stream=True,
            )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        run = await async_client.beta.threads.runs.retrieve(
            "string",
            thread_id="string",
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.threads.runs.with_raw_response.retrieve(
            "string",
            thread_id="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.threads.runs.with_streaming_response.retrieve(
            "string",
            thread_id="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = await response.parse()
            assert_matches_type(Run, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.beta.threads.runs.with_raw_response.retrieve(
                "string",
                thread_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `run_id` but received ''"):
            await async_client.beta.threads.runs.with_raw_response.retrieve(
                "",
                thread_id="string",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncOpenAI) -> None:
        run = await async_client.beta.threads.runs.update(
            "string",
            thread_id="string",
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncOpenAI) -> None:
        run = await async_client.beta.threads.runs.update(
            "string",
            thread_id="string",
            metadata={},
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.threads.runs.with_raw_response.update(
            "string",
            thread_id="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.threads.runs.with_streaming_response.update(
            "string",
            thread_id="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = await response.parse()
            assert_matches_type(Run, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.beta.threads.runs.with_raw_response.update(
                "string",
                thread_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `run_id` but received ''"):
            await async_client.beta.threads.runs.with_raw_response.update(
                "",
                thread_id="string",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        run = await async_client.beta.threads.runs.list(
            "string",
        )
        assert_matches_type(AsyncCursorPage[Run], run, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        run = await async_client.beta.threads.runs.list(
            "string",
            after="string",
            before="string",
            limit=0,
            order="asc",
        )
        assert_matches_type(AsyncCursorPage[Run], run, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.threads.runs.with_raw_response.list(
            "string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(AsyncCursorPage[Run], run, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.threads.runs.with_streaming_response.list(
            "string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = await response.parse()
            assert_matches_type(AsyncCursorPage[Run], run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.beta.threads.runs.with_raw_response.list(
                "",
            )

    @parametrize
    async def test_method_cancel(self, async_client: AsyncOpenAI) -> None:
        run = await async_client.beta.threads.runs.cancel(
            "string",
            thread_id="string",
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.threads.runs.with_raw_response.cancel(
            "string",
            thread_id="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.threads.runs.with_streaming_response.cancel(
            "string",
            thread_id="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = await response.parse()
            assert_matches_type(Run, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_cancel(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.beta.threads.runs.with_raw_response.cancel(
                "string",
                thread_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `run_id` but received ''"):
            await async_client.beta.threads.runs.with_raw_response.cancel(
                "",
                thread_id="string",
            )

    @parametrize
    async def test_method_submit_tool_outputs_overload_1(self, async_client: AsyncOpenAI) -> None:
        run = await async_client.beta.threads.runs.submit_tool_outputs(
            "string",
            thread_id="string",
            tool_outputs=[{}, {}, {}],
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_method_submit_tool_outputs_with_all_params_overload_1(self, async_client: AsyncOpenAI) -> None:
        run = await async_client.beta.threads.runs.submit_tool_outputs(
            "string",
            thread_id="string",
            tool_outputs=[
                {
                    "output": "output",
                    "tool_call_id": "tool_call_id",
                },
                {
                    "output": "output",
                    "tool_call_id": "tool_call_id",
                },
                {
                    "output": "output",
                    "tool_call_id": "tool_call_id",
                },
            ],
            stream=False,
        )
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_raw_response_submit_tool_outputs_overload_1(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.threads.runs.with_raw_response.submit_tool_outputs(
            "string",
            thread_id="string",
            tool_outputs=[{}, {}, {}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(Run, run, path=["response"])

    @parametrize
    async def test_streaming_response_submit_tool_outputs_overload_1(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.threads.runs.with_streaming_response.submit_tool_outputs(
            "string",
            thread_id="string",
            tool_outputs=[{}, {}, {}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = await response.parse()
            assert_matches_type(Run, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_submit_tool_outputs_overload_1(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.beta.threads.runs.with_raw_response.submit_tool_outputs(
                "string",
                thread_id="",
                tool_outputs=[{}, {}, {}],
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `run_id` but received ''"):
            await async_client.beta.threads.runs.with_raw_response.submit_tool_outputs(
                "",
                thread_id="string",
                tool_outputs=[{}, {}, {}],
            )

    @parametrize
    async def test_method_submit_tool_outputs_overload_2(self, async_client: AsyncOpenAI) -> None:
        run_stream = await async_client.beta.threads.runs.submit_tool_outputs(
            "string",
            thread_id="string",
            stream=True,
            tool_outputs=[{}, {}, {}],
        )
        await run_stream.response.aclose()

    @parametrize
    async def test_raw_response_submit_tool_outputs_overload_2(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.threads.runs.with_raw_response.submit_tool_outputs(
            "string",
            thread_id="string",
            stream=True,
            tool_outputs=[{}, {}, {}],
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        await stream.close()

    @parametrize
    async def test_streaming_response_submit_tool_outputs_overload_2(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.threads.runs.with_streaming_response.submit_tool_outputs(
            "string",
            thread_id="string",
            stream=True,
            tool_outputs=[{}, {}, {}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = await response.parse()
            await stream.close()

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_submit_tool_outputs_overload_2(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.beta.threads.runs.with_raw_response.submit_tool_outputs(
                "string",
                thread_id="",
                stream=True,
                tool_outputs=[{}, {}, {}],
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `run_id` but received ''"):
            await async_client.beta.threads.runs.with_raw_response.submit_tool_outputs(
                "",
                thread_id="string",
                stream=True,
                tool_outputs=[{}, {}, {}],
            )
