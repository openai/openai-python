from __future__ import annotations

import asyncio
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
    realtime = connection_type is RealtimeConnection

    def failing_send(data: str) -> None:
        nonlocal attempts
        assert data == ("b" if realtime and attempts == 1 else "aaa")
        if attempts == 0:
            q.enqueue("b")
        attempts += 1
        if not realtime or attempts == 1:
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
        max_retries=3,
    )
    for expected_attempts in range(1, 4):
        assert connection._reconnect(RuntimeError("fake disconnect"))
        assert q._bytes == ((1 if expected_attempts == 1 else 0) if realtime else 4)
        assert attempts == (min(expected_attempts, 2) if realtime else expected_attempts)
    assert not connection._reconnect(RuntimeError("fake disconnect"))
    assert attempts == (2 if realtime else 3)

    # A healthy application event resets the budget; an upgrade alone does not.
    ws.recv.return_value = '{"type": "response.created"}'
    connection.recv()

    sent: list[str] = []
    ws.send.side_effect = sent.append
    assert connection._reconnect(RuntimeError("fake disconnect"))
    assert sent == ([] if realtime else ["aaa", "b"])
    assert q._bytes == 0
    for _ in range(2):
        assert connection._reconnect(RuntimeError("fake disconnect"))
    assert not connection._reconnect(RuntimeError("retry budget exhausted"))


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
    realtime = connection_type is AsyncRealtimeConnection

    async def failing_send(data: str) -> None:
        nonlocal attempts
        assert data == ("b" if realtime and attempts == 1 else "aaa")
        if attempts == 0:
            q.enqueue("b")
        attempts += 1
        if not realtime or attempts == 1:
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
        max_retries=3,
    )
    for expected_attempts in range(1, 4):
        assert await connection._reconnect(RuntimeError("fake disconnect"))
        assert q._bytes == ((1 if expected_attempts == 1 else 0) if realtime else 4)
        assert attempts == (min(expected_attempts, 2) if realtime else expected_attempts)
    assert not await connection._reconnect(RuntimeError("fake disconnect"))
    assert attempts == (2 if realtime else 3)

    # A healthy application event resets the budget; an upgrade alone does not.
    ws.recv = AsyncMock(return_value='{"type": "response.created"}')
    await connection.recv()

    sent: list[str] = []
    ws.send.side_effect = sent.append
    assert await connection._reconnect(RuntimeError("fake disconnect"))
    assert sent == ([] if realtime else ["aaa", "b"])
    assert q._bytes == 0
    for _ in range(2):
        assert await connection._reconnect(RuntimeError("fake disconnect"))
    assert not await connection._reconnect(RuntimeError("retry budget exhausted"))


@pytest.mark.asyncio
async def test_cancelled_realtime_flush_does_not_replay_active_send() -> None:
    q = SendQueue(max_bytes=4)
    q.enqueue("é")
    q.enqueue("b")
    active = asyncio.Event()
    socket = MagicMock()

    async def suspended_send(data: str) -> None:
        assert data == "é"
        active.set()
        await asyncio.Event().wait()

    socket.send = AsyncMock(side_effect=suspended_send)
    connection = AsyncRealtimeConnection(socket, send_queue=q)
    task = asyncio.create_task(connection._flush_send_queue())
    try:
        await asyncio.wait_for(active.wait(), 5)
        q.enqueue("c")
        with pytest.raises(WebSocketQueueFullError):
            q.enqueue("d")
    finally:
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    # Only the active send was attempted; its bytes are released, and the
    # queued tail and concurrent enqueue remain in order for the next socket.
    q.enqueue("dd")
    sent: list[str] = []
    socket.send.side_effect = sent.append
    await connection._flush_send_queue()
    assert sent == ["b", "c", "dd"]
    q.enqueue("1234")
