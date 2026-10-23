# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.beta.agents.sessions import Turn

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTurns:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        turn = client.beta.agents.sessions.subagents.turns.retrieve(
            turn_id="turn_id",
            session_id="session_id",
            subagent_id="subagent_id",
        )
        assert_matches_type(Turn, turn, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.beta.agents.sessions.subagents.turns.with_raw_response.retrieve(
            turn_id="turn_id",
            session_id="session_id",
            subagent_id="subagent_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        turn = response.parse()
        assert_matches_type(Turn, turn, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.beta.agents.sessions.subagents.turns.with_streaming_response.retrieve(
            turn_id="turn_id",
            session_id="session_id",
            subagent_id="subagent_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            turn = response.parse()
            assert_matches_type(Turn, turn, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.agents.sessions.subagents.turns.with_raw_response.retrieve(
                turn_id="turn_id",
                session_id="",
                subagent_id="subagent_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `subagent_id` but received ''"):
            client.beta.agents.sessions.subagents.turns.with_raw_response.retrieve(
                turn_id="turn_id",
                session_id="session_id",
                subagent_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `turn_id` but received ''"):
            client.beta.agents.sessions.subagents.turns.with_raw_response.retrieve(
                turn_id="",
                session_id="session_id",
                subagent_id="subagent_id",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        turn = client.beta.agents.sessions.subagents.turns.list(
            subagent_id="subagent_id",
            session_id="session_id",
        )
        assert_matches_type(SyncCursorPage[Turn], turn, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        turn = client.beta.agents.sessions.subagents.turns.list(
            subagent_id="subagent_id",
            session_id="session_id",
            after="after",
            limit=1,
            order="asc",
        )
        assert_matches_type(SyncCursorPage[Turn], turn, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.beta.agents.sessions.subagents.turns.with_raw_response.list(
            subagent_id="subagent_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        turn = response.parse()
        assert_matches_type(SyncCursorPage[Turn], turn, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.beta.agents.sessions.subagents.turns.with_streaming_response.list(
            subagent_id="subagent_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            turn = response.parse()
            assert_matches_type(SyncCursorPage[Turn], turn, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.agents.sessions.subagents.turns.with_raw_response.list(
                subagent_id="subagent_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `subagent_id` but received ''"):
            client.beta.agents.sessions.subagents.turns.with_raw_response.list(
                subagent_id="",
                session_id="session_id",
            )


class TestAsyncTurns:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        turn = await async_client.beta.agents.sessions.subagents.turns.retrieve(
            turn_id="turn_id",
            session_id="session_id",
            subagent_id="subagent_id",
        )
        assert_matches_type(Turn, turn, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.sessions.subagents.turns.with_raw_response.retrieve(
            turn_id="turn_id",
            session_id="session_id",
            subagent_id="subagent_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        turn = response.parse()
        assert_matches_type(Turn, turn, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.sessions.subagents.turns.with_streaming_response.retrieve(
            turn_id="turn_id",
            session_id="session_id",
            subagent_id="subagent_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            turn = await response.parse()
            assert_matches_type(Turn, turn, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.agents.sessions.subagents.turns.with_raw_response.retrieve(
                turn_id="turn_id",
                session_id="",
                subagent_id="subagent_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `subagent_id` but received ''"):
            await async_client.beta.agents.sessions.subagents.turns.with_raw_response.retrieve(
                turn_id="turn_id",
                session_id="session_id",
                subagent_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `turn_id` but received ''"):
            await async_client.beta.agents.sessions.subagents.turns.with_raw_response.retrieve(
                turn_id="",
                session_id="session_id",
                subagent_id="subagent_id",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        turn = await async_client.beta.agents.sessions.subagents.turns.list(
            subagent_id="subagent_id",
            session_id="session_id",
        )
        assert_matches_type(AsyncCursorPage[Turn], turn, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        turn = await async_client.beta.agents.sessions.subagents.turns.list(
            subagent_id="subagent_id",
            session_id="session_id",
            after="after",
            limit=1,
            order="asc",
        )
        assert_matches_type(AsyncCursorPage[Turn], turn, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.sessions.subagents.turns.with_raw_response.list(
            subagent_id="subagent_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        turn = response.parse()
        assert_matches_type(AsyncCursorPage[Turn], turn, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.sessions.subagents.turns.with_streaming_response.list(
            subagent_id="subagent_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            turn = await response.parse()
            assert_matches_type(AsyncCursorPage[Turn], turn, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.agents.sessions.subagents.turns.with_raw_response.list(
                subagent_id="subagent_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `subagent_id` but received ''"):
            await async_client.beta.agents.sessions.subagents.turns.with_raw_response.list(
                subagent_id="",
                session_id="session_id",
            )
