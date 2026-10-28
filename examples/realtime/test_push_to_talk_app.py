"""Run with pytest after installing the push_to_talk_app.py sample dependencies."""

from __future__ import annotations

import sys
import asyncio
from types import ModuleType, SimpleNamespace
from typing import Any
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("textual")
pytest.importorskip("pydub")


@pytest.fixture()
def app_module(monkeypatch: pytest.MonkeyPatch) -> Any:
    started = asyncio.Event()

    class InputStream:
        def __init__(self, **_kwargs: Any):
            self.open = True
            self.samples = 480

        def start(self) -> None:
            started.set()

        @property
        def read_available(self) -> int:
            return self.samples

        def read(self, frames: int) -> tuple[Any, bool]:
            assert self.open
            self.samples -= frames
            return np.zeros((frames, 1), dtype=np.int16), False

        def abort(self) -> None:
            self.open = False

        def close(self) -> None:
            self.open = False

    class OutputStream:
        def __init__(self, callback: Any, **_kwargs: Any):
            self.callback = callback

        def start(self) -> None:
            pass

        def stop(self) -> None:
            pass

        def close(self) -> None:
            pass

    # Replace only audio device bindings; import the actual UI, player, and SDK.
    device = ModuleType("sounddevice")
    monkeypatch.setattr(device, "InputStream", InputStream, raising=False)
    monkeypatch.setattr(device, "OutputStream", OutputStream, raising=False)
    monkeypatch.setattr(device, "query_devices", lambda: {}, raising=False)
    pyaudio = ModuleType("pyaudio")
    monkeypatch.setattr(pyaudio, "paInt16", 8, raising=False)
    monkeypatch.setitem(sys.modules, "sounddevice", device)
    monkeypatch.setitem(sys.modules, "pyaudio", pyaudio)
    monkeypatch.syspath_prepend(str(Path(__file__).parent))
    monkeypatch.setenv("OPENAI_API_KEY", "test-only")
    # Offline tests never need the user's configured proxy.
    for name in ("ALL_PROXY", "HTTPS_PROXY", "HTTP_PROXY", "all_proxy", "https_proxy", "http_proxy"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.delitem(sys.modules, "audio_util", raising=False)
    monkeypatch.delitem(sys.modules, "push_to_talk_app", raising=False)
    import push_to_talk_app

    yield push_to_talk_app, started
    sys.modules.pop("audio_util", None)
    sys.modules.pop("push_to_talk_app", None)


def test_player_truncates_partial_and_queued_items(app_module: Any) -> None:
    module, _ = app_module
    player = module.AudioPlayerAsync()
    player.add_data(bytes(1920), response_id="r1", item_id="first", content_index=0)
    player.add_data(bytes(1920), response_id="r2", item_id="second", content_index=0)
    out = np.empty((480, 1), dtype=np.int16)
    player.stream.callback(out, 480, None, None)
    player.finish_response("r1")
    player.finish_response("r2")
    assert player.stop() == [(("r1", "first", 0), 480), (("r2", "second", 0), 0)]
    assert player.stop() == []


def test_finished_playback_does_not_accumulate(app_module: Any) -> None:
    module, _ = app_module
    player = module.AudioPlayerAsync()
    out = np.empty((480, 1), dtype=np.int16)
    for index in range(500):
        response_id = f"r{index}"
        player.add_data(bytes(960), response_id=response_id, item_id=f"i{index}", content_index=0)
        player.finish_response(response_id)
        player.stream.callback(out, 480, None, None)
    assert not player._played_by_item
    assert not player._finished_responses
    assert player.stop() == []


@pytest.mark.asyncio
@pytest.mark.parametrize("stop_before_cancel", [False, True])
async def test_capture_starts_before_blocked_cancel_but_sends_after(app_module: Any, stop_before_cancel: bool) -> None:
    module, mic_started = app_module
    app = module.RealtimeApp()
    status = SimpleNamespace(is_recording=False)
    app.query_one = lambda *_args, **_kwargs: status
    sent: list[str] = []
    waiting = asyncio.Event()
    release = asyncio.Event()

    async def cancel(**_kwargs: Any) -> None:
        waiting.set()
        await release.wait()
        sent.append("cancel")

    async def truncate(**kwargs: Any) -> None:
        sent.append("truncate")
        assert kwargs == {"item_id": "assistant", "content_index": 0, "audio_end_ms": 20}

    async def append(**_kwargs: Any) -> None:
        sent.append("append")

    app.connection = SimpleNamespace(
        response=SimpleNamespace(cancel=cancel),
        conversation=SimpleNamespace(item=SimpleNamespace(truncate=truncate)),
        input_audio_buffer=SimpleNamespace(append=append),
    )
    app.connected.set()
    app._active_response_id = "response"
    app.audio_player.add_data(bytes(1920), response_id="response", item_id="assistant", content_index=0)
    app.audio_player.stream.callback(np.empty((480, 1), dtype=np.int16), 480, None, None)
    mic = asyncio.create_task(app.send_mic_audio())
    key = asyncio.create_task(app.on_key(SimpleNamespace(key="k")))
    try:
        await asyncio.wait_for(waiting.wait(), 2)
        await asyncio.wait_for(mic_started.wait(), 2)
        assert status.is_recording
        assert not sent
        if stop_before_cancel:
            await app.on_key(SimpleNamespace(key="k"))
            assert app._mic_stream is None
        release.set()
        await asyncio.wait_for(key, 2)
        for _ in range(100):
            if "append" in sent:
                break
            await asyncio.sleep(0)
        assert sent == (["cancel", "truncate"] if stop_before_cancel else ["cancel", "truncate", "append"])
    finally:
        release.set()
        mic.cancel()
        await asyncio.gather(mic, return_exceptions=True)
        await app.client.close()
        assert app._mic_stream is None


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["normal", "abnormal", "unsent", "cancellation"])
async def test_disconnect_exits_and_user_cancellation_is_preserved(app_module: Any, failure: str) -> None:
    from websockets.exceptions import ConnectionClosedError

    from openai import WebSocketConnectionClosedError

    module, _ = app_module
    app = module.RealtimeApp()
    exited: list[dict[str, Any]] = []
    app.exit = lambda **kwargs: exited.append(kwargs)

    async def events() -> None:
        if failure == "abnormal":
            raise ConnectionClosedError(None, None)
        if failure == "unsent":
            raise WebSocketConnectionClosedError("fixture", unsent_messages=[])
        if failure == "cancellation":
            raise asyncio.CancelledError()

    app._receive_realtime_events = events
    try:
        if failure == "cancellation":
            with pytest.raises(asyncio.CancelledError):
                await app.handle_realtime_connection()
            assert not exited
        else:
            await app.handle_realtime_connection()
            assert exited == [{"return_code": 1, "message": "The Realtime connection closed."}]
    finally:
        await app.client.close()
