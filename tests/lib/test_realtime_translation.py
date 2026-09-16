from __future__ import annotations

import asyncio
from unittest.mock import Mock, AsyncMock

import anyio
import httpx2
import pytest
from websockets.uri import parse_uri
from websockets.client import ClientProtocol
from websockets.protocol import State
from websockets.exceptions import InvalidStatus, SecurityError, ConnectionClosedOK
from websockets.sync.client import ClientConnection
from websockets.asyncio.client import ClientConnection as AsyncClientConnection

from openai import OpenAI, AsyncOpenAI, WebSocketConnectionClosedError
from openai._types import Omit
from openai._send_queue import SendQueue
from openai.lib._realtime_translation import _connect, _async_connect

from .test_websocket_redirects import FOLLOWS_REDIRECTS, Handshakes, redirect_error, unexpected_http, async_http_client

ERROR_EVENT = b'{"type":"error","error":{"message":"fake diagnostic"}}'
CLOSED_EVENT = b'{"type":"session.closed"}'


def sync_client() -> OpenAI:
    return OpenAI(
        api_key="fake-key",
        http_client=httpx2.Client(transport=httpx2.MockTransport(unexpected_http)),
    )


def queue() -> SendQueue:
    pending = SendQueue()
    for data in ["first", "second", "third"]:
        pending.enqueue(data)
    return pending


def test_sync_credentials_url_and_options(monkeypatch: pytest.MonkeyPatch) -> None:
    provider = Mock(side_effect=["fake-first", "fake-second"])
    socket = Mock(spec=ClientConnection)
    connect = Mock(return_value=socket)
    monkeypatch.setattr("websockets.sync.client.connect", connect)
    with OpenAI(
        api_key=provider,
        base_url="https://api.example.test/v1/?base=value/",
        websocket_base_url="wss://socket.example.test/custom/",
        http_client=httpx2.Client(transport=httpx2.MockTransport(unexpected_http)),
    ) as client:
        for token in ["fake-first", "fake-second"]:
            connection = _connect(client, model="fake-model", extra_query={"extra": "value"})
            assert connect.call_args.args == (
                "wss://socket.example.test/custom/realtime/translations?base=value%2F&model=fake-model&extra=value",
            )
            assert connect.call_args.kwargs["additional_headers"]["Authorization"] == f"Bearer {token}"
            assert connect.call_args.kwargs["user_agent_header"] == client.user_agent
            assert connect.call_args.kwargs["max_size"] is None
            connection.close()
        _connect(
            client.with_options(api_key="fake-static"),
            model="fake-model",
            extra_headers={"Authorization": Omit(), "X-Test": "fake-value"},
            websocket_connection_options={"max_size": 123},
        ).close()
        assert connect.call_args.kwargs["additional_headers"] == {"X-Test": "fake-value"}
        assert connect.call_args.kwargs["max_size"] == 123
    assert provider.call_count == 2


async def test_async_credentials_url_and_options(monkeypatch: pytest.MonkeyPatch) -> None:
    provider = AsyncMock(side_effect=["fake-first", "fake-second"])
    socket = AsyncMock(spec=AsyncClientConnection)
    connect = AsyncMock(return_value=socket)
    monkeypatch.setattr("openai.lib._websocket._WebSocketConnect", connect)
    async with AsyncOpenAI(
        api_key=provider, base_url="http://origin.test/v1", http_client=async_http_client()
    ) as client:
        for token in ["fake-first", "fake-second"]:
            connection = await _async_connect(client, model="fake-model")
            assert connect.call_args.args == ("ws://origin.test/v1/realtime/translations?model=fake-model",)
            assert connect.call_args.kwargs["additional_headers"]["Authorization"] == f"Bearer {token}"
            assert connect.call_args.kwargs["max_size"] is None
            await connection.close()
        static_client = client.with_options(api_key="fake-static")
        connection = await _async_connect(
            static_client,
            model="fake-model",
            extra_headers={"Authorization": "Bearer fake-override"},
            websocket_connection_options={"max_size": 123},
        )
        assert connect.call_args.kwargs["additional_headers"]["Authorization"] == "Bearer fake-override"
        assert connect.call_args.kwargs["max_size"] == 123
        await connection.close()
    assert provider.await_count == 2


