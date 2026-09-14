# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.beta import AgentSession, AgentSessionDeleted

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSessions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create_overload_1(self, client: OpenAI) -> None:
        session = client.beta.agents.sessions.create(
            environment={"type": "none"},
        )
        assert_matches_type(AgentSession, session, path=["response"])

    @parametrize
    def test_method_create_with_all_params_overload_1(self, client: OpenAI) -> None:
        session = client.beta.agents.sessions.create(
            environment={"type": "none"},
            agent={
                "instructions": "instructions",
                "model": "model",
                "multi_agent": {
                    "enabled": True,
                    "max_concurrent_subagents": 1,
                },
                "reasoning": {
                    "effort": "none",
                    "summary": "concise",
                },
                "service_tier": "auto",
                "text": {
                    "format": {"type": "text"},
                    "verbosity": "low",
                },
                "tools": [
                    {
                        "description": "description",
                        "name": "name",
                        "parameters": {"foo": "bar"},
                        "type": "function",
                        "defer_loading": True,
                    }
                ],
            },
            agent_id="agent_id",
            input="x",
            metadata={"foo": "string"},
            stream=False,
            vault_ids=["string"],
        )
        assert_matches_type(AgentSession, session, path=["response"])

    @parametrize
    def test_raw_response_create_overload_1(self, client: OpenAI) -> None:
        response = client.beta.agents.sessions.with_raw_response.create(
            environment={"type": "none"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(AgentSession, session, path=["response"])

    @parametrize
    def test_streaming_response_create_overload_1(self, client: OpenAI) -> None:
        with client.beta.agents.sessions.with_streaming_response.create(
            environment={"type": "none"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(AgentSession, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_create_overload_2(self, client: OpenAI) -> None:
        session_stream = client.beta.agents.sessions.create(
            environment={"type": "none"},
            stream=True,
        )
        session_stream.response.close()

    @parametrize
    def test_method_create_with_all_params_overload_2(self, client: OpenAI) -> None:
        session_stream = client.beta.agents.sessions.create(
            environment={"type": "none"},
            stream=True,
            agent={
                "instructions": "instructions",
                "model": "model",
                "multi_agent": {
                    "enabled": True,
                    "max_concurrent_subagents": 1,
                },
                "reasoning": {
                    "effort": "none",
                    "summary": "concise",
                },
                "service_tier": "auto",
                "text": {
                    "format": {"type": "text"},
                    "verbosity": "low",
                },
                "tools": [
                    {
                        "description": "description",
                        "name": "name",
                        "parameters": {"foo": "bar"},
                        "type": "function",
                        "defer_loading": True,
                    }
                ],
            },
            agent_id="agent_id",
            input="x",
            metadata={"foo": "string"},
            vault_ids=["string"],
        )
        session_stream.response.close()

    @parametrize
    def test_raw_response_create_overload_2(self, client: OpenAI) -> None:
        response = client.beta.agents.sessions.with_raw_response.create(
            environment={"type": "none"},
            stream=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        stream.close()

    @parametrize
    def test_streaming_response_create_overload_2(self, client: OpenAI) -> None:
        with client.beta.agents.sessions.with_streaming_response.create(
            environment={"type": "none"},
            stream=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = response.parse()
            stream.close()

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        session = client.beta.agents.sessions.retrieve(
            "session_id",
        )
        assert_matches_type(AgentSession, session, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.beta.agents.sessions.with_raw_response.retrieve(
            "session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(AgentSession, session, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.beta.agents.sessions.with_streaming_response.retrieve(
            "session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(AgentSession, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.agents.sessions.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_update(self, client: OpenAI) -> None:
        session = client.beta.agents.sessions.update(
            session_id="session_id",
        )
        assert_matches_type(AgentSession, session, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: OpenAI) -> None:
        session = client.beta.agents.sessions.update(
            session_id="session_id",
            metadata={"foo": "string"},
        )
        assert_matches_type(AgentSession, session, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: OpenAI) -> None:
        response = client.beta.agents.sessions.with_raw_response.update(
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(AgentSession, session, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: OpenAI) -> None:
        with client.beta.agents.sessions.with_streaming_response.update(
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(AgentSession, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.agents.sessions.with_raw_response.update(
                session_id="",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        session = client.beta.agents.sessions.list()
        assert_matches_type(SyncCursorPage[AgentSession], session, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        session = client.beta.agents.sessions.list(
            after="after",
            agent_id="agent_id",
            limit=1,
            order="asc",
        )
        assert_matches_type(SyncCursorPage[AgentSession], session, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.beta.agents.sessions.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SyncCursorPage[AgentSession], session, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.beta.agents.sessions.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(SyncCursorPage[AgentSession], session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        session = client.beta.agents.sessions.delete(
            "session_id",
        )
        assert_matches_type(AgentSessionDeleted, session, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.beta.agents.sessions.with_raw_response.delete(
            "session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(AgentSessionDeleted, session, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.beta.agents.sessions.with_streaming_response.delete(
            "session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(AgentSessionDeleted, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.agents.sessions.with_raw_response.delete(
                "",
            )


class TestAsyncSessions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        session = await async_client.beta.agents.sessions.create(
            environment={"type": "none"},
        )
        assert_matches_type(AgentSession, session, path=["response"])

    @parametrize
    async def test_method_create_with_all_params_overload_1(self, async_client: AsyncOpenAI) -> None:
        session = await async_client.beta.agents.sessions.create(
            environment={"type": "none"},
            agent={
                "instructions": "instructions",
                "model": "model",
                "multi_agent": {
                    "enabled": True,
                    "max_concurrent_subagents": 1,
                },
                "reasoning": {
                    "effort": "none",
                    "summary": "concise",
                },
                "service_tier": "auto",
                "text": {
                    "format": {"type": "text"},
                    "verbosity": "low",
                },
                "tools": [
                    {
                        "description": "description",
                        "name": "name",
                        "parameters": {"foo": "bar"},
                        "type": "function",
                        "defer_loading": True,
                    }
                ],
            },
            agent_id="agent_id",
            input="x",
            metadata={"foo": "string"},
            stream=False,
            vault_ids=["string"],
        )
        assert_matches_type(AgentSession, session, path=["response"])

    @parametrize
    async def test_raw_response_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.sessions.with_raw_response.create(
            environment={"type": "none"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(AgentSession, session, path=["response"])

    @parametrize
    async def test_streaming_response_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.sessions.with_streaming_response.create(
            environment={"type": "none"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(AgentSession, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_create_overload_2(self, async_client: AsyncOpenAI) -> None:
        session_stream = await async_client.beta.agents.sessions.create(
            environment={"type": "none"},
            stream=True,
        )
        await session_stream.response.aclose()

    @parametrize
    async def test_method_create_with_all_params_overload_2(self, async_client: AsyncOpenAI) -> None:
        session_stream = await async_client.beta.agents.sessions.create(
            environment={"type": "none"},
            stream=True,
            agent={
                "instructions": "instructions",
                "model": "model",
                "multi_agent": {
                    "enabled": True,
                    "max_concurrent_subagents": 1,
                },
                "reasoning": {
                    "effort": "none",
                    "summary": "concise",
                },
                "service_tier": "auto",
                "text": {
                    "format": {"type": "text"},
                    "verbosity": "low",
                },
                "tools": [
                    {
                        "description": "description",
                        "name": "name",
                        "parameters": {"foo": "bar"},
                        "type": "function",
                        "defer_loading": True,
                    }
                ],
            },
            agent_id="agent_id",
            input="x",
            metadata={"foo": "string"},
            vault_ids=["string"],
        )
        await session_stream.response.aclose()

    @parametrize
    async def test_raw_response_create_overload_2(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.sessions.with_raw_response.create(
            environment={"type": "none"},
            stream=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        await stream.close()

    @parametrize
    async def test_streaming_response_create_overload_2(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.sessions.with_streaming_response.create(
            environment={"type": "none"},
            stream=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = await response.parse()
            await stream.close()

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        session = await async_client.beta.agents.sessions.retrieve(
            "session_id",
        )
        assert_matches_type(AgentSession, session, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.sessions.with_raw_response.retrieve(
            "session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(AgentSession, session, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.sessions.with_streaming_response.retrieve(
            "session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(AgentSession, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.agents.sessions.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncOpenAI) -> None:
        session = await async_client.beta.agents.sessions.update(
            session_id="session_id",
        )
        assert_matches_type(AgentSession, session, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncOpenAI) -> None:
        session = await async_client.beta.agents.sessions.update(
            session_id="session_id",
            metadata={"foo": "string"},
        )
        assert_matches_type(AgentSession, session, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.sessions.with_raw_response.update(
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(AgentSession, session, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.sessions.with_streaming_response.update(
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(AgentSession, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.agents.sessions.with_raw_response.update(
                session_id="",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        session = await async_client.beta.agents.sessions.list()
        assert_matches_type(AsyncCursorPage[AgentSession], session, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        session = await async_client.beta.agents.sessions.list(
            after="after",
            agent_id="agent_id",
            limit=1,
            order="asc",
        )
        assert_matches_type(AsyncCursorPage[AgentSession], session, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.sessions.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(AsyncCursorPage[AgentSession], session, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.sessions.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(AsyncCursorPage[AgentSession], session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        session = await async_client.beta.agents.sessions.delete(
            "session_id",
        )
        assert_matches_type(AgentSessionDeleted, session, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.sessions.with_raw_response.delete(
            "session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(AgentSessionDeleted, session, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.sessions.with_streaming_response.delete(
            "session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(AgentSessionDeleted, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.agents.sessions.with_raw_response.delete(
                "",
            )
