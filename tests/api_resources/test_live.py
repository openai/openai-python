# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types.live import LiveCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestLive:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        live = client.live.create(
            session={"model": "gpt-live-1"},
            transport={
                "sdp": "x",
                "type": "webrtc",
            },
        )
        assert_matches_type(LiveCreateResponse, live, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        live = client.live.create(
            session={
                "model": "x",
                "audio": {"output": {"voice": "alloy"}},
                "client": {
                    "data_channel": {
                        "allowed_client_events": "all",
                        "allowed_server_events": "all",
                    }
                },
                "delegation": {"type": "client"},
                "input": [
                    {
                        "content": [
                            {
                                "text": "text",
                                "type": "input_text",
                            }
                        ],
                        "role": "developer",
                        "id": "id",
                        "status": "incomplete",
                        "type": "message",
                    }
                ],
                "instructions": "instructions",
                "store": True,
            },
            transport={
                "sdp": "x",
                "type": "webrtc",
            },
        )
        assert_matches_type(LiveCreateResponse, live, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.live.with_raw_response.create(
            session={"model": "gpt-live-1"},
            transport={
                "sdp": "x",
                "type": "webrtc",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        live = response.parse()
        assert_matches_type(LiveCreateResponse, live, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.live.with_streaming_response.create(
            session={"model": "gpt-live-1"},
            transport={
                "sdp": "x",
                "type": "webrtc",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            live = response.parse()
            assert_matches_type(LiveCreateResponse, live, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncLive:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        live = await async_client.live.create(
            session={"model": "gpt-live-1"},
            transport={
                "sdp": "x",
                "type": "webrtc",
            },
        )
        assert_matches_type(LiveCreateResponse, live, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        live = await async_client.live.create(
            session={
                "model": "x",
                "audio": {"output": {"voice": "alloy"}},
                "client": {
                    "data_channel": {
                        "allowed_client_events": "all",
                        "allowed_server_events": "all",
                    }
                },
                "delegation": {"type": "client"},
                "input": [
                    {
                        "content": [
                            {
                                "text": "text",
                                "type": "input_text",
                            }
                        ],
                        "role": "developer",
                        "id": "id",
                        "status": "incomplete",
                        "type": "message",
                    }
                ],
                "instructions": "instructions",
                "store": True,
            },
            transport={
                "sdp": "x",
                "type": "webrtc",
            },
        )
        assert_matches_type(LiveCreateResponse, live, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.live.with_raw_response.create(
            session={"model": "gpt-live-1"},
            transport={
                "sdp": "x",
                "type": "webrtc",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        live = response.parse()
        assert_matches_type(LiveCreateResponse, live, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.live.with_streaming_response.create(
            session={"model": "gpt-live-1"},
            transport={
                "sdp": "x",
                "type": "webrtc",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            live = await response.parse()
            assert_matches_type(LiveCreateResponse, live, path=["response"])

        assert cast(Any, response.is_closed) is True
