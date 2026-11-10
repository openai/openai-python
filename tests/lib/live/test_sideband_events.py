from __future__ import annotations

import json

import httpx2
import pytest
from websockets.sync.server import ServerConnection

from openai import OpenAI, AsyncOpenAI
from openai.types.live.connect_server_event import (
    TransportFailed,
    TransportRinging,
    TransportAnswered,
    TransportDtmfSend,
    TransportDtmfReceived,
    SessionInputAudioAppend,
)
from openai.types.live.output_audio_delta_event import OutputAudioDeltaEvent

from ..responses.test_websocket_session import script_server


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_sideband_typed_events_and_cleanup(mode: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_PROXY", "127.0.0.1")
    monkeypatch.setenv("no_proxy", "127.0.0.1")
    frames = [
        {"type": "session.input_audio.append", "audio": "AAE="},
        {"type": "transport.dtmf.received", "event_id": "r1", "event": "5"},
        {"type": "transport.dtmf.send", "event_id": "s1", "event": "#", "client_event_id": "command1"},
        {"type": "transport.ringing", "event_id": "r2", "session_id": "live_test"},
        {"type": "transport.answered", "event_id": "a1", "session_id": "live_test"},
        {
            "type": "transport.failed",
            "event_id": "f1",
            "session_id": "live_test",
            "error": {
                "type": "call_error",
                "code": "provider_invite_failed",
                "message": "synthetic failure",
                "param": None,
            },
        },
        # Null is outside the server schema; retain the existing lenient decode behavior.
        {"type": "transport.dtmf.send", "event_id": "s2", "event": "#", "client_event_id": None},
        {"type": "transport.dtmf.send", "event_id": "s3", "event": "#"},
        {"type": "session.output_audio.delta", "delta": "AAE=", "start_ms": 10, "end_ms": 20},
        {"type": "session.closed", "event_id": "closed"},
        {"type": "future.transport.event", "marker": 42},
    ]

    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        assert socket.request.path == "/v1/live/sessions/live_test/attach"
        assert socket.request.headers["authorization"] == "Bearer synthetic"
        for frame in frames:
            socket.send(json.dumps(frame))

    with script_server(script) as url:
        if mode == "sync":
            with OpenAI(api_key="synthetic", base_url=url, http_client=httpx2.Client(trust_env=False)) as client:
                with client.live.sideband.connect(session_id="live_test") as connection:
                    events = [connection.recv() for _ in frames]
        else:
            async with AsyncOpenAI(
                api_key="synthetic", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
            ) as async_client:
                async with async_client.live.sideband.connect(session_id="live_test") as async_connection:
                    events = [await async_connection.recv() for _ in frames]

    assert isinstance(events[0], SessionInputAudioAppend) and events[0].audio == "AAE="
    assert isinstance(events[1], TransportDtmfReceived) and events[1].event == "5"
    assert isinstance(events[2], TransportDtmfSend) and events[2].client_event_id == "command1"
    assert isinstance(events[3], TransportRinging) and events[3].session_id == "live_test"
    assert isinstance(events[4], TransportAnswered) and events[4].session_id == "live_test"
    assert isinstance(events[5], TransportFailed) and events[5].error.message == "synthetic failure"
    assert isinstance(events[6], TransportDtmfSend) and events[6].client_event_id is None
    assert isinstance(events[7], TransportDtmfSend) and events[7].client_event_id is None
    assert isinstance(events[8], OutputAudioDeltaEvent)
    assert (events[8].delta, events[8].start_ms, events[8].end_ms) == ("AAE=", 10, 20)
    assert events[9].type == "session.closed"
    assert events[10].model_dump()["marker"] == 42
