from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from openai._exceptions import WebSocketQueueFullError
from openai._send_queue import SendQueue
from openai.resources.realtime.realtime import RealtimeConnection, AsyncRealtimeConnection
from openai.resources.responses.responses import ResponsesConnection, AsyncResponsesConnection
from openai.resources.beta.responses.responses import (
    ResponsesConnection as BetaResponsesConnection,
    AsyncResponsesConnection as AsyncBetaResponsesConnection,
)


@pytest.mark.parametrize("connection_type", [RealtimeConnection, ResponsesConnection, BetaResponsesConnection])
def test_reconnect_retries_bounded_send_queue(
    connection_type: type[RealtimeConnection] | type[ResponsesConnection] | type[BetaResponsesConnection],
) -> None:
    q = SendQueue(max_bytes=4)
    q.enqueue("aaa")
    ws = MagicMock()
    attempts = 0

    def failing_send(data: str) -> None:
        nonlocal attempts
        assert data == "aaa"
        if attempts == 0:
            q.enqueue("b")
        attempts += 1
        with pytest.raises(WebSocketQueueFullError):
            q.enqueue("c")
        raise RuntimeError("fake send failure")

    ws.send.side_effect = failing_send
    connection = connection_type(
        ws,
        send_queue=q,
        make_ws=MagicMock(return_value=ws),
        on_reconnecting=lambda _event: None,
        initial_delay=0,
        max_retries=1,
    )
    for _ in range(3):
        assert connection._reconnect(RuntimeError("fake disconnect"))
        assert q._bytes == 4
    assert attempts == 3

    sent: list[str] = []
    ws.send.side_effect = sent.append
    assert connection._reconnect(RuntimeError("fake disconnect"))
    assert sent == ["aaa", "b"]
    assert q._bytes == 0


@pytest.mark.parametrize(
    "connection_type", [AsyncRealtimeConnection, AsyncResponsesConnection, AsyncBetaResponsesConnection]
)
@pytest.mark.asyncio
async def test_async_reconnect_retries_bounded_send_queue(
    connection_type: type[AsyncRealtimeConnection]
    | type[AsyncResponsesConnection]
    | type[AsyncBetaResponsesConnection],
) -> None:
    q = SendQueue(max_bytes=4)
    q.enqueue("aaa")
    ws = MagicMock()
    attempts = 0

    async def failing_send(data: str) -> None:
        nonlocal attempts
        assert data == "aaa"
        if attempts == 0:
            q.enqueue("b")
        attempts += 1
        with pytest.raises(WebSocketQueueFullError):
            q.enqueue("c")
        raise RuntimeError("fake send failure")

    ws.send = AsyncMock(side_effect=failing_send)
    connection = connection_type(
        ws,
        send_queue=q,
        make_ws=AsyncMock(return_value=ws),
        on_reconnecting=lambda _event: None,
        initial_delay=0,
        max_retries=1,
    )
    for _ in range(3):
        assert await connection._reconnect(RuntimeError("fake disconnect"))
        assert q._bytes == 4
    assert attempts == 3

    sent: list[str] = []
    ws.send.side_effect = sent.append
    assert await connection._reconnect(RuntimeError("fake disconnect"))
    assert sent == ["aaa", "b"]
    assert q._bytes == 0