@pytest.mark.parametrize("target,allowed", [("/final", True), ("wss://other.test/final", False)])
async def test_async_protected_connector(monkeypatch: pytest.MonkeyPatch, target: str, allowed: bool) -> None:
    handshakes = Handshakes(monkeypatch, [target, None])
    pending = queue()
    succeeds = allowed and FOLLOWS_REDIRECTS
    async with AsyncOpenAI(
        api_key="fake-key", websocket_base_url="wss://origin.test", http_client=async_http_client()
    ) as client:
        if succeeds:
            connection = await _async_connect(client, model="fake-model", send_queue=pending)
            await connection.close()
            assert [data for _, data in handshakes.sent] == ["first", "second", "third"]
        else:
            with pytest.raises(WebSocketConnectionClosedError) as caught:
                await _async_connect(client, model="fake-model", send_queue=pending)
            assert isinstance(caught.value.__cause__, SecurityError if FOLLOWS_REDIRECTS else InvalidStatus)
            assert caught.value.unsent_messages == ["first", "second", "third"]
            assert not handshakes.sent
    assert len(handshakes.attempts) == (2 if succeeds else 1)
    assert all(uri.host == "origin.test" for uri, _ in handshakes.attempts)
    assert pending.drain() == []


def test_sync_redirect_failure_is_not_retried(monkeypatch: pytest.MonkeyPatch) -> None:
    connect = Mock(side_effect=redirect_error("wss://other.test/final"))
    monkeypatch.setattr("websockets.sync.client.connect", connect)
    with sync_client() as client, pytest.raises(InvalidStatus):
        _connect(client, model="fake-model")
    connect.assert_called_once()


@pytest.mark.parametrize("cleanup_fails", [False, True])
def test_sync_failed_sends(monkeypatch: pytest.MonkeyPatch, cleanup_fails: bool) -> None:
    socket = Mock(spec=ClientConnection)
    socket.send.side_effect = [None, RuntimeError("fake sensitive transport detail")]
    socket.close.side_effect = RuntimeError("fake cleanup detail") if cleanup_fails else None
    monkeypatch.setattr("websockets.sync.client.connect", Mock(return_value=socket))
    pending = queue()
    with sync_client() as client:
        with pytest.raises(WebSocketConnectionClosedError) as caught:
            _connect(client, model="fake-model", send_queue=pending)
        assert caught.value.unsent_messages == ["second", "third"]
        assert "fake" not in str(caught.value)
        assert pending.drain() == []
        socket.close.assert_called_once()

        socket.send.side_effect = RuntimeError("fake send detail")
        connection = _connect(client, model="fake-model")
        for data in ["failed frame", "later frame"]:
            with pytest.raises(WebSocketConnectionClosedError) as failed:
                connection.send(data)
            assert failed.value.unsent_messages == [data]
            assert data not in str(failed.value)
        assert socket.send.call_count == 3  # The later frame is never sent or retained.


@pytest.mark.parametrize("cleanup_fails", [False, True])
async def test_async_failed_sends(monkeypatch: pytest.MonkeyPatch, cleanup_fails: bool) -> None:
    socket = AsyncMock(spec=AsyncClientConnection)
    transport = Mock(spec=asyncio.Transport)
    socket.transport = transport
    socket.send.side_effect = [None, RuntimeError("fake sensitive transport detail")]
    socket.close.side_effect = RuntimeError("fake cleanup detail") if cleanup_fails else None
    monkeypatch.setattr("openai.lib._websocket._WebSocketConnect", AsyncMock(return_value=socket))
    pending = queue()
    async with AsyncOpenAI(api_key="fake-key", http_client=async_http_client()) as client:
        with pytest.raises(WebSocketConnectionClosedError) as caught:
            await _async_connect(client, model="fake-model", send_queue=pending)
        assert caught.value.unsent_messages == ["second", "third"]
        assert "fake" not in str(caught.value)
        assert pending.drain() == []
        socket.close.assert_awaited_once()
        assert transport.abort.call_count == (1 if cleanup_fails else 0)

        socket.send.side_effect = RuntimeError("fake send detail")
        connection = await _async_connect(client, model="fake-model")
        for data in ["failed frame", "later frame"]:
            with pytest.raises(WebSocketConnectionClosedError) as failed:
                await connection.send(data)
            assert failed.value.unsent_messages == [data]
            assert data not in str(failed.value)
        assert socket.send.await_count == 3


def test_sync_delivery_and_successful_startup(monkeypatch: pytest.MonkeyPatch) -> None:
    socket = Mock(spec=ClientConnection)
    socket.recv.side_effect = [ERROR_EVENT, CLOSED_EVENT, ConnectionClosedOK(None, None)]
    monkeypatch.setattr("websockets.sync.client.connect", Mock(return_value=socket))
    pending = queue()
    with sync_client() as client:
        connection = _connect(client, model="fake-model", send_queue=pending)
        assert pending.drain() == []
        assert [call.args[0] for call in socket.send.call_args_list] == ["first", "second", "third"]
        assert connection.recv() == ERROR_EVENT
        assert connection.recv() == CLOSED_EVENT
        with pytest.raises(ConnectionClosedOK):
            connection.recv()
        connection.close()
        with pytest.raises(WebSocketConnectionClosedError) as caught:
            connection.send("after close")
        assert caught.value.unsent_messages == ["after close"]


