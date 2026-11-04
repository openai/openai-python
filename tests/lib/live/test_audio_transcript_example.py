from __future__ import annotations

import json
import wave
import asyncio
from pathlib import Path

import pytest
from websockets.exceptions import ConnectionClosedOK
from websockets.sync.server import ServerConnection

from openai import OpenAIError
from examples.live.audio_transcript import run

from ..responses.test_websocket_session import script_server


@pytest.mark.parametrize("stage", ["startup", "audio", "requested"])
@pytest.mark.parametrize(
    "reason", ["close_requested", "expired", "content", "remote_hangup", "connection_lost", "error", "eof"]
)
async def test_audio_example_requires_its_requested_finalization(
    stage: str, reason: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    wav_path = tmp_path / "fixture.wav"
    with wave.open(str(wav_path), "wb") as wav:
        wav.setparams((1, 2, 24000, 0, "NONE", "not compressed"))
        wav.writeframes(bytes(24000 * 2 // 10))

    sent_closed = False
    received_close = False
    audio_messages = 0

    def script(socket: ServerConnection) -> None:
        nonlocal sent_closed, received_close, audio_messages

        def send_closed() -> None:
            nonlocal sent_closed
            sent_closed = True
            if reason == "eof":
                socket.close()
            elif reason == "error":
                socket.send('{"type": "error", "event_id": "failure", "message": "Synthetic test error"}')
            else:
                socket.send(json.dumps({"type": "session.closed", "event_id": "done", "reason": reason}))

        assert json.loads(socket.recv(timeout=3))["type"] == "session.start"
        if stage == "startup":
            send_closed()
        else:
            socket.send('{"type": "session.started", "event_id": "started", "session": {"id": "fixture"}}')
        # Leave the connection open after the terminal event. The client must
        # reject that event immediately, rather than waiting for transport EOF.
        try:
            while True:
                event = json.loads(socket.recv(timeout=3))
                if event["type"] == "session.input_audio.append":
                    audio_messages += 1
                    if stage == "audio" and not sent_closed:
                        send_closed()
                elif event["type"] == "session.close":
                    received_close = True
                    if stage == "requested":
                        # Final transcript data after close was requested must
                        # reach the caller before the confirmed result returns.
                        socket.send(
                            json.dumps(
                                {
                                    "type": "session.output_transcript.delta",
                                    "event_id": "text",
                                    "delta": "Final fixture transcript.",
                                    "start_ms": 0,
                                    "end_ms": 100,
                                }
                            )
                        )
                        send_closed()
        except ConnectionClosedOK:
            return

    monkeypatch.setenv("OPENAI_API_KEY", "fake-transcript-fixture-key")
    monkeypatch.setenv("NO_PROXY", "127.0.0.1")
    monkeypatch.setenv("no_proxy", "127.0.0.1")
    # The sample constructs its own client; restrict this fixture to loopback.
    for name in ("ALL_PROXY", "all_proxy", "HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy"):
        monkeypatch.delenv(name, raising=False)
    with script_server(script) as url:
        monkeypatch.setenv("OPENAI_BASE_URL", url)
        if stage == "requested" and reason == "close_requested":
            result = await asyncio.wait_for(run(wav_path, model="fixture-model", listen_seconds=0), timeout=1)
            assert any(segment.text == "Final fixture transcript." for segment in result)
        else:
            # recv() can report transport EOF directly while awaiting startup;
            # all terminal paths must fail instead of returning partial text.
            with pytest.raises((OpenAIError, ConnectionClosedOK)):
                await asyncio.wait_for(run(wav_path, model="fixture-model", listen_seconds=0), timeout=1)
    assert sent_closed
    assert received_close == (stage == "requested")
    if stage == "startup":
        assert audio_messages == 0
    elif stage == "requested":
        assert audio_messages == 5
    else:
        assert 1 <= audio_messages <= 5
