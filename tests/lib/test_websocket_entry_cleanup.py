from __future__ import annotations

import json
import asyncio
from typing import Any

import pytest

from openai import OpenAI, AsyncOpenAI

PRODUCTS = [
    "realtime",
    "transcription",
    "sideband",
    "responses",
    "beta.responses",
    "live",
    "live-sideband",
    "live-forks",
    "translation",
]


def manager(client: Any, product: str) -> Any:
    if product == "realtime":
        return client.realtime.connect(model="test")
    if product == "transcription":
        return client.realtime.connect(extra_query={"intent": "transcription"})
    if product == "sideband":
        return client.realtime.connect(call_id="call_1")
    if product == "responses":
        return client.responses.connect()
    if product == "beta.responses":
        return client.beta.responses.connect()
    if product == "live":
        return client.live.connect()
    if product == "live-sideband":
        return client.live.sideband.connect(session_id="live_1")
    if product == "live-forks":
        return client.live.forks.connect(session_id="live_1")
    return client.realtime.translations.connect("test")


@pytest.fixture(autouse=True)
def no_proxies(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_PROXY", "*")
    monkeypatch.setenv("no_proxy", "*")


@pytest.mark.parametrize("product", PRODUCTS)
@pytest.mark.parametrize("cancel", [False, True])
@pytest.mark.asyncio
async def test_enter_owns_socket_through_initial_flush(
    monkeypatch: pytest.MonkeyPatch, product: str, cancel: bool
) -> None:
    sending, release = asyncio.Event(), asyncio.Event()

    class Socket:
        closed = False
        sent: list[str] = []

        async def send(self, value: str) -> None:
            sending.set()
            await release.wait()
            self.sent.append(value)

        async def close(self, **_kwargs: Any) -> None:
            self.closed = True

    sock = Socket()

    async def connect(*_args: Any, **_kwargs: Any) -> Socket:
        return sock

    monkeypatch.setattr("openai.lib._websocket._WebSocketConnect", connect)
    async with AsyncOpenAI(api_key="fake-key") as client:
        session = manager(client, product)
        session.send({"type": "synthetic.first"})

        async def open_and_close() -> None:
            async with session:
                pass

        entering = asyncio.create_task(open_and_close())
        try:
            await asyncio.wait_for(sending.wait(), timeout=10)
            if cancel:
                entering.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await asyncio.wait_for(entering, timeout=10)
            else:
                release.set()
                await asyncio.wait_for(entering, timeout=10)
                assert [json.loads(value)["type"] for value in sock.sent] == ["synthetic.first"]
            assert sock.closed
        finally:
            release.set()
            if not entering.done():
                entering.cancel()
            await asyncio.gather(entering, return_exceptions=True)


@pytest.mark.parametrize("product", PRODUCTS)
@pytest.mark.parametrize("close_fails", [False, True])
def test_interrupted_sync_entry_closes_socket_and_preserves_error(
    monkeypatch: pytest.MonkeyPatch, product: str, close_fails: bool
) -> None:
    original = KeyboardInterrupt("initial send interrupted")

    class Socket:
        close_called = False

        def send(self, _value: str) -> None:
            raise original

        def close(self, **_kwargs: Any) -> None:
            self.close_called = True
            if close_fails:
                raise RuntimeError("cleanup also failed")

    sock = Socket()

    def connect(*_args: Any, **_kwargs: Any) -> Socket:
        return sock

    monkeypatch.setattr("websockets.sync.client.connect", connect)
    with OpenAI(api_key="fake-key") as client:
        session = manager(client, product)
        session.send({"type": "synthetic.first"})
        with pytest.raises(KeyboardInterrupt) as raised:
            with session:
                pytest.fail("entry must not succeed")
        assert raised.value is original
        assert sock.close_called


@pytest.mark.asyncio
async def test_async_constructor_failure_closes_acquired_socket(monkeypatch: pytest.MonkeyPatch) -> None:
    import openai.resources.realtime.realtime as module

    original = RuntimeError("cannot initialize connection")

    class Socket:
        close_called = False

        async def close(self, **_kwargs: Any) -> None:
            self.close_called = True
            raise ValueError("cannot close cleanly")

    sock = Socket()

    async def connect(*_args: Any, **_kwargs: Any) -> Socket:
        return sock

    def fail_construct(*_args: Any, **_kwargs: Any) -> None:
        raise original

    monkeypatch.setattr("openai.lib._websocket._WebSocketConnect", connect)
    async with AsyncOpenAI(api_key="fake-key") as client:
        session = client.realtime.connect(model="test")
        monkeypatch.setattr(module, "AsyncRealtimeConnection", fail_construct)
        with pytest.raises(RuntimeError) as raised:
            await session.enter()
        assert raised.value is original
        assert sock.close_called
