from __future__ import annotations

import json
import asyncio
import threading
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import httpx2
import pytest
from websockets.frames import Close
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

from openai import OpenAI, AsyncOpenAI
from openai._exceptions import WebSocketQueueFullError, WebSocketConnectionClosedError
from openai._send_queue import SendQueue
from openai.resources.live.live import LiveConnection, AsyncLiveConnection
from openai.resources.live.forks import ForksConnection, AsyncForksConnection
from openai.lib.responses_websocket import (
    ResponsesWebSocketLimits,
    ResponsesWebSocketSession,
    AsyncResponsesWebSocketSession,
)
from openai.resources.live.sideband import SidebandConnection, AsyncSidebandConnection
from openai.resources.realtime.realtime import RealtimeConnection, AsyncRealtimeConnection
from openai.resources.responses.responses import ResponsesConnection, AsyncResponsesConnection
from openai.resources.beta.responses.responses import (
    ResponsesConnection as BetaResponsesConnection,
    AsyncResponsesConnection as AsyncBetaResponsesConnection,
)
from openai.resources.realtime.translations.translations import TranslationsConnection, AsyncTranslationsConnection

from .lib.test_websocket_redirects import (
    RECONNECTING_RESOURCES,
    options,
    resource,
    unexpected_http,
    async_http_client,
)

SYNC_BINDINGS = [
    RealtimeConnection,
    ResponsesConnection,
    BetaResponsesConnection,
    LiveConnection,
    SidebandConnection,
    ForksConnection,
    TranslationsConnection,
]
ASYNC_BINDINGS = [
    AsyncRealtimeConnection,
    AsyncResponsesConnection,
    AsyncBetaResponsesConnection,
    AsyncLiveConnection,
    AsyncSidebandConnection,
    AsyncForksConnection,
    AsyncTranslationsConnection,
]
ERROR = b'{"type":"error","event_id":"fake-id","error":{"type":"fixture","message":"fake message"}}'


def closed(code: int) -> ConnectionClosedOK | ConnectionClosedError:
    if code == 1006:
        # 1006 denotes loss without a close frame; it is never sent on the wire.
        return ConnectionClosedError(None, None)
    frame = Close(code, "")
    kind = ConnectionClosedOK if code in (1000, 1001, 1005) else ConnectionClosedError
    return kind(frame, frame, True)


@pytest.mark.parametrize("code", [1000, 1001, 1005, 1011])
def test_sync_session_reports_unsent_after_failed_clean_recovery(code: int) -> None:
    socket = MagicMock()
    socket.recv.side_effect = closed(code)

    def failed_handshake(*_args: Any) -> Any:
        conn.send_raw("queued-during-recovery")
        raise OSError("synthetic failed handshake")

    conn = ResponsesConnection(
        socket, make_ws=failed_handshake, on_reconnecting=lambda _: None, max_retries=1, initial_delay=0
    )
    limits = ResponsesWebSocketLimits(1, 4, 4, 4096, 4096)
    with ResponsesWebSocketSession(conn, limits=limits) as session:
        if code == 1000:
            with pytest.raises(EOFError):
                session.default.recv(timeout=3)
        else:
            with pytest.raises(WebSocketConnectionClosedError) as caught:
                session.default.recv(timeout=3)
            assert caught.value.unsent_messages == ["queued-during-recovery"]
    assert conn._send_queue.drain() == []
    socket.send.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("code", [1000, 1001, 1005, 1011])
async def test_async_session_reports_unsent_after_failed_clean_recovery(code: int) -> None:
    socket = MagicMock()
    socket.recv = AsyncMock(side_effect=closed(code))
    socket.close = AsyncMock()

    async def failed_handshake(*_args: Any) -> Any:
        await conn.send_raw("queued-during-recovery")
        raise OSError("synthetic failed handshake")

    conn = AsyncResponsesConnection(
        socket, make_ws=failed_handshake, on_reconnecting=lambda _: None, max_retries=1, initial_delay=0
    )
    limits = ResponsesWebSocketLimits(1, 4, 4, 4096, 4096)
    async with AsyncResponsesWebSocketSession(conn, limits=limits) as session:
        if code == 1000:
            with pytest.raises(EOFError):
                await asyncio.wait_for(session.default.recv(), 3)
        else:
            with pytest.raises(WebSocketConnectionClosedError) as caught:
                await asyncio.wait_for(session.default.recv(), 3)
            assert caught.value.unsent_messages == ["queued-during-recovery"]
    assert conn._send_queue.drain() == []
    socket.send.assert_not_called()