async def test_async_delivery_and_successful_startup(monkeypatch: pytest.MonkeyPatch) -> None:
    socket = AsyncMock(spec=AsyncClientConnection)
    socket.recv.side_effect = [ERROR_EVENT, CLOSED_EVENT, ConnectionClosedOK(None, None)]
    monkeypatch.setattr("openai.lib._websocket._WebSocketConnect", AsyncMock(return_value=socket))
    pending = queue()
    async with AsyncOpenAI(api_key="fake-key", http_client=async_http_client()) as client:
        connection = await _async_connect(client, model="fake-model", send_queue=pending)
        assert pending.drain() == []
        assert [call.args[0] for call in socket.send.call_args_list] == ["first", "second", "third"]
        assert await connection.recv() == ERROR_EVENT
        assert await connection.recv() == CLOSED_EVENT
        with pytest.raises(ConnectionClosedOK):
            await connection.recv()
        await connection.close()
        with pytest.raises(WebSocketConnectionClosedError) as caught:
            await connection.send("after close")
        assert caught.value.unsent_messages == ["after close"]


async def test_cancelled_startup_closes_and_preserves_queue(monkeypatch: pytest.MonkeyPatch) -> None:
    socket = AsyncMock(spec=AsyncClientConnection)
    socket.send.side_effect = [None, asyncio.CancelledError()]
    monkeypatch.setattr("openai.lib._websocket._WebSocketConnect", AsyncMock(return_value=socket))
    pending = queue()
    async with AsyncOpenAI(api_key="fake-key", http_client=async_http_client()) as client:
        with pytest.raises(asyncio.CancelledError):
            await _async_connect(client, model="fake-model", send_queue=pending)
    socket.close.assert_awaited_once()
    assert pending.drain() == ["second", "third"]


async def test_cancelled_send_closes_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    socket = AsyncMock(spec=AsyncClientConnection)
    socket.send.side_effect = asyncio.CancelledError()
    monkeypatch.setattr("openai.lib._websocket._WebSocketConnect", AsyncMock(return_value=socket))
    async with AsyncOpenAI(api_key="fake-key", http_client=async_http_client()) as client:
        connection = await _async_connect(client, model="fake-model")
        with pytest.raises(asyncio.CancelledError):
            await connection.send("cancelled frame")
        socket.close.assert_awaited_once()
        with pytest.raises(WebSocketConnectionClosedError):
            await connection.send("later frame")
        socket.send.assert_awaited_once()


def test_sync_enqueue_during_startup(monkeypatch: pytest.MonkeyPatch) -> None:
    pending = queue()
    socket = Mock(spec=ClientConnection)

    def send(data: str) -> None:
        if data == "first":
            pending.enqueue("queued during flush")

    socket.send.side_effect = send
    monkeypatch.setattr("websockets.sync.client.connect", Mock(return_value=socket))
    with sync_client() as client:
        connection = _connect(client, model="fake-model", send_queue=pending)
        assert [call.args[0] for call in socket.send.call_args_list] == [
            "first",
            "second",
            "third",
            "queued during flush",
        ]
        assert pending.drain() == []
        connection.close()


async def test_async_enqueue_during_startup(monkeypatch: pytest.MonkeyPatch) -> None:
    pending = queue()
    socket = AsyncMock(spec=AsyncClientConnection)

    async def send(data: str) -> None:
        if data == "first":
            await anyio.sleep(0)
            pending.enqueue("queued during flush")

    socket.send.side_effect = send
    monkeypatch.setattr("openai.lib._websocket._WebSocketConnect", AsyncMock(return_value=socket))
    async with AsyncOpenAI(api_key="fake-key", http_client=async_http_client()) as client:
        connection = await _async_connect(client, model="fake-model", send_queue=pending)
        assert [call.args[0] for call in socket.send.call_args_list] == [
            "first",
            "second",
            "third",
            "queued during flush",
        ]
        assert pending.drain() == []
        await connection.close()


@pytest.mark.parametrize("startup", [False, True])
async def test_anyio_cancellation_finishes_cleanup(monkeypatch: pytest.MonkeyPatch, startup: bool) -> None:
    socket = AsyncMock(spec=AsyncClientConnection)
    transport = Mock(spec=asyncio.Transport)
    socket.transport = transport
    cleanup_completed = Mock()
    pending = queue()

    async def close(*, code: int, reason: str) -> None:
        assert code == 1000 and reason == ""
        await anyio.sleep(0)
        cleanup_completed()

    socket.close.side_effect = close
    monkeypatch.setattr("openai.lib._websocket._WebSocketConnect", AsyncMock(return_value=socket))
    async with AsyncOpenAI(api_key="fake-key", http_client=async_http_client()) as client:
        connection = None if startup else await _async_connect(client, model="fake-model")
        with anyio.CancelScope() as scope:

            async def cancel_send(_data: str) -> None:
                scope.cancel()
                await anyio.sleep(0)

            socket.send.side_effect = cancel_send
            if connection is None:
                await _async_connect(client, model="fake-model", send_queue=pending)
            else:
                await connection.send("cancelled frame")
            pytest.fail("Cancellation must propagate")
        assert scope.cancelled_caught
        cleanup_completed.assert_called_once()
        transport.abort.assert_not_called()
        assert pending.drain() == ["first", "second", "third"]


