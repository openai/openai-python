# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.beta.threads import (
    Message,
    MessageDeleted,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMessages:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        message = client.beta.threads.messages.create(
            "string",
            content="string",
            role="user",
        )
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        message = client.beta.threads.messages.create(
            "string",
            content="string",
            role="user",
            attachments=[
                {
                    "file_id": "string",
                    "tools": [{"type": "code_interpreter"}, {"type": "code_interpreter"}, {"type": "code_interpreter"}],
                },
                {
                    "file_id": "string",
                    "tools": [{"type": "code_interpreter"}, {"type": "code_interpreter"}, {"type": "code_interpreter"}],
                },
                {
                    "file_id": "string",
                    "tools": [{"type": "code_interpreter"}, {"type": "code_interpreter"}, {"type": "code_interpreter"}],
                },
            ],
            metadata={},
        )
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.beta.threads.messages.with_raw_response.create(
            "string",
            content="string",
            role="user",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.beta.threads.messages.with_streaming_response.create(
            "string",
            content="string",
            role="user",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = response.parse()
            assert_matches_type(Message, message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.beta.threads.messages.with_raw_response.create(
                "",
                content="string",
                role="user",
            )

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        message = client.beta.threads.messages.retrieve(
            "string",
            thread_id="string",
        )
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.beta.threads.messages.with_raw_response.retrieve(
            "string",
            thread_id="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.beta.threads.messages.with_streaming_response.retrieve(
            "string",
            thread_id="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = response.parse()
            assert_matches_type(Message, message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.beta.threads.messages.with_raw_response.retrieve(
                "string",
                thread_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `message_id` but received ''"):
            client.beta.threads.messages.with_raw_response.retrieve(
                "",
                thread_id="string",
            )

    @parametrize
    def test_method_update(self, client: OpenAI) -> None:
        message = client.beta.threads.messages.update(
            "string",
            thread_id="string",
        )
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: OpenAI) -> None:
        message = client.beta.threads.messages.update(
            "string",
            thread_id="string",
            metadata={},
        )
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: OpenAI) -> None:
        response = client.beta.threads.messages.with_raw_response.update(
            "string",
            thread_id="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: OpenAI) -> None:
        with client.beta.threads.messages.with_streaming_response.update(
            "string",
            thread_id="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = response.parse()
            assert_matches_type(Message, message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.beta.threads.messages.with_raw_response.update(
                "string",
                thread_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `message_id` but received ''"):
            client.beta.threads.messages.with_raw_response.update(
                "",
                thread_id="string",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        message = client.beta.threads.messages.list(
            "string",
        )
        assert_matches_type(SyncCursorPage[Message], message, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        message = client.beta.threads.messages.list(
            "string",
            after="string",
            before="string",
            limit=0,
            order="asc",
            run_id="string",
        )
        assert_matches_type(SyncCursorPage[Message], message, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.beta.threads.messages.with_raw_response.list(
            "string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(SyncCursorPage[Message], message, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.beta.threads.messages.with_streaming_response.list(
            "string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = response.parse()
            assert_matches_type(SyncCursorPage[Message], message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.beta.threads.messages.with_raw_response.list(
                "",
            )

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        message = client.beta.threads.messages.delete(
            "string",
            thread_id="string",
        )
        assert_matches_type(MessageDeleted, message, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.beta.threads.messages.with_raw_response.delete(
            "string",
            thread_id="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(MessageDeleted, message, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.beta.threads.messages.with_streaming_response.delete(
            "string",
            thread_id="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = response.parse()
            assert_matches_type(MessageDeleted, message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            client.beta.threads.messages.with_raw_response.delete(
                "string",
                thread_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `message_id` but received ''"):
            client.beta.threads.messages.with_raw_response.delete(
                "",
                thread_id="string",
            )


class TestAsyncMessages:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        message = await async_client.beta.threads.messages.create(
            "string",
            content="string",
            role="user",
        )
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        message = await async_client.beta.threads.messages.create(
            "string",
            content="string",
            role="user",
            attachments=[
                {
                    "file_id": "string",
                    "tools": [{"type": "code_interpreter"}, {"type": "code_interpreter"}, {"type": "code_interpreter"}],
                },
                {
                    "file_id": "string",
                    "tools": [{"type": "code_interpreter"}, {"type": "code_interpreter"}, {"type": "code_interpreter"}],
                },
                {
                    "file_id": "string",
                    "tools": [{"type": "code_interpreter"}, {"type": "code_interpreter"}, {"type": "code_interpreter"}],
                },
            ],
            metadata={},
        )
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.threads.messages.with_raw_response.create(
            "string",
            content="string",
            role="user",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.threads.messages.with_streaming_response.create(
            "string",
            content="string",
            role="user",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = await response.parse()
            assert_matches_type(Message, message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.beta.threads.messages.with_raw_response.create(
                "",
                content="string",
                role="user",
            )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        message = await async_client.beta.threads.messages.retrieve(
            "string",
            thread_id="string",
        )
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.threads.messages.with_raw_response.retrieve(
            "string",
            thread_id="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.threads.messages.with_streaming_response.retrieve(
            "string",
            thread_id="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = await response.parse()
            assert_matches_type(Message, message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.beta.threads.messages.with_raw_response.retrieve(
                "string",
                thread_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `message_id` but received ''"):
            await async_client.beta.threads.messages.with_raw_response.retrieve(
                "",
                thread_id="string",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncOpenAI) -> None:
        message = await async_client.beta.threads.messages.update(
            "string",
            thread_id="string",
        )
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncOpenAI) -> None:
        message = await async_client.beta.threads.messages.update(
            "string",
            thread_id="string",
            metadata={},
        )
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.threads.messages.with_raw_response.update(
            "string",
            thread_id="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(Message, message, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.threads.messages.with_streaming_response.update(
            "string",
            thread_id="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = await response.parse()
            assert_matches_type(Message, message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.beta.threads.messages.with_raw_response.update(
                "string",
                thread_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `message_id` but received ''"):
            await async_client.beta.threads.messages.with_raw_response.update(
                "",
                thread_id="string",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        message = await async_client.beta.threads.messages.list(
            "string",
        )
        assert_matches_type(AsyncCursorPage[Message], message, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        message = await async_client.beta.threads.messages.list(
            "string",
            after="string",
            before="string",
            limit=0,
            order="asc",
            run_id="string",
        )
        assert_matches_type(AsyncCursorPage[Message], message, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.threads.messages.with_raw_response.list(
            "string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(AsyncCursorPage[Message], message, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.threads.messages.with_streaming_response.list(
            "string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = await response.parse()
            assert_matches_type(AsyncCursorPage[Message], message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.beta.threads.messages.with_raw_response.list(
                "",
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        message = await async_client.beta.threads.messages.delete(
            "string",
            thread_id="string",
        )
        assert_matches_type(MessageDeleted, message, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.threads.messages.with_raw_response.delete(
            "string",
            thread_id="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(MessageDeleted, message, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.threads.messages.with_streaming_response.delete(
            "string",
            thread_id="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = await response.parse()
            assert_matches_type(MessageDeleted, message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `thread_id` but received ''"):
            await async_client.beta.threads.messages.with_raw_response.delete(
                "string",
                thread_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `message_id` but received ''"):
            await async_client.beta.threads.messages.with_raw_response.delete(
                "",
                thread_id="string",
            )
