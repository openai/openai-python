from __future__ import annotations

import json
import asyncio
from typing import Any, Literal, Callable, Generator
from threading import Event, Thread
from contextlib import contextmanager

import httpx2
import pytest
from websockets.exceptions import ConnectionClosed, ConnectionClosedError
from websockets.sync.server import ServerConnection, serve
from websockets.extensions.permessage_deflate import ClientPerMessageDeflateFactory

from openai import OpenAI, AsyncOpenAI
from openai.types.websocket_reconnection import ReconnectingEvent
from tests.lib.test_websocket_entry_cleanup import PRODUCTS
from openai.types.websocket_connection_options import WebSocketConnectionOptions


@pytest.fixture(autouse=True)
def no_proxies(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_PROXY", "*")
    monkeypatch.setenv("no_proxy", "*")


def manager(
    client: Any,
    product: str,
    options: WebSocketConnectionOptions,
    on_reconnecting: Callable[[ReconnectingEvent], None] | None = None,
) -> Any:
    settings: dict[str, Any] = {
        "websocket_connection_options": options,
        "on_reconnecting": on_reconnecting,
        "initial_delay": 0,
        "max_retries": 1,
    }
    if product == "realtime":
        return client.realtime.connect(model="test", **settings)
    if product == "transcription":
        return client.realtime.connect(extra_query={"intent": "transcription"}, **settings)
    if product == "sideband":
        return client.realtime.connect(call_id="call_1", **settings)
    if product == "responses":
        return client.responses.connect(**settings)
    if product == "beta.responses":
        return client.beta.responses.connect(**settings)
    if product == "live":
        return client.live.connect(**settings)
    if product == "live-sideband":
        return client.live.sideband.connect(session_id="live_1", **settings)
    if product == "live-forks":
        return client.live.forks.connect(session_id="live_1", **settings)
    assert product == "translation"
    return client.realtime.translations.connect("test", **settings)


@contextmanager
def compression_peer(
    product: str, *, reconnect: bool = False, wire: bytes | None = None
) -> Generator[tuple[str, bytes, list[tuple[list[str], list[str]]], list[tuple[int, str | bytes]]], None, None]:
    if wire is None:
        if product == "live":
            wire = b'{"type":"session.output_transcript.delta","event_id":"recovered","delta":"go"}'
        else:
            wire = b'{"type":"input_audio_buffer.cleared","event_id":"recovered"}'
    handshakes: list[tuple[list[str], list[str]]] = []
    frames: list[tuple[int, str | bytes]] = []
    failures: list[Exception] = []
    finished: list[Event] = []

    def accept(socket: ServerConnection) -> None:
        done = Event()
        finished.append(done)
        try:
            assert socket.request is not None
            handshakes.append(
                (
                    socket.request.headers.get_all("Sec-WebSocket-Extensions"),
                    [extension.name for extension in socket.protocol.extensions],
                )
            )
            current = len(handshakes)
            if reconnect and current == 1:
                frames.append((current, socket.recv(timeout=5)))
                socket.close(1011, "synthetic restart")
                return
            socket.send(wire)
            try:
                while True:
                    message = socket.recv(timeout=5)
                    frames.append((current, message))
                    if reconnect and current == 2 and message == "after-reconnect":
                        socket.send(b"test.peer.received")
            except ConnectionClosed:
                # Caller either consumed the message and closed, or rejected size 0.
                pass
        except Exception as exc:
            failures.append(exc)
        finally:
            done.set()

    with serve(accept, "127.0.0.1", 0, close_timeout=1) as server:
        thread = Thread(target=server.serve_forever)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.socket.getsockname()[1]}/v1", wire, handshakes, frames
        finally:
            server.shutdown()
            thread.join(5)
            assert not thread.is_alive()
            for done in finished:
                assert done.wait(5), "peer handler did not finish"
            assert not failures, failures


def assert_compression(handshakes: list[tuple[list[str], list[str]]], compressed: bool, count: int = 1) -> None:
    assert len(handshakes) == count
    for offered, negotiated in handshakes:
        assert ("permessage-deflate" in ", ".join(offered)) is compressed
        assert ("permessage-deflate" in negotiated) is compressed


async def receive_once(
    product: str,
    mode: Literal["sync", "async"],
    options: WebSocketConnectionOptions,
    compressed: bool,
    *,
    wire: bytes | None = None,
) -> None:
    with compression_peer(product, wire=wire) as (url, wire, handshakes, frames):
        reject = options.get("max_size") == 0
        if mode == "sync":

            def read() -> bytes:
                with OpenAI(
                    api_key="local",
                    base_url=url,
                    websocket_base_url=url.replace("http:", "ws:"),
                    http_client=httpx2.Client(trust_env=False),
                ) as client:
                    with manager(client, product, options) as connection:
                        return connection.recv_bytes()

            if reject:
                with pytest.raises(ConnectionClosedError) as exc:
                    await asyncio.wait_for(asyncio.to_thread(read), 10)
                assert exc.value.sent is not None and exc.value.sent.code == 1009
            else:
                assert await asyncio.wait_for(asyncio.to_thread(read), 10) == wire
        else:
            async with AsyncOpenAI(
                api_key="local",
                base_url=url,
                websocket_base_url=url.replace("http:", "ws:"),
                http_client=httpx2.AsyncClient(trust_env=False),
            ) as async_client:
                async with manager(async_client, product, options) as connection:
                    if reject:
                        with pytest.raises(ConnectionClosedError) as exc:
                            await asyncio.wait_for(connection.recv_bytes(), 10)
                        assert exc.value.sent is not None and exc.value.sent.code == 1009
                    else:
                        assert await asyncio.wait_for(connection.recv_bytes(), 10) == wire
    assert frames == []
    assert_compression(handshakes, compressed)


