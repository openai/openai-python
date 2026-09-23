# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import httpx2
import pytest

import openai._legacy_response as _legacy_response
from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from tests.respx2 import MockRouter
from openai.types.live import (
    SessionForkResponse,
)

# pyright: reportDeprecated=false

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSessions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_accept(self, client: OpenAI) -> None:
        session = client.live.sessions.accept(
            session_id="session_id",
            session={
                "model": "gpt-live-1",
                "type": "live",
            },
        )
        assert session is None

    @parametrize
    def test_method_accept_with_all_params(self, client: OpenAI) -> None:
        session = client.live.sessions.accept(
            session_id="session_id",
            session={
                "model": "x",
                "type": "live",
                "audio": {"output": {"voice": "alloy"}},
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
        )
        assert session is None

    @parametrize
    def test_raw_response_accept(self, client: OpenAI) -> None:
        response = client.live.sessions.with_raw_response.accept(
            session_id="session_id",
            session={
                "model": "gpt-live-1",
                "type": "live",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert session is None

    @parametrize
    def test_streaming_response_accept(self, client: OpenAI) -> None:
        with client.live.sessions.with_streaming_response.accept(
            session_id="session_id",
            session={
                "model": "gpt-live-1",
                "type": "live",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert session is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_accept(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.live.sessions.with_raw_response.accept(
                session_id="",
                session={
                    "model": "gpt-live-1",
                    "type": "live",
                },
            )

    @parametrize
    @pytest.mark.respx2(base_url=base_url)
    def test_method_download_recording(self, client: OpenAI, respx2_mock: MockRouter) -> None:
        respx2_mock.get("/live/sessions/live_SQ/content").mock(return_value=httpx2.Response(200, json={"foo": "bar"}))
        session = client.live.sessions.download_recording(
            "live_SQ",
        )
        assert isinstance(session, _legacy_response.HttpxBinaryResponseContent)
        assert session.json() == {"foo": "bar"}

    @parametrize
    @pytest.mark.respx2(base_url=base_url)
    def test_raw_response_download_recording(self, client: OpenAI, respx2_mock: MockRouter) -> None:
        respx2_mock.get("/live/sessions/live_SQ/content").mock(return_value=httpx2.Response(200, json={"foo": "bar"}))

        response = client.live.sessions.with_raw_response.download_recording(
            "live_SQ",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(_legacy_response.HttpxBinaryResponseContent, session, path=["response"])

    @parametrize
    @pytest.mark.respx2(base_url=base_url)
    def test_streaming_response_download_recording(self, client: OpenAI, respx2_mock: MockRouter) -> None:
        respx2_mock.get("/live/sessions/live_SQ/content").mock(return_value=httpx2.Response(200, json={"foo": "bar"}))
        with client.live.sessions.with_streaming_response.download_recording(
            "live_SQ",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(bytes, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    @pytest.mark.respx2(base_url=base_url)
    def test_path_params_download_recording(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.live.sessions.with_raw_response.download_recording(
                "",
            )

    @parametrize
    def test_method_fork(self, client: OpenAI) -> None:
        session = client.live.sessions.fork(
            session_id="session_id",
            transport={
                "sdp": "x",
                "type": "webrtc",
            },
        )
        assert_matches_type(SessionForkResponse, session, path=["response"])

    @parametrize
    def test_method_fork_with_all_params(self, client: OpenAI) -> None:
        session = client.live.sessions.fork(
            session_id="session_id",
            transport={
                "sdp": "x",
                "type": "webrtc",
            },
            session={
                "client": {
                    "data_channel": {
                        "allowed_client_events": "all",
                        "allowed_server_events": "all",
                    }
                },
                "delegation": {
                    "type": "responses",
                    "responses": {
                        "instructions": "instructions",
                        "max_output_tokens": 16,
                        "model": "model",
                        "parallel_tool_calls": True,
                        "reasoning": {
                            "effort": "none",
                            "summary": "concise",
                        },
                        "service_tier": "auto",
                        "text": {"verbosity": "low"},
                        "tool_choice": "auto",
                        "tools": [
                            {
                                "name": "name",
                                "type": "function",
                                "description": "description",
                                "parameters": {"foo": "bar"},
                                "strict": True,
                            }
                        ],
                    },
                },
                "store": True,
            },
        )
        assert_matches_type(SessionForkResponse, session, path=["response"])

    @parametrize
    def test_raw_response_fork(self, client: OpenAI) -> None:
        response = client.live.sessions.with_raw_response.fork(
            session_id="session_id",
            transport={
                "sdp": "x",
                "type": "webrtc",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionForkResponse, session, path=["response"])

    @parametrize
    def test_streaming_response_fork(self, client: OpenAI) -> None:
        with client.live.sessions.with_streaming_response.fork(
            session_id="session_id",
            transport={
                "sdp": "x",
                "type": "webrtc",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(SessionForkResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_fork(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.live.sessions.with_raw_response.fork(
                session_id="",
                transport={
                    "sdp": "x",
                    "type": "webrtc",
                },
            )

    @parametrize
    def test_method_hangup(self, client: OpenAI) -> None:
        session = client.live.sessions.hangup(
            "session_id",
        )
        assert session is None

    @parametrize
    def test_raw_response_hangup(self, client: OpenAI) -> None:
        response = client.live.sessions.with_raw_response.hangup(
            "session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert session is None

    @parametrize
    def test_streaming_response_hangup(self, client: OpenAI) -> None:
        with client.live.sessions.with_streaming_response.hangup(
            "session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert session is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_hangup(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.live.sessions.with_raw_response.hangup(
                "",
            )

    @parametrize
    def test_method_refer(self, client: OpenAI) -> None:
        session = client.live.sessions.refer(
            session_id="session_id",
            target_uri="tel:+14155550123",
        )
        assert session is None

    @parametrize
    def test_raw_response_refer(self, client: OpenAI) -> None:
        response = client.live.sessions.with_raw_response.refer(
            session_id="session_id",
            target_uri="tel:+14155550123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert session is None

    @parametrize
    def test_streaming_response_refer(self, client: OpenAI) -> None:
        with client.live.sessions.with_streaming_response.refer(
            session_id="session_id",
            target_uri="tel:+14155550123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert session is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_refer(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.live.sessions.with_raw_response.refer(
                session_id="",
                target_uri="tel:+14155550123",
            )

    @parametrize
    def test_method_reject(self, client: OpenAI) -> None:
        session = client.live.sessions.reject(
            session_id="session_id",
            status_code=486,
        )
        assert session is None

    @parametrize
    def test_raw_response_reject(self, client: OpenAI) -> None:
        response = client.live.sessions.with_raw_response.reject(
            session_id="session_id",
            status_code=486,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert session is None

    @parametrize
    def test_streaming_response_reject(self, client: OpenAI) -> None:
        with client.live.sessions.with_streaming_response.reject(
            session_id="session_id",
            status_code=486,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert session is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_reject(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.live.sessions.with_raw_response.reject(
                session_id="",
                status_code=486,
            )


class TestAsyncSessions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_accept(self, async_client: AsyncOpenAI) -> None:
        session = await async_client.live.sessions.accept(
            session_id="session_id",
            session={
                "model": "gpt-live-1",
                "type": "live",
            },
        )
        assert session is None

    @parametrize
    async def test_method_accept_with_all_params(self, async_client: AsyncOpenAI) -> None:
        session = await async_client.live.sessions.accept(
            session_id="session_id",
            session={
                "model": "x",
                "type": "live",
                "audio": {"output": {"voice": "alloy"}},
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
        )
        assert session is None

    @parametrize
    async def test_raw_response_accept(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.live.sessions.with_raw_response.accept(
            session_id="session_id",
            session={
                "model": "gpt-live-1",
                "type": "live",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert session is None

    @parametrize
    async def test_streaming_response_accept(self, async_client: AsyncOpenAI) -> None:
        async with async_client.live.sessions.with_streaming_response.accept(
            session_id="session_id",
            session={
                "model": "gpt-live-1",
                "type": "live",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert session is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_accept(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.live.sessions.with_raw_response.accept(
                session_id="",
                session={
                    "model": "gpt-live-1",
                    "type": "live",
                },
            )

    @parametrize
    @pytest.mark.respx2(base_url=base_url)
    async def test_method_download_recording(self, async_client: AsyncOpenAI, respx2_mock: MockRouter) -> None:
        respx2_mock.get("/live/sessions/live_SQ/content").mock(return_value=httpx2.Response(200, json={"foo": "bar"}))
        session = await async_client.live.sessions.download_recording(
            "live_SQ",
        )
        assert isinstance(session, _legacy_response.HttpxBinaryResponseContent)
        assert session.json() == {"foo": "bar"}

    @parametrize
    @pytest.mark.respx2(base_url=base_url)
    async def test_raw_response_download_recording(self, async_client: AsyncOpenAI, respx2_mock: MockRouter) -> None:
        respx2_mock.get("/live/sessions/live_SQ/content").mock(return_value=httpx2.Response(200, json={"foo": "bar"}))

        response = await async_client.live.sessions.with_raw_response.download_recording(
            "live_SQ",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(_legacy_response.HttpxBinaryResponseContent, session, path=["response"])

    @parametrize
    @pytest.mark.respx2(base_url=base_url)
    async def test_streaming_response_download_recording(
        self, async_client: AsyncOpenAI, respx2_mock: MockRouter
    ) -> None:
        respx2_mock.get("/live/sessions/live_SQ/content").mock(return_value=httpx2.Response(200, json={"foo": "bar"}))
        async with async_client.live.sessions.with_streaming_response.download_recording(
            "live_SQ",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(bytes, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    @pytest.mark.respx2(base_url=base_url)
    async def test_path_params_download_recording(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.live.sessions.with_raw_response.download_recording(
                "",
            )

    @parametrize
    async def test_method_fork(self, async_client: AsyncOpenAI) -> None:
        session = await async_client.live.sessions.fork(
            session_id="session_id",
            transport={
                "sdp": "x",
                "type": "webrtc",
            },
        )
        assert_matches_type(SessionForkResponse, session, path=["response"])

    @parametrize
    async def test_method_fork_with_all_params(self, async_client: AsyncOpenAI) -> None:
        session = await async_client.live.sessions.fork(
            session_id="session_id",
            transport={
                "sdp": "x",
                "type": "webrtc",
            },
            session={
                "client": {
                    "data_channel": {
                        "allowed_client_events": "all",
                        "allowed_server_events": "all",
                    }
                },
                "delegation": {
                    "type": "responses",
                    "responses": {
                        "instructions": "instructions",
                        "max_output_tokens": 16,
                        "model": "model",
                        "parallel_tool_calls": True,
                        "reasoning": {
                            "effort": "none",
                            "summary": "concise",
                        },
                        "service_tier": "auto",
                        "text": {"verbosity": "low"},
                        "tool_choice": "auto",
                        "tools": [
                            {
                                "name": "name",
                                "type": "function",
                                "description": "description",
                                "parameters": {"foo": "bar"},
                                "strict": True,
                            }
                        ],
                    },
                },
                "store": True,
            },
        )
        assert_matches_type(SessionForkResponse, session, path=["response"])

    @parametrize
    async def test_raw_response_fork(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.live.sessions.with_raw_response.fork(
            session_id="session_id",
            transport={
                "sdp": "x",
                "type": "webrtc",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionForkResponse, session, path=["response"])

    @parametrize
    async def test_streaming_response_fork(self, async_client: AsyncOpenAI) -> None:
        async with async_client.live.sessions.with_streaming_response.fork(
            session_id="session_id",
            transport={
                "sdp": "x",
                "type": "webrtc",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(SessionForkResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_fork(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.live.sessions.with_raw_response.fork(
                session_id="",
                transport={
                    "sdp": "x",
                    "type": "webrtc",
                },
            )

    @parametrize
    async def test_method_hangup(self, async_client: AsyncOpenAI) -> None:
        session = await async_client.live.sessions.hangup(
            "session_id",
        )
        assert session is None

    @parametrize
    async def test_raw_response_hangup(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.live.sessions.with_raw_response.hangup(
            "session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert session is None

    @parametrize
    async def test_streaming_response_hangup(self, async_client: AsyncOpenAI) -> None:
        async with async_client.live.sessions.with_streaming_response.hangup(
            "session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert session is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_hangup(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.live.sessions.with_raw_response.hangup(
                "",
            )

    @parametrize
    async def test_method_refer(self, async_client: AsyncOpenAI) -> None:
        session = await async_client.live.sessions.refer(
            session_id="session_id",
            target_uri="tel:+14155550123",
        )
        assert session is None

    @parametrize
    async def test_raw_response_refer(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.live.sessions.with_raw_response.refer(
            session_id="session_id",
            target_uri="tel:+14155550123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert session is None

    @parametrize
    async def test_streaming_response_refer(self, async_client: AsyncOpenAI) -> None:
        async with async_client.live.sessions.with_streaming_response.refer(
            session_id="session_id",
            target_uri="tel:+14155550123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert session is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_refer(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.live.sessions.with_raw_response.refer(
                session_id="",
                target_uri="tel:+14155550123",
            )

    @parametrize
    async def test_method_reject(self, async_client: AsyncOpenAI) -> None:
        session = await async_client.live.sessions.reject(
            session_id="session_id",
            status_code=486,
        )
        assert session is None

    @parametrize
    async def test_raw_response_reject(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.live.sessions.with_raw_response.reject(
            session_id="session_id",
            status_code=486,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert session is None

    @parametrize
    async def test_streaming_response_reject(self, async_client: AsyncOpenAI) -> None:
        async with async_client.live.sessions.with_streaming_response.reject(
            session_id="session_id",
            status_code=486,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert session is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_reject(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.live.sessions.with_raw_response.reject(
                session_id="",
                status_code=486,
            )