@pytest.mark.parametrize("connection_type", SYNC_BINDINGS)
@pytest.mark.parametrize("code,expected", [(1000, []), (1001, [1001]), (1005, [1005]), (1012, [1012])])
def test_received_close_policy_on_sync_iterator(connection_type: type[Any], code: int, expected: list[int]) -> None:
    original, replacement = MagicMock(), MagicMock()
    original.recv.side_effect = closed(code)
    replacement.recv.side_effect = [ERROR, closed(1000)]
    seen: list[int] = []
    conn = connection_type(
        original,
        make_ws=lambda *_: replacement,
        on_reconnecting=lambda e: seen.append(e.close_code),
        initial_delay=0,
    )
    events = list(conn)
    assert seen == expected
    assert [e.type for e in events] == (["error"] if expected else [])


@pytest.mark.asyncio
@pytest.mark.parametrize("connection_type", ASYNC_BINDINGS)
@pytest.mark.parametrize("code,expected", [(1000, []), (1001, [1001]), (1005, [1005]), (1012, [1012])])
async def test_received_close_policy_on_async_iterator(
    connection_type: type[Any], code: int, expected: list[int]
) -> None:
    original, replacement = MagicMock(), MagicMock()
    original.recv = AsyncMock(side_effect=closed(code))
    replacement.recv = AsyncMock(side_effect=[ERROR, closed(1000)])
    seen: list[int] = []
    conn = connection_type(
        original,
        make_ws=AsyncMock(return_value=replacement),
        on_reconnecting=lambda e: seen.append(e.close_code),
        initial_delay=0,
    )
    events = [e async for e in conn]
    assert seen == expected
    assert [e.type for e in events] == (["error"] if expected else [])


def register_handlers(conn: Any, mode: str, seen: list[str]) -> None:
    def handler(event: Any) -> None:
        seen.append(event.type)

    # The generic no-op leaves an error consumer after the off+once case ends.
    conn.on("event", lambda _e: None)
    if mode == "same":
        conn.on("error", handler)
        conn.once("error", handler)
    elif mode == "different":
        conn.on("event", handler)
        conn.once("error", handler)
    else:
        conn.on("error", handler)
        conn.once("error", handler)
        conn.off("error", handler)


@pytest.mark.parametrize("connection_type", SYNC_BINDINGS)
@pytest.mark.parametrize("mode,count", [("same", 3), ("different", 3), ("off", 1)])
def test_sync_dispatch_keeps_each_registration(connection_type: type[Any], mode: str, count: int) -> None:
    socket = MagicMock()
    socket.recv.side_effect = [ERROR, ERROR, closed(1000)]
    conn = connection_type(socket)
    seen: list[str] = []
    register_handlers(conn, mode, seen)
    conn.dispatch_events()
    assert seen == ["error"] * count


@pytest.mark.asyncio
@pytest.mark.parametrize("connection_type", ASYNC_BINDINGS)
@pytest.mark.parametrize("mode,count", [("same", 3), ("different", 3), ("off", 1)])
async def test_async_dispatch_keeps_each_registration(connection_type: type[Any], mode: str, count: int) -> None:
    socket = MagicMock()
    socket.recv = AsyncMock(side_effect=[ERROR, ERROR, closed(1000)])
    conn = connection_type(socket)
    seen: list[str] = []
    register_handlers(conn, mode, seen)
    await conn.dispatch_events()
    assert seen == ["error"] * count


