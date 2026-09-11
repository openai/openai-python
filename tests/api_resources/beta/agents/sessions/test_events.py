# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEvents:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        event = client.beta.agents.sessions.events.create(
            session_id="session_id",
            events=[
                {
                    "input": [
                        {
                            "content": [
                                {
                                    "text": "text",
                                    "type": "input_text",
                                }
                            ],
                            "role": "user",
                        }
                    ],
                    "type": "agent.session.input.message",
                }
            ],
        )
        assert event is None

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        event = client.beta.agents.sessions.events.create(
            session_id="session_id",
            events=[
                {
                    "input": [
                        {
                            "content": [
                                {
                                    "text": "text",
                                    "type": "input_text",
                                }
                            ],
                            "role": "user",
                            "type": "message",
                        }
                    ],
                    "type": "agent.session.input.message",
                }
            ],
            idempotency_key="x",
        )
        assert event is None

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.beta.agents.sessions.events.with_raw_response.create(
            session_id="session_id",
            events=[
                {
                    "input": [
                        {
                            "content": [
                                {
                                    "text": "text",
                                    "type": "input_text",
                                }
                            ],
                            "role": "user",
                        }
                    ],
                    "type": "agent.session.input.message",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        event = response.parse()
        assert event is None

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.beta.agents.sessions.events.with_streaming_response.create(
            session_id="session_id",
            events=[
                {
                    "input": [
                        {
                            "content": [
                                {
                                    "text": "text",
                                    "type": "input_text",
                                }
                            ],
                            "role": "user",
                        }
                    ],
                    "type": "agent.session.input.message",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            event = response.parse()
            assert event is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.agents.sessions.events.with_raw_response.create(
                session_id="",
                events=[
                    {
                        "input": [
                            {
                                "content": [
                                    {
                                        "text": "text",
                                        "type": "input_text",
                                    }
                                ],
                                "role": "user",
                            }
                        ],
                        "type": "agent.session.input.message",
                    }
                ],
            )

    @parametrize
    def test_method_stream(self, client: OpenAI) -> None:
        event_stream = client.beta.agents.sessions.events.stream(
            "session_id",
        )
        event_stream.response.close()

    @parametrize
    def test_raw_response_stream(self, client: OpenAI) -> None:
        response = client.beta.agents.sessions.events.with_raw_response.stream(
            "session_id",
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        stream.close()

    @parametrize
    def test_streaming_response_stream(self, client: OpenAI) -> None:
        with client.beta.agents.sessions.events.with_streaming_response.stream(
            "session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = response.parse()
            stream.close()

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_stream(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.agents.sessions.events.with_raw_response.stream(
                "",
            )


class TestAsyncEvents:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        event = await async_client.beta.agents.sessions.events.create(
            session_id="session_id",
            events=[
                {
                    "input": [
                        {
                            "content": [
                                {
                                    "text": "text",
                                    "type": "input_text",
                                }
                            ],
                            "role": "user",
                        }
                    ],
                    "type": "agent.session.input.message",
                }
            ],
        )
        assert event is None

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        event = await async_client.beta.agents.sessions.events.create(
            session_id="session_id",
            events=[
                {
                    "input": [
                        {
                            "content": [
                                {
                                    "text": "text",
                                    "type": "input_text",
                                }
                            ],
                            "role": "user",
                            "type": "message",
                        }
                    ],
                    "type": "agent.session.input.message",
                }
            ],
            idempotency_key="x",
        )
        assert event is None

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.sessions.events.with_raw_response.create(
            session_id="session_id",
            events=[
                {
                    "input": [
                        {
                            "content": [
                                {
                                    "text": "text",
                                    "type": "input_text",
                                }
                            ],
                            "role": "user",
                        }
                    ],
                    "type": "agent.session.input.message",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        event = response.parse()
        assert event is None

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.sessions.events.with_streaming_response.create(
            session_id="session_id",
            events=[
                {
                    "input": [
                        {
                            "content": [
                                {
                                    "text": "text",
                                    "type": "input_text",
                                }
                            ],
                            "role": "user",
                        }
                    ],
                    "type": "agent.session.input.message",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            event = await response.parse()
            assert event is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.agents.sessions.events.with_raw_response.create(
                session_id="",
                events=[
                    {
                        "input": [
                            {
                                "content": [
                                    {
                                        "text": "text",
                                        "type": "input_text",
                                    }
                                ],
                                "role": "user",
                            }
                        ],
                        "type": "agent.session.input.message",
                    }
                ],
            )

    @parametrize
    async def test_method_stream(self, async_client: AsyncOpenAI) -> None:
        event_stream = await async_client.beta.agents.sessions.events.stream(
            "session_id",
        )
        await event_stream.response.aclose()

    @parametrize
    async def test_raw_response_stream(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.sessions.events.with_raw_response.stream(
            "session_id",
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        await stream.close()

    @parametrize
    async def test_streaming_response_stream(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.sessions.events.with_streaming_response.stream(
            "session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = await response.parse()
            await stream.close()

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_stream(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.agents.sessions.events.with_raw_response.stream(
                "",
            )
