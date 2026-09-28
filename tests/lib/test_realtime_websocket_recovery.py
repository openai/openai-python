from __future__ import annotations

import json
import asyncio
import threading
from urllib.parse import parse_qs, urlsplit

import httpx2
import pytest
from websockets.exceptions import ConnectionClosedError
from websockets.sync.server import ServerConnection

from openai import OpenAI, AsyncOpenAI, AzureOpenAI, AsyncAzureOpenAI
from openai.lib.azure import API_KEY_SENTINEL
from openai.types.websocket_reconnection import ReconnectingEvent, ReconnectingOverrides
from openai.types.realtime.realtime_error_event import RealtimeErrorEvent
from openai.types.realtime.input_audio_buffer_cleared_event import InputAudioBufferClearedEvent

from .responses.test_websocket_session import script_server


@pytest.fixture(autouse=True)
def bypass_loopback_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_PROXY", "127.0.0.1")
    monkeypatch.setenv("no_proxy", "127.0.0.1")


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("profile", ["direct-recv", "no-callback", "caller-abort", "nonrecoverable", "clean"])
async def test_realtime_recovery_stops_without_an_extra_upgrade(mode: str, profile: str) -> None:
    attempts: list[int] = []
    code = {"nonrecoverable": 1008, "clean": 1000}.get(profile, 1011)

    def script(socket: ServerConnection) -> None:
        socket.close(code, "synthetic close")

    def on_retry(event: ReconnectingEvent) -> ReconnectingOverrides:
        attempts.append(event.attempt)
        return {"abort": True}

    with script_server(script) as url:
        callback = None if profile == "no-callback" else on_retry
        if mode == "sync":
            with OpenAI(
                api_key="fake-realtime-key", base_url=url, http_client=httpx2.Client(trust_env=False)
            ) as client:
                with client.realtime.connect(model="gpt-realtime", on_reconnecting=callback, initial_delay=0) as conn:
                    if profile == "clean":
                        assert list(conn) == []
                    else:
                        with pytest.raises(ConnectionClosedError) as error:
                            if profile == "direct-recv":
                                conn.recv()
                            else:
                                next(iter(conn))
                        assert error.value.rcvd is not None and error.value.rcvd.code == code
        else:
            async with AsyncOpenAI(
                api_key="fake-realtime-key", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
            ) as async_client:
                async with async_client.realtime.connect(
                    model="gpt-realtime", on_reconnecting=callback, initial_delay=0
                ) as async_conn:
                    if profile == "clean":
                        assert [e async for e in async_conn] == []
                    else:
                        with pytest.raises(ConnectionClosedError) as async_error:
                            if profile == "direct-recv":
                                await asyncio.wait_for(async_conn.recv(), timeout=5)
                            else:
                                await asyncio.wait_for(async_conn.__aiter__().__anext__(), timeout=5)
                        assert async_error.value.rcvd is not None and async_error.value.rcvd.code == code
    assert attempts == ([1] if profile == "caller-abort" else [])


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_realtime_admission_errors_do_not_reset_the_retry_budget(mode: str) -> None:
    attempts: list[int] = []
    seen: list[RealtimeErrorEvent] = []

    def script(socket: ServerConnection) -> None:
        socket.send(
            json.dumps(
                {
                    "type": "error",
                    "event_id": "fake-error",
                    "error": {"type": "server_error", "code": "busy", "message": "Synthetic busy"},
                }
            )
        )
        socket.close(1011, "synthetic close")

    def on_retry(event: ReconnectingEvent) -> None:
        assert event.close_code == 1011
        assert event.max_attempts == 2
        attempts.append(event.attempt)

    with script_server(script, expected_connections=3) as url:
        if mode == "sync":
            with OpenAI(
                api_key="fake-realtime-key", base_url=url, http_client=httpx2.Client(trust_env=False)
            ) as client:
                with client.realtime.connect(
                    model="gpt-realtime", on_reconnecting=on_retry, max_retries=2, initial_delay=0
                ) as conn:
                    with pytest.raises(ConnectionClosedError):
                        for event in conn:
                            assert isinstance(event, RealtimeErrorEvent)
                            seen.append(event)
                            assert len(seen) <= 3
        else:
            async with AsyncOpenAI(
                api_key="fake-realtime-key", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
            ) as client_async:
                async with client_async.realtime.connect(
                    model="gpt-realtime", on_reconnecting=on_retry, max_retries=2, initial_delay=0
                ) as async_conn:
                    with pytest.raises(ConnectionClosedError):
                        async for event in async_conn:
                            assert isinstance(event, RealtimeErrorEvent)
                            seen.append(event)
                            assert len(seen) <= 3
    assert attempts == [1, 2]
    assert [e.error.code for e in seen] == ["busy", "busy", "busy"]


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("provider", ["openai", "azure"])
async def test_realtime_replacement_refreshes_provider_and_preserves_connection_options(
    mode: str, provider: str
) -> None:
    credential = "fake-realtime-before"
    upgrades: list[str] = []

    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        target = urlsplit(socket.request.path)
        upgrades.append(socket.request.path)
        assert target.path.endswith("/customer/realtime")
        query = parse_qs(target.query)
        assert query["contract"] == ["socket"]
        assert query["tenant"] == ["sample"]
        assert socket.request.headers.get_all("Authorization") == [f"Bearer {credential}"]
        assert socket.request.headers.get("api-key") is None
        assert socket.request.headers["X-Realtime-Test"] == "connection"
        assert socket.request.headers.get("Sec-WebSocket-Extensions") is None
        if len(upgrades) == 1:
            socket.close(1011, "synthetic close")
        else:
            socket.send('{"type":"input_audio_buffer.cleared","event_id":"recovered"}')
            assert json.loads(socket.recv(timeout=5)) == {"type": "input_audio_buffer.clear", "event_id": "next"}

    def on_retry(event: ReconnectingEvent) -> None:
        nonlocal credential
        assert event.attempt == 1
        credential = "fake-realtime-after"

    def get_token() -> str:
        return credential

    async def get_async_token() -> str:
        return credential

    with script_server(script, expected_connections=2) as url:
        if mode == "sync":
            client = (
                AzureOpenAI(
                    api_key=API_KEY_SENTINEL,
                    azure_ad_token_provider=get_token,
                    azure_endpoint="https://origin.test",
                    websocket_base_url=f"{url.replace('http://', 'ws://')}/customer",
                    api_version="2024-01-01",
                    http_client=httpx2.Client(trust_env=False),
                )
                if provider == "azure"
                else OpenAI(
                    api_key=get_token,
                    base_url=f"{url}/customer?tenant=sample",
                    http_client=httpx2.Client(trust_env=False),
                )
            )
            with client:
                with client.realtime.connect(
                    model="gpt-realtime",
                    on_reconnecting=on_retry,
                    initial_delay=0,
                    extra_query={"contract": "socket", **({"tenant": "sample"} if provider == "azure" else {})},
                    extra_headers={"X-Realtime-Test": "connection"},
                    websocket_connection_options={"compression": None},
                ) as conn:
                    event = next(iter(conn))
                    assert isinstance(event, InputAudioBufferClearedEvent)
                    assert event.event_id == "recovered"
                    conn.input_audio_buffer.clear(event_id="next")
        else:
            async_client = (
                AsyncAzureOpenAI(
                    api_key=API_KEY_SENTINEL,
                    azure_ad_token_provider=get_token,
                    azure_endpoint="https://origin.test",
                    websocket_base_url=f"{url.replace('http://', 'ws://')}/customer",
                    api_version="2024-01-01",
                    http_client=httpx2.AsyncClient(trust_env=False),
                )
                if provider == "azure"
                else AsyncOpenAI(
                    api_key=get_async_token,
                    base_url=f"{url}/customer?tenant=sample",
                    http_client=httpx2.AsyncClient(trust_env=False),
                )
            )
            async with async_client:
                async with async_client.realtime.connect(
                    model="gpt-realtime",
                    on_reconnecting=on_retry,
                    initial_delay=0,
                    extra_query={"contract": "socket", **({"tenant": "sample"} if provider == "azure" else {})},
                    extra_headers={"X-Realtime-Test": "connection"},
                    websocket_connection_options={"compression": None},
                ) as async_conn:
                    async_event = await asyncio.wait_for(async_conn.__aiter__().__anext__(), timeout=5)
                    assert isinstance(async_event, InputAudioBufferClearedEvent)
                    assert async_event.event_id == "recovered"
                    await async_conn.input_audio_buffer.clear(event_id="next")
    assert len(upgrades) == 2 and upgrades[0] == upgrades[1]


async def test_realtime_cancelled_receive_preserves_next_event_and_socket() -> None:
    release = threading.Event()

    def script(socket: ServerConnection) -> None:
        assert release.wait(timeout=5)
        socket.send('{"type":"input_audio_buffer.cleared","event_id":"after-cancel"}')
        assert json.loads(socket.recv(timeout=5)) == {"type": "input_audio_buffer.clear", "event_id": "after-cancel"}

    with script_server(script) as url:
        async with AsyncOpenAI(
            api_key="fake-realtime-key", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
        ) as client:
            async with client.realtime.connect(model="gpt-realtime") as conn:
                receiving = asyncio.create_task(conn.recv())
                await asyncio.sleep(0)
                receiving.cancel()
                try:
                    with pytest.raises(asyncio.CancelledError):
                        await receiving
                finally:
                    release.set()
                event = await asyncio.wait_for(conn.recv(), timeout=5)
                assert isinstance(event, InputAudioBufferClearedEvent)
                assert event.event_id == "after-cancel"
                await conn.input_audio_buffer.clear(event_id="after-cancel")