@pytest.mark.parametrize("startup", [False, True])
@pytest.mark.parametrize("cancel_kind", ["asyncio", "anyio"])
async def test_cancelled_flow_control_has_bounded_cleanup(
    monkeypatch: pytest.MonkeyPatch, startup: bool, cancel_kind: str
) -> None:
    # Exercise the installed connection's send/drain/close code without sockets.
    # pause_writing is the protocol callback for transport backpressure.
    socket = AsyncClientConnection(ClientProtocol(parse_uri("ws://example.test"), state=State.OPEN))
    transport = Mock(spec=asyncio.Transport)
    transport.is_closing.return_value = False
    socket.connection_made(transport)
    socket.pause_writing()
    transport.abort.side_effect = lambda: socket.connection_lost(None)
    written = asyncio.Event()

    def write(_data: bytes) -> None:
        written.set()

    transport.write.side_effect = write
    monkeypatch.setattr("openai.lib._websocket._WebSocketConnect", AsyncMock(return_value=socket))
    monkeypatch.setattr("openai.lib._realtime_translation._FAILURE_CLOSE_TIMEOUT", 0.01)
    pending = queue()
    scopes: list[anyio.CancelScope] = []
    async with AsyncOpenAI(api_key="fake-key", http_client=async_http_client()) as client:
        connection = None if startup else await _async_connect(client, model="fake-model")

        async def send() -> None:
            with anyio.CancelScope() as scope:
                scopes.append(scope)
                if connection is None:
                    await _async_connect(client, model="fake-model", send_queue=pending)
                else:
                    await connection.send("fake frame")
                pytest.fail("The interrupted send must not complete")

        task = asyncio.create_task(send())
        try:
            await asyncio.wait_for(written.wait(), timeout=1)
            if cancel_kind == "asyncio":
                task.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await asyncio.wait_for(task, timeout=1)
            else:
                scopes[0].cancel()
                await asyncio.wait_for(task, timeout=1)
                assert scopes[0].cancelled_caught
            transport.abort.assert_called_once()
            assert socket.state is State.CLOSED
            assert socket.connection_lost_waiter.done()
            assert pending.drain() == ["first", "second", "third"]
        finally:
            if not socket.connection_lost_waiter.done():
                socket.connection_lost(None)
            if not task.done():
                task.cancel()
            await asyncio.gather(task, return_exceptions=True)


@pytest.mark.parametrize("startup", [False, True])
@pytest.mark.parametrize("abort_fails", [False, True])
async def test_stalled_cleanup_preserves_failed_send(
    monkeypatch: pytest.MonkeyPatch, startup: bool, abort_fails: bool
) -> None:
    socket = AsyncMock(spec=AsyncClientConnection)
    transport = Mock(spec=asyncio.Transport)
    socket.transport = transport
    if abort_fails:
        transport.abort.side_effect = RuntimeError("fake abort failure")
    original = RuntimeError("fake send failure")
    socket.send.side_effect = original

    async def close(*, code: int, reason: str) -> None:
        assert code == 1000 and reason == ""
        await anyio.sleep_forever()

    socket.close.side_effect = close
    monkeypatch.setattr("openai.lib._websocket._WebSocketConnect", AsyncMock(return_value=socket))
    monkeypatch.setattr("openai.lib._realtime_translation._FAILURE_CLOSE_TIMEOUT", 0.01)
    pending = queue()
    async with AsyncOpenAI(api_key="fake-key", http_client=async_http_client()) as client:
        connection = None if startup else await _async_connect(client, model="fake-model")
        with pytest.raises(WebSocketConnectionClosedError) as caught:
            if connection is None:
                await asyncio.wait_for(_async_connect(client, model="fake-model", send_queue=pending), timeout=1)
            else:
                await asyncio.wait_for(connection.send("fake frame"), timeout=1)
        assert caught.value.__cause__ is original
        assert caught.value.unsent_messages == (["first", "second", "third"] if startup else ["fake frame"])
        assert pending.drain() == ([] if startup else ["first", "second", "third"])
        transport.abort.assert_called_once()
