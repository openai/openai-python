"""Opt-in live helper smoke tests. Credentials are read only from the environment.

Run with OPENAI_WEBSOCKET_LIVE_TEST=1 and OPENAI_API_KEY configured. Optionally
choose a Responses model with OPENAI_WEBSOCKET_TEST_MODEL.
"""

from __future__ import annotations

import os
import asyncio

import pytest

from openai import OpenAI, AsyncOpenAI
from openai.lib.responses_websocket import (
    ResponsesWebSocketLimits,
    ResponsesWebSocketSession,
    AsyncResponsesWebSocketSession,
)

pytestmark = pytest.mark.skipif(
    os.environ.get("OPENAI_WEBSOCKET_LIVE_TEST") != "1" or not os.environ.get("OPENAI_API_KEY"),
    reason="Live Responses WebSocket tests require explicit opt-in and environment credentials",
)

LIMITS = ResponsesWebSocketLimits(
    max_lanes=4,
    max_events_per_lane=128,
    max_events=256,
    max_bytes_per_lane=8 * 1024 * 1024,
    max_bytes=16 * 1024 * 1024,
    max_response_bytes=16 * 1024 * 1024,
)


def test_live_sync_session_continuation() -> None:
    model = os.environ.get("OPENAI_WEBSOCKET_TEST_MODEL", "gpt-4o-mini")
    with (
        OpenAI(default_headers={"X-SDK-Header-Test": "client"}) as client,
        client.responses.connect(extra_headers={"X-SDK-Header-Test": "connection"}) as connection,
        ResponsesWebSocketSession(connection, limits=LIMITS) as session,
    ):
        lane = session.lane("sdk-live-sync")
        lane.send({"type": "response.create", "model": model, "input": "Reply with exactly OK.", "store": False})
        first = lane.get_final_response(timeout=60)
        assert first.status == "completed"
        assert first.output_text
        lane.send(
            {
                "type": "response.create",
                "model": model,
                "previous_response_id": first.id,
                "input": "Reply with exactly OK again.",
                "store": False,
            }
        )
        second = lane.get_final_response(timeout=60)
        assert second.status == "completed"
        assert second.id != first.id
        assert second.output_text


async def test_live_async_session_continuation() -> None:
    model = os.environ.get("OPENAI_WEBSOCKET_TEST_MODEL", "gpt-4o-mini")
    async with (
        AsyncOpenAI(default_headers={"X-SDK-Header-Test": "client"}) as client,
        client.responses.connect(extra_headers={"X-SDK-Header-Test": "connection"}) as connection,
        AsyncResponsesWebSocketSession(connection, limits=LIMITS) as session,
    ):
        lane = session.lane("sdk-live-async")
        await lane.send({"type": "response.create", "model": model, "input": "Reply with exactly OK.", "store": False})
        first = await asyncio.wait_for(lane.get_final_response(), timeout=60)
        assert first.status == "completed"
        assert first.output_text
        await lane.send(
            {
                "type": "response.create",
                "model": model,
                "previous_response_id": first.id,
                "input": "Reply with exactly OK again.",
                "store": False,
            }
        )
        second = await asyncio.wait_for(lane.get_final_response(), timeout=60)
        assert second.status == "completed"
        assert second.id != first.id
        assert second.output_text