@pytest.mark.parametrize("connection_type", SYNC_BINDINGS)
@pytest.mark.parametrize("typed", [False, True], ids=["raw", "typed"])
def test_sync_flush_admits_writes_in_order(connection_type: type[Any], typed: bool) -> None:
    entered, release, closed_socket = threading.Event(), threading.Event(), threading.Event()
    sent: list[str | bytes] = []
    queue = SendQueue(max_bytes=80)
    queue.enqueue("old-1")
    queue.enqueue("old-2")
    original, replacement = MagicMock(), MagicMock()

    def send(data: str | bytes) -> None:
        sent.append(data)
        if data == "old-1":
            entered.set()
            assert release.wait(3), "test failed to release blocked write"

    replacement.send.side_effect = send
    replacement.close.side_effect = lambda **_kwargs: closed_socket.set()
    conn = connection_type(
        original, send_queue=queue, make_ws=lambda *_: replacement, on_reconnecting=lambda _: None, initial_delay=0
    )
    recovered: list[bool] = []
    worker = threading.Thread(target=lambda: recovered.append(conn._reconnect(closed(1012))))
    worker.start()
    try:
        assert entered.wait(3)
        if typed:
            conn.send({"type": "response.create"})
            last = json.dumps({"type": "response.create"})
        else:
            conn.send_raw("new-3")
            last = "new-3"
        with pytest.raises(WebSocketQueueFullError):
            conn.send_raw("x" * 80)
        assert sent == ["old-1"]
    finally:
        release.set()
        worker.join(3)
    assert not worker.is_alive()
    assert recovered == [True]
    assert sent == ["old-1", "old-2", last]
    conn.close()
    assert closed_socket.is_set()


@pytest.mark.asyncio
@pytest.mark.parametrize("connection_type", ASYNC_BINDINGS)
@pytest.mark.parametrize("typed", [False, True], ids=["raw", "typed"])
async def test_async_flush_admits_writes_in_order(connection_type: type[Any], typed: bool) -> None:
    entered, release = asyncio.Event(), asyncio.Event()
    sent: list[str | bytes] = []
    queue = SendQueue(max_bytes=80)
    queue.enqueue("old-1")
    queue.enqueue("old-2")
    original, replacement = MagicMock(), MagicMock()

    async def send(data: str | bytes) -> None:
        sent.append(data)
        if data == "old-1":
            entered.set()
            await release.wait()

    replacement.send = AsyncMock(side_effect=send)
    conn = connection_type(
        original,
        send_queue=queue,
        make_ws=AsyncMock(return_value=replacement),
        on_reconnecting=lambda _: None,
        initial_delay=0,
    )
    worker = asyncio.create_task(conn._reconnect(closed(1012)))
    try:
        await asyncio.wait_for(entered.wait(), 3)
        if typed:
            await conn.send({"type": "response.create"})
            last = json.dumps({"type": "response.create"})
        else:
            await conn.send_raw("new-3")
            last = "new-3"
        with pytest.raises(WebSocketQueueFullError):
            await conn.send_raw("x" * 80)
        assert sent == ["old-1"]
    finally:
        release.set()
        result = await asyncio.wait_for(worker, 3)
    assert result
    assert sent == ["old-1", "old-2", last]


def test_sync_close_interrupts_a_blocked_flush() -> None:
    entered, socket_closed = threading.Event(), threading.Event()
    socket = MagicMock()
    attempted: list[str | bytes] = []
    queue = SendQueue()
    queue.enqueue("attempted")
    queue.enqueue("never attempted")

    def send(data: str | bytes) -> None:
        attempted.append(data)
        entered.set()
        assert socket_closed.wait(3), "close must not wait for network send"
        raise RuntimeError("fixture: transport closed")

    socket.send.side_effect = send
    socket.close.side_effect = lambda **_: socket_closed.set()
    conn = RealtimeConnection(
        socket, send_queue=queue, make_ws=lambda *_: socket, on_reconnecting=lambda _: None, initial_delay=0
    )
    worker = threading.Thread(target=lambda: conn._reconnect(closed(1012)))
    worker.start()
    try:
        assert entered.wait(3)
        conn.close()
        assert socket_closed.is_set()
    finally:
        socket_closed.set()
        worker.join(3)
    assert not worker.is_alive()
    assert attempted == ["attempted"]
    assert queue.drain() == ["never attempted"]