@pytest.mark.parametrize("product", PRODUCTS)
@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("options", [{}, {"max_size": None}], ids=["absent-limit", "explicit-unlimited"])
async def test_generated_unlimited_default(
    product: str, mode: Literal["sync", "async"], options: WebSocketConnectionOptions
) -> None:
    await receive_once(product, mode, options, compressed=False)


@pytest.mark.parametrize("product", PRODUCTS)
@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_generated_default_receives_more_than_native_message_limit(
    product: str, mode: Literal["sync", "async"]
) -> None:
    event: dict[str, object] = {"event_id": "event_1", "delta": "x" * (2 * 1024 * 1024)}
    if product.startswith("live") or product == "translation":
        event.update(type="session.output_transcript.delta", start_ms=0, end_ms=200)
    elif product == "transcription":
        event.update(type="conversation.item.input_audio_transcription.delta", item_id="item_1", content_index=0)
    else:
        event.update(
            type="response.output_text.delta",
            response_id="resp_1",
            item_id="item_1",
            output_index=0,
            content_index=0,
            sequence_number=1,
            logprobs=[],
        )
    await receive_once(product, mode, {}, compressed=False, wire=json.dumps(event).encode())


@pytest.mark.parametrize("product", ["realtime", "live"])
@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    ("options", "compressed"),
    [
        pytest.param({"max_size": 0}, True, id="zero-limit-native-default"),
        pytest.param({"max_size": 512}, True, id="finite-limit-native-default"),
        pytest.param({"compression": "deflate"}, True, id="explicit-deflate-unlimited"),
        pytest.param({"compression": None}, False, id="explicit-off-unlimited"),
        pytest.param({"max_size": 512, "compression": None}, False, id="explicit-off-finite"),
        pytest.param({"max_size": 512, "compression": "deflate"}, True, id="explicit-deflate-finite"),
        pytest.param(
            {"extensions": [ClientPerMessageDeflateFactory()]},
            True,
            id="explicit-extension-unlimited",
        ),
    ],
)
async def test_generated_respects_compression_options(
    product: str, mode: Literal["sync", "async"], options: WebSocketConnectionOptions, compressed: bool
) -> None:
    await receive_once(product, mode, options, compressed)


@pytest.mark.parametrize("product", ["realtime", "live"])
@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    ("options", "compressed"),
    [
        pytest.param({}, False, id="absent-limit"),
        pytest.param({"max_size": None}, False, id="explicit-unlimited"),
        pytest.param({"max_size": 512}, True, id="finite-limit-native-default"),
        pytest.param({"compression": "deflate"}, True, id="explicit-deflate-unlimited"),
        pytest.param({"compression": None}, False, id="explicit-off-unlimited"),
        pytest.param({"extensions": [ClientPerMessageDeflateFactory()]}, True, id="explicit-extension-unlimited"),
    ],
)
async def test_generated_reconnect_preserves_compression_without_replay(
    product: str, mode: Literal["sync", "async"], options: WebSocketConnectionOptions, compressed: bool
) -> None:
    attempts: list[int] = []

    def on_reconnecting(event: ReconnectingEvent) -> None:
        assert event.close_code == 1011
        attempts.append(event.attempt)

    with compression_peer(product, reconnect=True) as (url, _wire, handshakes, frames):
        if mode == "sync":

            def recover() -> None:
                with OpenAI(
                    api_key="local",
                    base_url=url,
                    websocket_base_url=url.replace("http:", "ws:"),
                    http_client=httpx2.Client(trust_env=False),
                ) as client:
                    with manager(client, product, options, on_reconnecting) as connection:
                        connection.send_raw("before-close")
                        event = next(iter(connection))
                        assert event.event_id == "recovered"
                        connection.send_raw("after-reconnect")
                        assert connection.recv_bytes() == b"test.peer.received"

            await asyncio.wait_for(asyncio.to_thread(recover), 10)
        else:
            async with AsyncOpenAI(
                api_key="local",
                base_url=url,
                websocket_base_url=url.replace("http:", "ws:"),
                http_client=httpx2.AsyncClient(trust_env=False),
            ) as async_client:
                async with manager(async_client, product, options, on_reconnecting) as connection:
                    await connection.send_raw("before-close")
                    event = await asyncio.wait_for(anext(aiter(connection)), 10)
                    assert event.event_id == "recovered"
                    await connection.send_raw("after-reconnect")
                    assert await asyncio.wait_for(connection.recv_bytes(), 5) == b"test.peer.received"
    assert attempts == [1]
    assert frames == [(1, "before-close"), (2, "after-reconnect")]
    assert_compression(handshakes, compressed, count=2)
