# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types.beta.chatkit import (
    ChatSession,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSessions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        session = client.beta.chatkit.sessions.create(
            user="x",
            workflow={"id": "id"},
        )
        assert_matches_type(ChatSession, session, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        session = client.beta.chatkit.sessions.create(
            user="x",
            workflow={
                "id": "id",
                "state_variables": {"foo": "string"},
                "tracing": {"enabled": True},
                "version": "version",
            },
            chatkit_configuration={
                "automatic_thread_titling": {"enabled": True},
                "file_upload": {
                    "enabled": True,
                    "max_file_size": 1,
                    "max_files": 1,
                },
                "history": {
                    "enabled": True,
                    "recent_threads": 1,
                },
            },
            expires_after={
                "anchor": "created_at",
                "seconds": 1,
            },
            rate_limits={"max_requests_per_1_minute": 1},
        )
        assert_matches_type(ChatSession, session, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.beta.chatkit.sessions.with_raw_response.create(
            user="x",
            workflow={"id": "id"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(ChatSession, session, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.beta.chatkit.sessions.with_streaming_response.create(
            user="x",
            workflow={"id": "id"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(ChatSession, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_cancel(self, client: OpenAI) -> None:
        session = client.beta.chatkit.sessions.cancel(
            "cksess_123",
        )
        assert_matches_type(ChatSession, session, path=["response"])

    @parametrize
    def test_raw_response_cancel(self, client: OpenAI) -> None:
        response = client.beta.chatkit.sessions.with_raw_response.cancel(
            "cksess_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(ChatSession, session, path=["response"])

    @parametrize
    def test_streaming_response_cancel(self, client: OpenAI) -> None:
        with client.beta.chatkit.sessions.with_streaming_response.cancel(
            "cksess_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(ChatSession, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_cancel(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.chatkit.sessions.with_raw_response.cancel(
                "",
            )


class TestAsyncSessions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        session = await async_client.beta.chatkit.sessions.create(
            user="x",
            workflow={"id": "id"},
        )
        assert_matches_type(ChatSession, session, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        session = await async_client.beta.chatkit.sessions.create(
            user="x",
            workflow={
                "id": "id",
                "state_variables": {"foo": "string"},
                "tracing": {"enabled": True},
                "version": "version",
            },
            chatkit_configuration={
                "automatic_thread_titling": {"enabled": True},
                "file_upload": {
                    "enabled": True,
                    "max_file_size": 1,
                    "max_files": 1,
                },
                "history": {
                    "enabled": True,
                    "recent_threads": 1,
                },
            },
            expires_after={
                "anchor": "created_at",
                "seconds": 1,
            },
            rate_limits={"max_requests_per_1_minute": 1},
        )
        assert_matches_type(ChatSession, session, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.chatkit.sessions.with_raw_response.create(
            user="x",
            workflow={"id": "id"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(ChatSession, session, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.chatkit.sessions.with_streaming_response.create(
            user="x",
            workflow={"id": "id"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(ChatSession, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_cancel(self, async_client: AsyncOpenAI) -> None:
        session = await async_client.beta.chatkit.sessions.cancel(
            "cksess_123",
        )
        assert_matches_type(ChatSession, session, path=["response"])

    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.chatkit.sessions.with_raw_response.cancel(
            "cksess_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(ChatSession, session, path=["response"])

    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.chatkit.sessions.with_streaming_response.cancel(
            "cksess_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(ChatSession, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_cancel(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.chatkit.sessions.with_raw_response.cancel(
                "",
            )
