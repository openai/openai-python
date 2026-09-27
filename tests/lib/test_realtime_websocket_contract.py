from __future__ import annotations

import json
import asyncio
from urllib.parse import parse_qs, urlsplit

import httpx2
import pytest
from websockets.sync.server import ServerConnection

from openai import OpenAI, AsyncOpenAI
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
