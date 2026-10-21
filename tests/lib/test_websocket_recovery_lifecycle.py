from __future__ import annotations

import asyncio
import threading
from typing import Any, Callable
from typing_extensions import override

import pytest
from websockets.exceptions import ConnectionClosedError

from openai import OpenAI, AsyncOpenAI

PRODUCTS = ["realtime", "transcription", "sideband", "responses", "live"]


def manager(client: Any, product: str, on_reconnecting: Callable[[Any], Any] | None = None) -> Any:
    def allow_reconnecting(_event: Any) -> None:
        pass

    options = {"on_reconnecting": on_reconnecting or allow_reconnecting, "initial_delay": 0}
    if product == "realtime":
        return client.realtime.connect(model="test-model", **options)
    if product == "transcription":
        return client.realtime.connect(extra_query={"intent": "transcription"}, **options)
    if product == "sideband":
        return client.realtime.connect(call_id="test-call", **options)
    if product == "beta_responses":
        return client.beta.responses.connect(**options)
    if product == "live_forks":
        return client.live.forks.connect(session_id="test-session", **options)
    if product == "live_sideband":
        return client.live.sideband.connect(session_id="test-session", **options)
    if product == "translations":
        return client.realtime.translations.connect(model="test-model", **options)
    return getattr(client, product).connect(**options)


class Socket:
    def __init__(self, initial: bool) -> None:
        self.initial = initial
        self.closed = False
        self.sent: list[str | bytes] = []

    def recv(self, **_kwargs: Any) -> bytes:
        if self.initial or self.closed:
            raise ConnectionClosedError(None, None)
        return b'{"type":"synthetic.progress","event_id":"test-1"}'

    def send(self, message: str | bytes) -> None:
        if self.initial or self.closed:
            raise ConnectionClosedError(None, None)
        self.sent.append(message)

    def close(self, **_kwargs: Any) -> None:
        self.closed = True


class AsyncSocket:
    def __init__(self, initial: bool) -> None:
        self.socket = Socket(initial)

    async def recv(self, **kwargs: Any) -> bytes:
        return self.socket.recv(**kwargs)

    async def send(self, message: str | bytes) -> None:
        self.socket.send(message)

    async def close(self, **kwargs: Any) -> None:
        self.socket.close(**kwargs)


