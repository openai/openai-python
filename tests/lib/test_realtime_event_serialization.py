from __future__ import annotations

import json
from unittest.mock import Mock, AsyncMock

import pytest

from openai.resources.realtime.realtime import (
    RealtimeConnection,
    AsyncRealtimeConnection,
)
from openai.resources.beta.realtime.realtime import (
    RealtimeConnection as BetaRealtimeConnection,
    AsyncRealtimeConnection as BetaAsyncRealtimeConnection,
)
from openai.types.realtime.session_update_event import SessionUpdateEvent
from openai.types.beta.realtime.session_update_event import (
    Session as BetaSession,
    SessionUpdateEvent as BetaSessionUpdateEvent,
)
from openai.types.realtime.realtime_session_create_request import RealtimeSessionCreateRequest


def test_sync_realtime_serializes_explicit_default_value() -> None:
    websocket = Mock()
    connection = RealtimeConnection(websocket)
    event = SessionUpdateEvent(
        type="session.update",
        session=RealtimeSessionCreateRequest(type="realtime", instructions=None),
    )

    connection.send(event)

    payload = json.loads(websocket.send.call_args.args[0])
    assert payload["session"]["instructions"] is None
    assert "event_id" not in payload


@pytest.mark.asyncio
async def test_async_realtime_serializes_explicit_default_value() -> None:
    websocket = AsyncMock()
    connection = AsyncRealtimeConnection(websocket)
    event = SessionUpdateEvent(
        type="session.update",
        session=RealtimeSessionCreateRequest(type="realtime", instructions=None),
    )

    await connection.send(event)

    payload = json.loads(websocket.send.call_args.args[0])
    assert payload["session"]["instructions"] is None
    assert "event_id" not in payload


def test_sync_beta_realtime_serializes_explicit_null_turn_detection() -> None:
    websocket = Mock()
    connection = BetaRealtimeConnection(websocket)
    event = BetaSessionUpdateEvent(
        type="session.update",
        session=BetaSession(turn_detection=None),
    )

    connection.send(event)

    payload = json.loads(websocket.send.call_args.args[0])
    assert payload["session"]["turn_detection"] is None
    assert "event_id" not in payload


@pytest.mark.asyncio
async def test_async_beta_realtime_serializes_explicit_null_turn_detection() -> None:
    websocket = AsyncMock()
    connection = BetaAsyncRealtimeConnection(websocket)
    event = BetaSessionUpdateEvent(
        type="session.update",
        session=BetaSession(turn_detection=None),
    )

    await connection.send(event)

    payload = json.loads(websocket.send.call_args.args[0])
    assert payload["session"]["turn_detection"] is None
    assert "event_id" not in payload
