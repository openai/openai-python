from __future__ import annotations

import sys
import runpy
import base64
import asyncio
from types import SimpleNamespace
from typing import Any
from pathlib import Path
from contextlib import suppress
from unittest.mock import Mock, AsyncMock

import pytest


class FakeStream:
    def __init__(self, **_kwargs: Any) -> None:
        self.active = False
        self.closed = False
        self.frames: list[bytes] = []

    def start(self) -> None:
        self.active = True

    def capture(self, frame: bytes) -> None:
        if self.active:
            self.frames.append(frame)

    @property
    def read_available(self) -> int:
        return 480 if self.frames else 0

    def read(self, _size: int) -> tuple[bytes, bool]:
        assert self.active
        return self.frames.pop(0), False

    def abort(self) -> None:
        self.active = False

    def stop(self) -> None:
        self.active = False

    def close(self) -> None:
        self.active = False
        self.closed = True


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch) -> Any:
    # Load the complete example with UI/audio stand-ins: these optional example
    # dependencies must not open devices or be required by the SDK test suite.
    ui = Mock()
    ui.App.__getitem__ = Mock(return_value=object)
    modules = {
        "textual": Mock(),
        "textual.app": ui,
        "textual.widgets": SimpleNamespace(Button=object, Static=object, RichLog=object),
        "textual.reactive": SimpleNamespace(reactive=Mock(return_value=False)),
        "textual.containers": Mock(),
        "audio_util": SimpleNamespace(CHANNELS=1, SAMPLE_RATE=24000, AudioPlayerAsync=Mock()),
        "sounddevice": SimpleNamespace(query_devices=Mock(return_value=[]), InputStream=Mock(side_effect=FakeStream)),
    }
    for name, module in modules.items():
        monkeypatch.setitem(sys.modules, name, module)
    monkeypatch.setattr("openai.AsyncOpenAI", Mock())
    namespace = runpy.run_path(str(Path(__file__).parents[1] / "examples/realtime/push_to_talk_app.py"))
    instance = namespace["RealtimeApp"]()
    instance.stream_factory = modules["sounddevice"].InputStream
    instance.query_one = Mock(return_value=SimpleNamespace(is_recording=False))
    instance.connection = SimpleNamespace(
        send=AsyncMock(),
        input_audio_buffer=SimpleNamespace(append=AsyncMock(), commit=AsyncMock()),
        response=SimpleNamespace(create=AsyncMock()),
    )
    instance.connected.set()
    return instance


async def tick() -> None:
    # Yield to the microphone worker without depending on wall-clock timing.
    for _ in range(5):
        await asyncio.sleep(0)


async def cancel(task: asyncio.Task[None]) -> None:
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task


async def test_recording_starts_and_stops_capture(app: Any) -> None:
    task = asyncio.create_task(app.send_mic_audio())
    try:
        await tick()
        app.stream_factory.assert_not_called()

        await app.on_key(SimpleNamespace(key="k"))
        await tick()
        first = app._mic_stream
        assert first.active
        first.capture(b"first recording")
        await tick()
        app.connection.input_audio_buffer.append.assert_awaited_once_with(
            audio=base64.b64encode(b"first recording").decode()
        )

        first.capture(b"unread previous recording")
        await app.on_key(SimpleNamespace(key="k"))
        assert first.closed
        assert not first.active
        assert not app.query_one().is_recording
        first.capture(b"while stopped")

        # Restart without yielding, so even quick toggles discard the old stream.
        await app.on_key(SimpleNamespace(key="k"))
        await tick()
        second = app._mic_stream
        assert second is not first
        assert second.active
        second.capture(b"second recording")
        await tick()
        assert [
            base64.b64decode(call.kwargs["audio"]) for call in app.connection.input_audio_buffer.append.await_args_list
        ] == [
            b"first recording",
            b"second recording",
        ]
    finally:
        await cancel(task)
    assert second.closed


async def test_stop_while_waiting_for_connection_does_not_start_capture(app: Any) -> None:
    app.connected.clear()
    task = asyncio.create_task(app.send_mic_audio())
    try:
        await app.on_key(SimpleNamespace(key="k"))
        await tick()
        await app.on_key(SimpleNamespace(key="k"))
        app.connected.set()
        await tick()
        assert app._mic_stream is None
        assert not app.query_one().is_recording
        app.connection.input_audio_buffer.append.assert_not_awaited()
    finally:
        await cancel(task)


async def test_manual_turn_commits_after_capture_stops(app: Any) -> None:
    app.session = SimpleNamespace(audio=SimpleNamespace(input=SimpleNamespace(turn_detection=None)))
    task = asyncio.create_task(app.send_mic_audio())
    try:
        await app.on_key(SimpleNamespace(key="k"))
        await tick()
        stream = app._mic_stream

        async def commit() -> None:
            assert stream.closed
            assert not stream.active

        app.connection.input_audio_buffer.commit.side_effect = commit
        await app.on_key(SimpleNamespace(key="k"))
        app.connection.input_audio_buffer.commit.assert_awaited_once()
        app.connection.response.create.assert_awaited_once()
    finally:
        await cancel(task)


async def test_send_error_closes_capture(app: Any) -> None:
    app.connection.input_audio_buffer.append.side_effect = RuntimeError("fake send failure")
    task = asyncio.create_task(app.send_mic_audio())
    try:
        await app.on_key(SimpleNamespace(key="k"))
        await tick()
        stream = app._mic_stream
        stream.capture(b"recorded audio")
        with pytest.raises(RuntimeError, match="fake send failure"):
            await asyncio.wait_for(task, timeout=1)
        assert stream.closed
        assert not stream.active
    finally:
        if not task.done():
            await cancel(task)


async def test_stop_during_upload_closes_capture_immediately(app: Any) -> None:
    uploading = asyncio.Event()
    finish_upload = asyncio.Event()

    async def append(*, audio: str) -> None:
        assert base64.b64decode(audio) == b"recorded audio"
        uploading.set()
        await finish_upload.wait()

    app.connection.input_audio_buffer.append.side_effect = append
    task = asyncio.create_task(app.send_mic_audio())
    try:
        await app.on_key(SimpleNamespace(key="k"))
        await tick()
        stream = app._mic_stream
        stream.capture(b"recorded audio")
        await asyncio.wait_for(uploading.wait(), timeout=1)
        await app.on_key(SimpleNamespace(key="k"))
        assert stream.closed
        assert not stream.active
        finish_upload.set()
        await tick()
        assert not app.query_one().is_recording
        app.connection.input_audio_buffer.append.assert_awaited_once()
    finally:
        await cancel(task)