@pytest.fixture(autouse=True)
def no_proxies(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_PROXY", "*")
    monkeypatch.setenv("no_proxy", "*")


@pytest.mark.parametrize("product", PRODUCTS)
@pytest.mark.parametrize("close_during_handshake", [False, True])
@pytest.mark.asyncio
async def test_async_recovery_keeps_close_authoritative(
    monkeypatch: pytest.MonkeyPatch, product: str, close_during_handshake: bool
) -> None:
    original, replacement = AsyncSocket(True), AsyncSocket(False)
    started, release = asyncio.Event(), asyncio.Event()
    opens = 0

    async def connect(*_args: Any, **_kwargs: Any) -> AsyncSocket:
        nonlocal opens
        opens += 1
        if opens == 1:
            return original
        started.set()
        await release.wait()
        return replacement

    monkeypatch.setattr("openai.lib._websocket._WebSocketConnect", connect)
    async with AsyncOpenAI(api_key="fake-key") as client:
        async with manager(client, product) as connection:
            iterator = aiter(connection)
            receiving = asyncio.create_task(anext(iterator))
            try:
                await asyncio.wait_for(started.wait(), timeout=10)
                if close_during_handshake:
                    await connection.close()
                    # Closing must retire the queue even before the pending
                    # handshake returns, for typed and raw sends alike.
                    with pytest.raises(ConnectionClosedError):
                        await connection.send_raw('{"type":"synthetic.after_close"}')
                    with pytest.raises(ConnectionClosedError):
                        await connection.send({"type": "synthetic.after_close"})
                release.set()
                if close_during_handshake:
                    with pytest.raises(ConnectionClosedError):
                        await asyncio.wait_for(receiving, timeout=10)
                    assert replacement.socket.closed
                else:
                    event = await asyncio.wait_for(receiving, timeout=10)
                    assert getattr(event, "type", None) == "synthetic.progress"
                    assert not replacement.socket.closed
                assert opens == 2
            finally:
                release.set()
                if not receiving.done():
                    receiving.cancel()
                await asyncio.gather(receiving, return_exceptions=True)
                await iterator.aclose()


@pytest.mark.parametrize("product", PRODUCTS)
@pytest.mark.asyncio
async def test_cancelled_recovery_cannot_queue_after_close(monkeypatch: pytest.MonkeyPatch, product: str) -> None:
    original = AsyncSocket(True)
    started = asyncio.Event()
    opens = 0

    async def connect(*_args: Any, **_kwargs: Any) -> AsyncSocket:
        nonlocal opens
        opens += 1
        if opens == 1:
            return original
        started.set()
        await asyncio.Future[Any]()
        raise AssertionError("The canceled connection must never complete")

    monkeypatch.setattr("openai.lib._websocket._WebSocketConnect", connect)
    async with AsyncOpenAI(api_key="fake-key") as client:
        async with manager(client, product) as connection:
            iterator = aiter(connection)
            receiving = asyncio.create_task(anext(iterator))
            try:
                await asyncio.wait_for(started.wait(), timeout=10)
                receiving.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await asyncio.wait_for(receiving, timeout=10)
                with pytest.raises(ConnectionClosedError):
                    await connection.send_raw('{"type":"synthetic.after_cancel"}')
                await connection.close()
                with pytest.raises(ConnectionClosedError):
                    await connection.send({"type": "synthetic.after_close"})
                assert original.socket.sent == []
            finally:
                if not receiving.done():
                    receiving.cancel()
                await asyncio.gather(receiving, return_exceptions=True)
                await iterator.aclose()


@pytest.mark.parametrize("product", PRODUCTS)
@pytest.mark.asyncio
async def test_cancel_during_discard_still_closes_replacement(monkeypatch: pytest.MonkeyPatch, product: str) -> None:
    original = AsyncSocket(True)
    handshake_started, release_handshake = asyncio.Event(), asyncio.Event()
    cleanup_started, release_cleanup, cleanup_done = asyncio.Event(), asyncio.Event(), asyncio.Event()
    opens = 0

    class ReplacementSocket(AsyncSocket):
        @override
        async def close(self, **kwargs: Any) -> None:
            cleanup_started.set()
            await release_cleanup.wait()
            await super().close(**kwargs)
            cleanup_done.set()

    replacement = ReplacementSocket(False)

    async def connect(*_args: Any, **_kwargs: Any) -> AsyncSocket:
        nonlocal opens
        opens += 1
        if opens == 1:
            return original
        handshake_started.set()
        await release_handshake.wait()
        return replacement

    monkeypatch.setattr("openai.lib._websocket._WebSocketConnect", connect)
    async with AsyncOpenAI(api_key="fake-key") as client:
        async with manager(client, product) as connection:
            iterator = aiter(connection)
            receiving = asyncio.create_task(anext(iterator))
            try:
                await asyncio.wait_for(handshake_started.wait(), timeout=10)
                await connection.close()
                release_handshake.set()
                await asyncio.wait_for(cleanup_started.wait(), timeout=10)
                receiving.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await asyncio.wait_for(receiving, timeout=10)
                with pytest.raises(ConnectionClosedError):
                    await connection.send_raw('{"type":"synthetic.after_close"}')
                release_cleanup.set()
                await asyncio.wait_for(cleanup_done.wait(), timeout=10)
                assert replacement.socket.closed
            finally:
                release_handshake.set()
                release_cleanup.set()
                if not receiving.done():
                    receiving.cancel()
                await asyncio.gather(receiving, return_exceptions=True)
                await iterator.aclose()


@pytest.mark.parametrize("product", PRODUCTS)
@pytest.mark.parametrize("close_during_handshake", [False, True])
def test_sync_recovery_keeps_close_authoritative(
    monkeypatch: pytest.MonkeyPatch, product: str, close_during_handshake: bool
) -> None:
    original, replacement = Socket(True), Socket(False)
    started, release = threading.Event(), threading.Event()
    opens = 0

    def connect(*_args: Any, **_kwargs: Any) -> Socket:
        nonlocal opens
        opens += 1
        if opens == 1:
            return original
        started.set()
        assert release.wait(10)
        return replacement

    monkeypatch.setattr("websockets.sync.client.connect", connect)
    with OpenAI(api_key="fake-key") as client:
        with manager(client, product) as connection:
            result: list[Any] = []
            iterator = iter(connection)

            def receive() -> None:
                try:
                    result.append(next(iterator))
                except Exception as exc:
                    result.append(exc)

            worker = threading.Thread(target=receive)
            worker.start()
            try:
                assert started.wait(10)
                if close_during_handshake:
                    connection.close()
                    with pytest.raises(ConnectionClosedError):
                        connection.send_raw('{"type":"synthetic.after_close"}')
                    with pytest.raises(ConnectionClosedError):
                        connection.send({"type": "synthetic.after_close"})
                release.set()
                worker.join(10)
                assert not worker.is_alive()
                assert len(result) == 1
                if close_during_handshake:
                    assert isinstance(result[0], ConnectionClosedError)
                    assert replacement.closed
                else:
                    assert getattr(result[0], "type", None) == "synthetic.progress"
                    assert not replacement.closed
                assert opens == 2
            finally:
                release.set()
                worker.join(10)
                iterator.close()


@pytest.mark.parametrize("product", PRODUCTS + ["beta_responses", "live_forks", "live_sideband", "translations"])
@pytest.mark.parametrize("interrupt_from", ["callback", "handshake"])
@pytest.mark.parametrize("error_type", [KeyboardInterrupt, SystemExit])
def test_interrupted_sync_recovery_rejects_sends_until_retried(
    monkeypatch: pytest.MonkeyPatch, product: str, interrupt_from: str, error_type: type[BaseException]
) -> None:
    original, replacement = Socket(True), Socket(False)
    failure = error_type("synthetic recovery interruption")
    opens = 0
    callbacks = 0

    def connect(*_args: Any, **_kwargs: Any) -> Socket:
        nonlocal opens
        opens += 1
        if opens == 1:
            return original
        if opens == 2 and interrupt_from == "handshake":
            raise failure
        return replacement

    def reconnecting(_event: Any) -> None:
        nonlocal callbacks
        callbacks += 1
        if callbacks == 1 and interrupt_from == "callback":
            raise failure

    monkeypatch.setattr("websockets.sync.client.connect", connect)
    with OpenAI(api_key="fake-key") as client:
        with manager(client, product, reconnecting) as connection:
            with pytest.raises(error_type) as caught:
                next(iter(connection))
            assert caught.value is failure
            with pytest.raises(ConnectionClosedError):
                connection.send_raw('{"type":"synthetic.after_interrupt_raw"}')
            with pytest.raises(ConnectionClosedError):
                connection.send({"type": "synthetic.after_interrupt_typed"})
            # A later receive may start another recovery. The failed sends
            # above must not be silently transmitted as a result.
            event = next(iter(connection))
            assert getattr(event, "type", None) == "synthetic.progress"
            assert callbacks == 2
            assert opens == (3 if interrupt_from == "handshake" else 2)
            assert original.sent == []
            assert replacement.sent == []


@pytest.mark.parametrize("product", PRODUCTS)
def test_ordinary_sync_reconnecting_error_preserves_original_close(
    monkeypatch: pytest.MonkeyPatch, product: str
) -> None:
    original = Socket(True)

    def connect(*_args: Any, **_kwargs: Any) -> Socket:
        return original

    monkeypatch.setattr("websockets.sync.client.connect", connect)

    def reconnecting(_event: Any) -> None:
        raise ValueError("synthetic callback error")

    with OpenAI(api_key="fake-key") as client:
        with manager(client, product, reconnecting) as connection:
            with pytest.raises(ConnectionClosedError):
                next(iter(connection))
            with pytest.raises(ConnectionClosedError):
                connection.send_raw('{"type":"synthetic.after_error"}')
            assert original.sent == []
