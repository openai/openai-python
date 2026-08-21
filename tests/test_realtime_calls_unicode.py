from __future__ import annotations

import httpx2
import pytest

import openai._legacy_response as _legacy_response
from openai import OpenAI, AsyncOpenAI
from tests.respx2 import MockRouter


class TestRealtimeCallsUnicode:
    @pytest.mark.respx2(base_url="http://127.0.0.1:4010")
    def test_realtime_create_unicode_session_not_escaped(self, client: OpenAI, respx2_mock: MockRouter) -> None:
        captured_requests: list[httpx2.Request] = []

        def side_effect(request: httpx2.Request) -> httpx2.Response:
            captured_requests.append(request)
            return httpx2.Response(200, json={"id": "call_123"})

        respx2_mock.post("/realtime/calls").mock(side_effect=side_effect)

        unicode_instructions = "Привет мир! 你好世界 こんにちは"
        call = client.realtime.calls.create(
            sdp="v=0\r\no=- 0 0 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\n",
            session={
                "type": "realtime",
                "instructions": unicode_instructions,
            },
        )
        assert isinstance(call, _legacy_response.HttpxBinaryResponseContent)
        assert len(captured_requests) == 1

        body_bytes = captured_requests[0].content
        # Ensure the Unicode string is present directly as UTF-8 bytes, not \uXXXX escaped
        assert unicode_instructions.encode("utf-8") in body_bytes
        # Ensure it's not escaped
        assert b"\\u041f\\u0440\\u0438" not in body_bytes

    @pytest.mark.asyncio
    @pytest.mark.respx2(base_url="http://127.0.0.1:4010")
    async def test_async_realtime_create_unicode_session_not_escaped(
        self, async_client: AsyncOpenAI, respx2_mock: MockRouter
    ) -> None:
        captured_requests: list[httpx2.Request] = []

        def side_effect(request: httpx2.Request) -> httpx2.Response:
            captured_requests.append(request)
            return httpx2.Response(200, json={"id": "call_123"})

        respx2_mock.post("/realtime/calls").mock(side_effect=side_effect)

        unicode_instructions = "Привет мир! 你好世界 こんにちは"
        call = await async_client.realtime.calls.create(
            sdp="v=0\r\no=- 0 0 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\n",
            session={
                "type": "realtime",
                "instructions": unicode_instructions,
            },
        )
        assert isinstance(call, _legacy_response.HttpxBinaryResponseContent)
        assert len(captured_requests) == 1

        body_bytes = captured_requests[0].content
        # Ensure the Unicode string is present directly as UTF-8 bytes, not \uXXXX escaped
        assert unicode_instructions.encode("utf-8") in body_bytes
        assert b"\\u041f\\u0440\\u0438" not in body_bytes