@pytest.mark.parametrize("connection_type", SYNC_BINDINGS)
@pytest.mark.parametrize(
    "failure,expected_codes",
    [(None, [1012, 1012]), (1000, [1012]), (1006, [1012, 1006]), (1008, [1012]), (1013, [1012, 1013])],
)
@pytest.mark.parametrize("budget", [1, 2])
def test_sync_failed_recovery_flush_keeps_unsent_order(
    connection_type: type[Any], failure: int | None, expected_codes: list[int], budget: int
) -> None:
    original, failed, working = MagicMock(), MagicMock(), MagicMock()
    initial_close = closed(1012)
    original.recv.side_effect = initial_close
    failed.recv.return_value = ERROR
    working.recv.return_value = ERROR
    queue = SendQueue()
    queue.enqueue("attempted")
    queue.enqueue("earlier")
    entered, release = threading.Event(), threading.Event()
    attempts: list[str | bytes] = []
    codes: list[int] = []

    def send(data: str | bytes) -> None:
        attempts.append(data)
        entered.set()
        assert release.wait(3)
        if failure is not None:
            raise closed(failure)
        raise OSError("synthetic write failure")

    failed.send.side_effect = send
    working.send.side_effect = attempts.append
    conn = connection_type(
        original,
        send_queue=queue,
        make_ws=MagicMock(side_effect=[failed, working]),
        on_reconnecting=lambda e: codes.append(e.close_code),
        initial_delay=0,
        max_retries=budget,
    )
    events: list[Any] = []
    errors: list[WebSocketConnectionClosedError] = []

    def read() -> None:
        try:
            events.append(next(iter(conn)))
        except WebSocketConnectionClosedError as exc:
            errors.append(exc)

    worker = threading.Thread(target=read)
    worker.start()
    try:
        assert entered.wait(3)
        conn.send_raw(b"\xfflater")
    finally:
        release.set()
        worker.join(3)
    assert not worker.is_alive()
    assert codes == expected_codes[:budget]
    failed.recv.assert_not_called()
    failed.close.assert_called_once()
    if len(codes) == 2:
        assert [event.type for event in events] == ["error"]
        assert not errors
        assert attempts == ["attempted", "earlier", b"\xfflater"]
    else:
        assert not events
        assert len(errors) == 1
        assert errors[0].unsent_frames == ["earlier", b"\xfflater"]
        assert errors[0].__cause__ is initial_close
        assert attempts == ["attempted"]
    assert queue.drain() == []


@pytest.mark.asyncio
@pytest.mark.parametrize("connection_type", ASYNC_BINDINGS)
@pytest.mark.parametrize(
    "failure,expected_codes",
    [(None, [1012, 1012]), (1000, [1012]), (1006, [1012, 1006]), (1008, [1012]), (1013, [1012, 1013])],
)
@pytest.mark.parametrize("budget", [1, 2])
async def test_async_failed_recovery_flush_keeps_unsent_order(
    connection_type: type[Any], failure: int | None, expected_codes: list[int], budget: int
) -> None:
    original, failed, working = MagicMock(), MagicMock(), MagicMock()
    initial_close = closed(1012)
    original.recv = AsyncMock(side_effect=initial_close)
    failed.recv = AsyncMock(return_value=ERROR)
    failed.close = AsyncMock()
    working.recv = AsyncMock(return_value=ERROR)
    working.close = AsyncMock()
    queue = SendQueue()
    queue.enqueue("attempted")
    queue.enqueue("earlier")
    entered, release = asyncio.Event(), asyncio.Event()
    attempts: list[str | bytes] = []
    codes: list[int] = []

    async def send(data: str | bytes) -> None:
        attempts.append(data)
        entered.set()
        await release.wait()
        if failure is not None:
            raise closed(failure)
        raise OSError("synthetic write failure")

    failed.send = AsyncMock(side_effect=send)
    working.send = AsyncMock(side_effect=attempts.append)
    conn = connection_type(
        original,
        send_queue=queue,
        make_ws=AsyncMock(side_effect=[failed, working]),
        on_reconnecting=lambda e: codes.append(e.close_code),
        initial_delay=0,
        max_retries=budget,
    )
    worker = asyncio.create_task(anext(aiter(conn)))
    await asyncio.wait_for(entered.wait(), 3)
    try:
        await conn.send_raw(b"\xfflater")
    finally:
        release.set()
    if len(expected_codes) > 1 and budget > 1:
        event = await asyncio.wait_for(worker, 3)
        assert event.type == "error"
        assert attempts == ["attempted", "earlier", b"\xfflater"]
    else:
        with pytest.raises(WebSocketConnectionClosedError) as caught:
            await asyncio.wait_for(worker, 3)
        assert caught.value.unsent_frames == ["earlier", b"\xfflater"]
        assert caught.value.__cause__ is initial_close
        assert attempts == ["attempted"]
    assert codes == expected_codes[:budget]
    failed.recv.assert_not_called()
    failed.close.assert_awaited_once()
    assert queue.drain() == []


