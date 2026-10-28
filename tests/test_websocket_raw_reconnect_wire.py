from __future__ import annotations

import json
import asyncio
import threading
from queue import Queue
from typing import Any, Iterator

import httpx2
import pytest
from websockets.sync.server import ServerConnection, serve

from openai import OpenAI, AsyncOpenAI, WebSocketConnectionClosedError
from openai.types.websocket_reconnection import ReconnectingEvent

from .lib.test_websocket_redirects import (
    RECONNECTING_RESOURCES,
    options,
    resource,
    unexpected_http,
    async_http_client,
)

PAYLOADS = [
    pytest.param('{"type":"synthetic.raw","text":"é"}', id="text"),
    pytest.param('{"type":"synthetic.raw","text":"é"}'.encode(), id="binary-json"),
    pytest.param(b"\x00\xff\x80\x01", id="binary"),
]


@pytest.fixture
def recovery_peer(monkeypatch: pytest.MonkeyPatch) -> Iterator[tuple[str, Queue[str | bytes]]]:
    monkeypatch.setenv("NO_PROXY", "*")
    monkeypatch.setenv("no_proxy", "*")
    seen: Queue[str | bytes] = Queue()
    handshakes = 0

    def handle(socket: ServerConnection) -> None:
        nonlocal handshakes
        handshakes += 1
        seen.put(socket.recv(timeout=3))
        if handshakes == 1:
            socket.close(1012, "service restart")
        else:
            socket.send('{"type":"synthetic.progress","event_id":"fake-event"}')

    with serve(handle, "127.0.0.1", 0) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            yield f"ws://127.0.0.1:{server.socket.getsockname()[1]}/v1", seen
        finally:
            server.shutdown()
            thread.join(timeout=5)
            assert not thread.is_alive()


def connection_options(client: Any, name: str) -> dict[str, Any]:
    params = options(client, name)
    if name == "realtime":
        params["model"] = "fake-model"
    return params


@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
@pytest.mark.parametrize("payload", PAYLOADS)
def test_raw_message_keeps_bytes_and_opcode_after_recovery(
    recovery_peer: tuple[str, Queue[str | bytes]], name: str, payload: str | bytes
) -> None:
    url, seen = recovery_peer
    with OpenAI(
        api_key="fake-key",
        websocket_base_url=url,
        http_client=httpx2.Client(transport=httpx2.MockTransport(unexpected_http)),
    ) as client:

        def retry(_event: ReconnectingEvent) -> None:
            connection.send_raw(payload)

        with resource(client, name).connect(
            **connection_options(client, name), on_reconnecting=retry, max_retries=1, initial_delay=0
        ) as connection:
            connection.send_raw(payload)
            next(iter(connection))
    assert seen.get(timeout=1) == payload
    assert seen.get(timeout=1) == payload


@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
@pytest.mark.parametrize("payload", PAYLOADS)
async def test_async_raw_message_keeps_bytes_and_opcode_after_recovery(
    recovery_peer: tuple[str, Queue[str | bytes]], name: str, payload: str | bytes
) -> None:
    url, seen = recovery_peer
    pending: list[asyncio.Task[None]] = []
    async with AsyncOpenAI(api_key="fake-key", websocket_base_url=url, http_client=async_http_client()) as client:

        def retry(_event: ReconnectingEvent) -> None:
            pending.append(asyncio.create_task(connection.send_raw(payload)))

        async with resource(client, name).connect(
            **connection_options(client, name), on_reconnecting=retry, max_retries=1, initial_delay=0.01
        ) as connection:
            await connection.send_raw(payload)
            await asyncio.wait_for(anext(aiter(connection)), timeout=4)
            await asyncio.gather(*pending)
    assert seen.get(timeout=1) == payload
    assert seen.get(timeout=1) == payload


@pytest.mark.parametrize("name", RECONNECTING_RESOURCES)
def test_raw_frames_are_available_after_recovery_aborts(
    recovery_peer: tuple[str, Queue[str | bytes]], name: str
) -> None:
    url, seen = recovery_peer
    frames: list[str | bytes] = ["first", b"\x00\xff\x80", b'{"type":"synthetic.raw"}', "last"]
    with OpenAI(
        api_key="fake-key",
        websocket_base_url=url,
        http_client=httpx2.Client(transport=httpx2.MockTransport(unexpected_http)),
    ) as client:

        def abort(_event: ReconnectingEvent) -> dict[str, bool]:
            for frame in frames:
                connection.send_raw(frame)
            return {"abort": True}

        with resource(client, name).connect(
            **connection_options(client, name), on_reconnecting=abort, max_retries=1, initial_delay=0
        ) as connection:
            connection.send_raw("original")
            with pytest.raises(WebSocketConnectionClosedError) as caught:
                next(iter(connection))
    assert seen.get(timeout=1) == "original"
    assert caught.value.unsent_frames == frames
    assert caught.value.unsent_messages == ["first", '{"type":"synthetic.raw"}', "last"]


def test_text_messages_preserve_their_list_identity() -> None:
    messages = ["one", "two"]
    error = WebSocketConnectionClosedError("closed", unsent_messages=messages)
    legacy: list[str] = error.unsent_messages
    assert legacy is messages
    assert error.unsent_frames is messages


def test_error_attributes_do_not_render_queued_frames() -> None:
    frames: list[str | bytes] = [
        "fake-text-customer-content",
        b"fake-valid-binary-content",
        b"\xfffake-opaque-binary-content",
    ]
    error = WebSocketConnectionClosedError("closed", unsent_messages=frames)
    for snapshot in (repr(vars(error)), json.dumps(vars(error), default=str)):
        assert "fake-text-customer-content" not in snapshot
        assert "fake-valid-binary-content" not in snapshot
        assert "fake-opaque-binary-content" not in snapshot
    assert error.unsent_frames is frames
    assert error.unsent_messages == ["fake-text-customer-content", "fake-valid-binary-content"]


def test_recovery_lists_keep_legacy_aliasing_and_independent_assignment() -> None:
    messages = ["one", "two"]
    error = WebSocketConnectionClosedError("closed", unsent_messages=messages)
    error.unsent_messages.append("three")
    assert error.unsent_frames is messages
    assert messages == ["one", "two", "three"]
    replaced = ["replacement"]
    error.unsent_messages = replaced
    assert error.unsent_messages is replaced
    assert error.unsent_frames is messages
    binary: list[str | bytes] = [b"\xfffake-binary", "last"]
    error.unsent_frames = binary
    assert error.unsent_frames is binary
    assert error.unsent_messages is replaced


def test_subclass_can_read_and_write_inherited_recovery_messages() -> None:
    class ClosedDuringReconnect(WebSocketConnectionClosedError):
        def retry_messages(self) -> list[str]:
            messages: list[str] = self.unsent_messages
            self.unsent_messages = messages + ["retry"]
            return self.unsent_messages

    error = ClosedDuringReconnect("closed", unsent_messages=["text"])
    assert error.retry_messages() == ["text", "retry"]


def test_subclass_can_set_legacy_messages_before_parent_init() -> None:
    early = ["fake-early-message"]
    final = ["fake-constructor-message"]

    class ClosedDuringReconnect(WebSocketConnectionClosedError):
        def __init__(self) -> None:
            self.unsent_messages = early
            assert self.unsent_messages is early
            super().__init__("closed", unsent_messages=final)

    error = ClosedDuringReconnect()
    assert error.unsent_messages is final
    assert error.unsent_frames is final
