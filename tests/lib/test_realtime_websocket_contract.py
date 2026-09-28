from __future__ import annotations

import json
import asyncio
from urllib.parse import parse_qs, urlsplit

import httpx2
import pytest
from websockets.sync.client import ClientConnection
from websockets.sync.server import ServerConnection
from websockets.asyncio.client import ClientConnection as AsyncClientConnection

from openai import OpenAI, AsyncOpenAI
from openai._exceptions import WebSocketQueueFullError
from openai.types.websocket_reconnection import ReconnectingEvent
from openai.types.realtime.realtime_error_event import RealtimeErrorEvent
from openai.types.realtime.input_audio_buffer_cleared_event import InputAudioBufferClearedEvent

from .responses.test_websocket_session import script_server


@pytest.fixture(autouse=True)
def bypass_loopback_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_PROXY", "127.0.0.1")
    monkeypatch.setenv("no_proxy", "127.0.0.1")


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("base_query", ["", "?tenant=sample"], ids=["custom-path", "custom-path-and-query"])
async def test_realtime_error_keeps_connection_open(mode: str, base_query: str) -> None:
    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        target = urlsplit(socket.request.path)
        assert target.path == "/v1/customer/realtime"
        expected_query = {"model": ["gpt-realtime"], "contract": ["socket"]}
        if base_query:
            expected_query["tenant"] = ["sample"]
        assert parse_qs(target.query) == expected_query
        assert socket.request.headers.get_all("Authorization") == ["Bearer ek_fake_realtime"]
        assert socket.request.headers["X-Realtime-Test"] == "connection"
        assert socket.request.headers["X-Client-Only"] == "preserved"
        assert socket.request.headers.get("Sec-WebSocket-Extensions") is None
        assert json.loads(socket.recv(timeout=5)) == {
            "type": "input_audio_buffer.append",
            "event_id": "append-1",
            "audio": "AA==",
        }
        socket.send(
            json.dumps(
                {
                    "type": "error",
                    "event_id": "error-1",
                    "error": {
                        "type": "invalid_request_error",
                        "code": "invalid_audio",
                        "param": "audio",
                        "message": "Synthetic audio rejected",
                        "event_id": "append-1",
                    },
                }
            )
        )
        # A documented recoverable error must not close or replace the physical socket.
        assert json.loads(socket.recv(timeout=5)) == {"type": "input_audio_buffer.clear", "event_id": "clear-1"}
        socket.send(json.dumps({"type": "input_audio_buffer.cleared", "event_id": "clear-1", "future": {"kept": True}}))
        socket.send(' { "type": "realtime.future", "event_id": "future-1", "text": "東京🙂" }\n')
        # script_server verifies one connection, a clean caller close, and no extra sends.

    with script_server(script) as url:
        base_url = f"{url}/customer{base_query}"
        client_headers = {"X-Realtime-Test": "client", "X-Client-Only": "preserved"}
        if mode == "sync":
            with OpenAI(
                api_key="ek_fake_realtime",
                base_url=base_url,
                default_headers=client_headers,
                http_client=httpx2.Client(trust_env=False),
            ) as client:
                with client.realtime.connect(
                    model="gpt-realtime",
                    extra_query={"contract": "socket"},
                    extra_headers={"X-Realtime-Test": "connection"},
                    websocket_connection_options={"compression": None},
                ) as connection:
                    connection.input_audio_buffer.append(audio="AA==", event_id="append-1")
                    error = connection.recv()
                    assert isinstance(error, RealtimeErrorEvent)
                    assert (error.error.code, error.error.param, error.error.event_id) == (
                        "invalid_audio",
                        "audio",
                        "append-1",
                    )
                    connection.input_audio_buffer.clear(event_id="clear-1")
                    cleared = connection.recv()
                    assert isinstance(cleared, InputAudioBufferClearedEvent)
                    assert cleared.to_dict(exclude_unset=True) == {
                        "type": "input_audio_buffer.cleared",
                        "event_id": "clear-1",
                        "future": {"kept": True},
                    }
                    assert json.loads(connection.recv_bytes()) == {
                        "type": "realtime.future",
                        "event_id": "future-1",
                        "text": "東京🙂",
                    }
        else:
            async with AsyncOpenAI(
                api_key="ek_fake_realtime",
                base_url=base_url,
                default_headers=client_headers,
                http_client=httpx2.AsyncClient(trust_env=False),
            ) as async_client:
                async with async_client.realtime.connect(
                    model="gpt-realtime",
                    extra_query={"contract": "socket"},
                    extra_headers={"X-Realtime-Test": "connection"},
                    websocket_connection_options={"compression": None},
                ) as async_connection:
                    await async_connection.input_audio_buffer.append(audio="AA==", event_id="append-1")
                    async_error = await asyncio.wait_for(async_connection.recv(), timeout=5)
                    assert isinstance(async_error, RealtimeErrorEvent)
                    assert (async_error.error.code, async_error.error.param, async_error.error.event_id) == (
                        "invalid_audio",
                        "audio",
                        "append-1",
                    )
                    await async_connection.input_audio_buffer.clear(event_id="clear-1")
                    async_cleared = await asyncio.wait_for(async_connection.recv(), timeout=5)
                    assert isinstance(async_cleared, InputAudioBufferClearedEvent)
                    assert async_cleared.to_dict(exclude_unset=True) == {
                        "type": "input_audio_buffer.cleared",
                        "event_id": "clear-1",
                        "future": {"kept": True},
                    }
                    assert json.loads(await asyncio.wait_for(async_connection.recv_bytes(), timeout=5)) == {
                        "type": "realtime.future",
                        "event_id": "future-1",
                        "text": "東京🙂",
                    }


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_realtime_empty_manager_queue_keeps_budget_after_open(mode: str) -> None:
    opened = 0

    def script(socket: ServerConnection) -> None:
        nonlocal opened
        opened += 1
        if opened == 1:
            socket.close(code=1011, reason="synthetic restart")
            return
        # Let the iterator resume even if its connection lost the manager's
        # queue. Server-side inspection still proves exactly what was sent.
        socket.send('{"type": "input_audio_buffer.cleared", "event_id": "ready"}')
        assert json.loads(socket.recv(timeout=5)) == {"type": "input_audio_buffer.clear", "event_id": "queued"}

    with script_server(script, expected_connections=2) as url:
        if mode == "sync":
            with OpenAI(
                api_key="fake-realtime-key", base_url=url, http_client=httpx2.Client(trust_env=False)
            ) as client:

                def on_retry(_event: ReconnectingEvent) -> None:
                    manager.send({"type": "input_audio_buffer.clear", "event_id": "queued"})
                    with pytest.raises(WebSocketQueueFullError):
                        manager.send({"type": "input_audio_buffer.append", "audio": "AAAA" * 100})

                manager = client.realtime.connect(
                    model="gpt-realtime", max_queue_size=96, on_reconnecting=on_retry, initial_delay=0
                )
                with manager as connection:
                    event = next(iter(connection))
                    assert event.type == "input_audio_buffer.cleared"
        else:
            async with AsyncOpenAI(
                api_key="fake-realtime-key", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
            ) as client:

                def on_async_retry(_event: ReconnectingEvent) -> None:
                    async_manager.send({"type": "input_audio_buffer.clear", "event_id": "queued"})
                    with pytest.raises(WebSocketQueueFullError):
                        async_manager.send({"type": "input_audio_buffer.append", "audio": "AAAA" * 100})

                async_manager = client.realtime.connect(
                    model="gpt-realtime", max_queue_size=96, on_reconnecting=on_async_retry, initial_delay=0
                )
                async with async_manager as connection:
                    event = await asyncio.wait_for(anext(aiter(connection)), 5)
                    assert event.type == "input_audio_buffer.cleared"


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("preopen", [True, False], ids=["preopen-flush", "direct"])
async def test_realtime_recovery_never_replays_an_attempted_command(
    mode: str, preopen: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    opened = 0
    recorded: list[tuple[int, str]] = []

    def script(socket: ServerConnection) -> None:
        nonlocal opened
        opened += 1
        current = opened
        if current == 1:
            for _ in range(2 if preopen else 1):
                recorded.append((current, json.loads(socket.recv(timeout=5))["event_id"]))
            socket.close(code=1011, reason="synthetic restart")
            return
        socket.send('{"type": "input_audio_buffer.cleared", "event_id": "ready"}')
        for _ in range(2 if preopen else 1):
            recorded.append((current, json.loads(socket.recv(timeout=5))["event_id"]))

    # Fail after the real wire send: an exception cannot establish non-delivery.
    original = ClientConnection.send
    original_async = AsyncClientConnection.send

    def send_then_interrupt(self: ClientConnection, message: object, *args: object, **kwargs: object) -> None:
        original(self, message, *args, **kwargs)  # type: ignore[arg-type]
        if json.loads(message)["event_id"] == "attempted":  # type: ignore[arg-type]
            raise OSError("synthetic interruption after send")

    async def async_send_then_interrupt(
        self: AsyncClientConnection, message: object, *args: object, **kwargs: object
    ) -> None:
        await original_async(self, message, *args, **kwargs)  # type: ignore[arg-type]
        if json.loads(message)["event_id"] == "attempted":  # type: ignore[arg-type]
            raise OSError("synthetic interruption after send")

    if mode == "sync":
        monkeypatch.setattr(ClientConnection, "send", send_then_interrupt)
    else:
        monkeypatch.setattr(AsyncClientConnection, "send", async_send_then_interrupt)
    with script_server(script, expected_connections=2) as url:
        if mode == "sync":
            with OpenAI(
                api_key="fake-realtime-key", base_url=url, http_client=httpx2.Client(trust_env=False)
            ) as client:

                def on_retry(_event: ReconnectingEvent) -> None:
                    manager.send({"type": "input_audio_buffer.clear", "event_id": "during-recovery"})

                manager = client.realtime.connect(model="gpt-realtime", on_reconnecting=on_retry, initial_delay=0)
                if preopen:
                    for identity in ("first", "attempted", "unattempted"):
                        manager.send({"type": "input_audio_buffer.clear", "event_id": identity})
                with manager as connection:
                    if not preopen:
                        with pytest.raises(OSError, match="synthetic interruption after send"):
                            connection.send({"type": "input_audio_buffer.clear", "event_id": "attempted"})
                    assert next(iter(connection)).type == "input_audio_buffer.cleared"
        else:
            async with AsyncOpenAI(
                api_key="fake-realtime-key", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
            ) as client:

                def on_async_retry(_event: ReconnectingEvent) -> None:
                    async_manager.send({"type": "input_audio_buffer.clear", "event_id": "during-recovery"})

                async_manager = client.realtime.connect(
                    model="gpt-realtime", on_reconnecting=on_async_retry, initial_delay=0
                )
                if preopen:
                    for identity in ("first", "attempted", "unattempted"):
                        async_manager.send({"type": "input_audio_buffer.clear", "event_id": identity})
                async with async_manager as connection:
                    if not preopen:
                        with pytest.raises(OSError, match="synthetic interruption after send"):
                            await connection.send({"type": "input_audio_buffer.clear", "event_id": "attempted"})
                    event = await asyncio.wait_for(anext(aiter(connection)), 5)
                    assert event.type == "input_audio_buffer.cleared"
    expected = [(1, "first"), (1, "attempted"), (2, "unattempted"), (2, "during-recovery")]
    assert recorded == (expected if preopen else [(1, "attempted"), (2, "during-recovery")])