@pytest.mark.parametrize("connection_type", SYNC_BINDINGS)
def test_sync_non_recovery_flush_preserves_entry_failure_behavior(connection_type: type[Any]) -> None:
    queue = SendQueue()
    queue.enqueue("attempted")
    queue.enqueue("remaining")
    socket = MagicMock()
    socket.send.side_effect = OSError("synthetic entry failure")
    conn = connection_type(socket, send_queue=queue)
    conn._flush_send_queue()
    assert queue.drain() == ["remaining"]
    socket.close.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("connection_type", ASYNC_BINDINGS)
async def test_async_non_recovery_flush_preserves_entry_failure_behavior(connection_type: type[Any]) -> None:
    queue = SendQueue()
    queue.enqueue("attempted")
    queue.enqueue("remaining")
    socket = MagicMock()
    socket.send = AsyncMock(side_effect=OSError("synthetic entry failure"))
    socket.close = AsyncMock()
    conn = connection_type(socket, send_queue=queue)
    await conn._flush_send_queue()
    assert queue.drain() == ["remaining"]
    socket.close.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("connection_type", ASYNC_BINDINGS)
async def test_cancelled_recovery_flush_does_not_retry(connection_type: type[Any]) -> None:
    original, replacement = MagicMock(), MagicMock()
    original.recv = AsyncMock(side_effect=closed(1012))
    replacement.close = AsyncMock()
    entered = asyncio.Event()
    queue = SendQueue()
    queue.enqueue("attempted")
    queue.enqueue("remaining")

    async def blocked_send(_data: str | bytes) -> None:
        entered.set()
        await asyncio.Event().wait()

    replacement.send = AsyncMock(side_effect=blocked_send)
    handshakes = AsyncMock(return_value=replacement)
    conn = connection_type(
        original,
        send_queue=queue,
        make_ws=handshakes,
        on_reconnecting=lambda _: None,
        initial_delay=0,
    )
    reader = asyncio.create_task(anext(aiter(conn)))
    await asyncio.wait_for(entered.wait(), 3)
    await conn.send_raw("later")
    reader.cancel()
    with pytest.raises(asyncio.CancelledError):
        await reader
    handshakes.assert_awaited_once()
    assert queue.drain() == ["remaining", "later"]
    await conn.close()
    replacement.close.assert_awaited_once()


@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
@pytest.mark.parametrize("mode,count", [("same", 3), ("different", 3), ("off", 1)])
def test_sync_manager_transfers_per_registration_flags(
    monkeypatch: pytest.MonkeyPatch, name: str, mode: str, count: int
) -> None:
    socket = MagicMock()
    socket.recv.side_effect = [ERROR, ERROR, closed(1000)]
    monkeypatch.setattr("websockets.sync.client.connect", MagicMock(return_value=socket))
    with OpenAI(
        api_key="fake-key",
        websocket_base_url="wss://origin.test",
        http_client=httpx2.Client(transport=httpx2.MockTransport(unexpected_http)),
    ) as client:
        manager = resource(client, name).connect(**options(client, name))
        seen: list[str] = []
        register_handlers(manager, mode, seen)
        with manager as conn:
            conn.dispatch_events()
        assert seen == ["error"] * count


@pytest.mark.asyncio
@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
@pytest.mark.parametrize("mode,count", [("same", 3), ("different", 3), ("off", 1)])
async def test_async_manager_transfers_per_registration_flags(
    monkeypatch: pytest.MonkeyPatch, name: str, mode: str, count: int
) -> None:
    socket = MagicMock()
    socket.recv = AsyncMock(side_effect=[ERROR, ERROR, closed(1000)])
    socket.close = AsyncMock()
    monkeypatch.setattr("openai.lib._websocket._WebSocketConnect", AsyncMock(return_value=socket))
    async with AsyncOpenAI(
        api_key="fake-key", websocket_base_url="wss://origin.test", http_client=async_http_client()
    ) as client:
        manager = resource(client, name).connect(**options(client, name))
        seen: list[str] = []
        register_handlers(manager, mode, seen)
        async with manager as conn:
            await conn.dispatch_events()
        assert seen == ["error"] * count
