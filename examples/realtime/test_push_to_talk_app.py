"""Run with pytest after installing the push_to_talk_app.py sample dependencies."""

from __future__ import annotations

import sys
import asyncio
import importlib
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
            self._callback = callback
            self.time = 0.0
            self.buffered = b""
            self.emitted = b""

        def callback(self, out: Any, frames: int, timing: Any, status: Any) -> None:
            if timing is None:
                # The existing tests model immediately played callback audio.
                start = self.time
                self.time += frames / module_rate
                timing = SimpleNamespace(outputBufferDacTime=start, currentTime=self.time)
            self._callback(out, frames, timing, status)

        def start(self) -> None:
            pass

        def stop(self) -> None:
            # PortAudio stop plays pending buffers; abort discards them.
            self.emitted += self.buffered
            self.buffered = b""

        def abort(self) -> None:
            self.buffered = b""

        def close(self) -> None:
            pass

    # Replace only audio device bindings; import the actual UI, player, and SDK.
    module_rate = 24000
    device = ModuleType("sounddevice")

    def query_devices() -> dict[str, str]:
        return {}

    monkeypatch.setattr(device, "InputStream", InputStream, raising=False)
    monkeypatch.setattr(device, "OutputStream", OutputStream, raising=False)
    monkeypatch.setattr(device, "query_devices", query_devices, raising=False)
    pyaudio = ModuleType("pyaudio")
    monkeypatch.setattr(pyaudio, "paInt16", 8, raising=False)
    monkeypatch.setitem(sys.modules, "sounddevice", device)
    monkeypatch.setitem(sys.modules, "pyaudio", pyaudio)
    monkeypatch.setattr(sys, "path", [str(Path(__file__).parent), *sys.path])
    monkeypatch.setenv("OPENAI_API_KEY", "test-only")
    # Offline tests never need the user's configured proxy.
    for name in ("ALL_PROXY", "HTTPS_PROXY", "HTTP_PROXY", "all_proxy", "https_proxy", "http_proxy"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.delitem(sys.modules, "audio_util", raising=False)
    monkeypatch.delitem(sys.modules, "push_to_talk_app", raising=False)
    push_to_talk_app = importlib.import_module("push_to_talk_app")
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
    assert not player._scheduled
    assert player.stop() == []


def test_interrupt_discards_device_buffered_audio(app_module: Any) -> None:
    module, _ = app_module
    player = module.AudioPlayerAsync()
    player.add_data(bytes(1920), response_id="r1", item_id="first", content_index=0)
    player.stream.buffered = b"assistant audio that has not reached the speaker"
    assert player.stop(interrupted_response_id="r1") == [(("r1", "first", 0), 0)]
    assert not player.stream.emitted
    # stop() clears the fake device buffer through abort(); ty retains the earlier literal.
    assert not player.stream.buffered  # ty: ignore[redundant-condition]


@pytest.mark.parametrize("at,expected_frames", [(0.99, 0), (1.01, 240), (1.03, None)])
def test_final_device_buffer_remains_owned_until_dac_finishes(
    app_module: Any, at: float, expected_frames: int | None
) -> None:
    module, _ = app_module
    player = module.AudioPlayerAsync()
    player.add_data(bytes(960), response_id="done", item_id="last", content_index=0)
    player.stream.time = 0.98
    player.stream.callback(
        np.empty((480, 1), dtype=np.int16),
        480,
        SimpleNamespace(currentTime=0.98, outputBufferDacTime=1.0),
        None,
    )
    player.finish_response("done")
    player.stream.time = at
    assert player.stop() == ([] if expected_frames is None else [(("done", "last", 0), expected_frames)])
    assert not player._played_by_item
    assert not player._finished_responses


@pytest.mark.asyncio
@pytest.mark.parametrize("stage", ["transcript-first", "done-dac-pending", "done-dac-played"])
async def test_transcript_interruption_tracks_only_unheard_content(app_module: Any, stage: str) -> None:
    module, _ = app_module
    app = module.RealtimeApp()
    status = SimpleNamespace(is_recording=False)
    display: list[str] = []
    sent: list[tuple[str, dict[str, Any]]] = []

    class Log:
        def clear(self) -> None:
            display.clear()

        def write(self, text: str) -> None:
            display.append(text)

    def query_one(*args: Any, **_kwargs: Any) -> Any:
        return status if args[0] is module.AudioStatusIndicator else Log()

    async def update(**_kwargs: Any) -> None:
        pass

    async def cancel(**kwargs: Any) -> None:
        sent.append(("cancel", kwargs))

    async def truncate(**kwargs: Any) -> None:
        sent.append(("truncate", kwargs))

    class Connection:
        session = SimpleNamespace(update=update)
        response = SimpleNamespace(cancel=cancel)
        conversation = SimpleNamespace(item=SimpleNamespace(truncate=truncate))

        async def __aenter__(self) -> Any:
            return self

        async def __aexit__(self, *_args: Any) -> None:
            pass

        async def __aiter__(self) -> Any:
            yield SimpleNamespace(type="response.created", response=SimpleNamespace(id="r1"))
            yield SimpleNamespace(
                type="response.output_audio_transcript.delta",
                response_id="r1",
                item_id="only-text",
                content_index=0,
                delta="Unheard answer",
            )
            assert display == ["Unheard answer"]
            if stage != "transcript-first":
                yield SimpleNamespace(
                    type="response.output_audio.delta",
                    response_id="r1",
                    item_id="only-text",
                    content_index=0,
                    delta=module.base64.b64encode(bytes(960)),
                )
                player = app.audio_player
                player.stream.time = 0.98
                player.stream.callback(
                    np.empty((480, 1), dtype=np.int16),
                    480,
                    SimpleNamespace(currentTime=0.98, outputBufferDacTime=1.0),
                    None,
                )
                yield SimpleNamespace(
                    type="response.done",
                    response=SimpleNamespace(id="r1", status="completed"),
                )
                if stage == "done-dac-played":
                    player.stream.time = 1.03
            await app.on_key(SimpleNamespace(key="k"))
            await app.workers.wait_for_complete()
            if stage == "done-dac-played":
                assert display == ["Unheard answer"]
                assert sent == []
                return
            assert display == ["Response interrupted."]
            expected: list[tuple[str, dict[str, Any]]] = (
                [("cancel", {"response_id": "r1"})] if stage == "transcript-first" else []
            )
            expected.append(("truncate", {"item_id": "only-text", "content_index": 0, "audio_end_ms": 0}))
            assert sent == expected
            if stage == "transcript-first":
                yield SimpleNamespace(
                    type="response.output_audio.delta",
                    response_id="r1",
                    item_id="only-text",
                    content_index=0,
                    delta="AAAAAAAAAAA=",
                )
            assert not app.audio_player.playing
            assert sent == expected

    app.query_one = query_one
    client = app.client

    def connect(**_kwargs: Any) -> Connection:
        return Connection()

    app.client = SimpleNamespace(realtime=SimpleNamespace(connect=connect))
    try:
        await app._receive_realtime_events()
    finally:
        app._stop_mic_stream()
        await client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("blocked", ["commit", "create"])
@pytest.mark.parametrize("continuous", [False, True])
async def test_manual_send_backpressure_does_not_block_next_key_capture(
    app_module: Any, monkeypatch: pytest.MonkeyPatch, blocked: str, continuous: bool
) -> None:
    module, mic_started = app_module
    if continuous:
        # A real input device can always have another frame ready. This leaves
        # the sender contending for the lock when key release starts a commit.
        device = sys.modules["sounddevice"]

        def read_available(_stream: Any) -> int:
            return 480

        monkeypatch.setattr(device.InputStream, "read_available", property(read_available))
    app = module.RealtimeApp()
    waiting = asyncio.Event()
    release = asyncio.Event()
    appended = asyncio.Event()
    sent: list[str] = []

    async def append(**_kwargs: Any) -> None:
        sent.append("append")
        appended.set()

    async def write(name: str) -> None:
        if name == blocked:
            waiting.set()
            await release.wait()
        sent.append(name)

    async def commit() -> None:
        await write("commit")

    async def create() -> None:
        await write("create")

    async def already_connected() -> None:
        await asyncio.Future[None]()

    monkeypatch.setattr(app, "handle_realtime_connection", already_connected)
    app.connection = SimpleNamespace(
        input_audio_buffer=SimpleNamespace(append=append, commit=commit),
        response=SimpleNamespace(create=create),
    )
    app.connected.set()
    app.session = SimpleNamespace(audio=SimpleNamespace(input=SimpleNamespace(turn_detection=None)))
    async with app.run_test():
        app.post_message(module.events.Key("k", "k"))
        await asyncio.wait_for(appended.wait(), 2)
        mic_started.clear()
        appended.clear()
        # Real Textual key dispatch must remain available during a blocked write.
        app.post_message(module.events.Key("k", "k"))
        try:
            await asyncio.wait_for(waiting.wait(), 2)
            # The send lock is held, so later appends can only be from the
            # next recording after commit/create have finished.
            appended.clear()
            app.post_message(module.events.Key("k", "k"))
            await asyncio.wait_for(mic_started.wait(), 2)
            assert app.query_one(module.AudioStatusIndicator).is_recording
            prior = list(sent)
            if blocked == "commit":
                assert prior and set(prior) == {"append"}
            else:
                assert prior[-1] == "commit" and set(prior[:-1]) == {"append"}
            release.set()
            await asyncio.wait_for(appended.wait(), 2)
            if continuous:
                commit_index = sent.index("commit")
                assert set(sent[:commit_index]) == {"append"}
                assert sent[commit_index : commit_index + 2] == ["commit", "create"]
                assert sent[commit_index + 2 :] and set(sent[commit_index + 2 :]) == {"append"}
            else:
                assert sent == ["append", "commit", "create", "append"]
        finally:
            release.set()


@pytest.mark.asyncio
@pytest.mark.parametrize("stop_before_cancel", [False, True])
@pytest.mark.parametrize("manual_turn", [False, True])
async def test_capture_starts_before_blocked_cancel_but_sends_after(
    app_module: Any, stop_before_cancel: bool, manual_turn: bool
) -> None:
    module, mic_started = app_module
    app = module.RealtimeApp()
    status = SimpleNamespace(is_recording=False)
    display = ["spoken and unspoken output"]

    class Log:
        def clear(self) -> None:
            display.clear()

        def write(self, message: str) -> None:
            display.append(message)

    def query_one(*_args: Any, **_kwargs: Any) -> SimpleNamespace:
        return (
            status if _args[0] is module.AudioStatusIndicator else SimpleNamespace(clear=Log().clear, write=Log().write)
        )

    app.query_one = query_one
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

    async def commit() -> None:
        sent.append("commit")

    async def create() -> None:
        sent.append("create")

    app.connection = SimpleNamespace(
        response=SimpleNamespace(cancel=cancel, create=create),
        conversation=SimpleNamespace(item=SimpleNamespace(truncate=truncate)),
        input_audio_buffer=SimpleNamespace(append=append, commit=commit),
    )
    if manual_turn:
        app.session = SimpleNamespace(audio=SimpleNamespace(input=SimpleNamespace(turn_detection=None)))
    app.connected.set()
    app._active_response_id = "response"
    app._displayed_item = ("response", "assistant", 0)
    app.audio_player.add_data(bytes(1920), response_id="response", item_id="assistant", content_index=0)
    app.audio_player.stream.callback(np.empty((480, 1), dtype=np.int16), 480, None, None)
    mic = asyncio.create_task(app.send_mic_audio())
    key = asyncio.create_task(app.on_key(SimpleNamespace(key="k")))
    stop: asyncio.Task[None] | None = None
    try:
        await asyncio.wait_for(waiting.wait(), 2)
        await asyncio.wait_for(mic_started.wait(), 2)
        assert status.is_recording
        assert not sent
        assert display == ["Response interrupted."]
        if stop_before_cancel:
            stop = asyncio.create_task(app.on_key(SimpleNamespace(key="k")))
            for _ in range(100):
                if app._mic_stream is None:
                    break
                await asyncio.sleep(0)
            assert app._mic_stream is None
        release.set()
        await asyncio.wait_for(key, 2)
        if stop is not None:
            await asyncio.wait_for(stop, 2)
        for _ in range(100):
            if "append" in sent:
                break
            await asyncio.sleep(0)
        assert sent == (["cancel", "truncate"] if stop_before_cancel else ["cancel", "truncate", "append"])
        if not stop_before_cancel:
            await app.on_key(SimpleNamespace(key="k"))
            await app.workers.wait_for_complete()
            assert sent == ["cancel", "truncate", "append"] + (["commit", "create"] if manual_turn else [])
    finally:
        release.set()
        mic.cancel()
        await asyncio.gather(mic, return_exceptions=True)
        await app.client.close()
        assert app._mic_stream is None


@pytest.mark.asyncio
async def test_cancelling_first_append_does_not_commit_empty_manual_audio(app_module: Any) -> None:
    module, _ = app_module
    app = module.RealtimeApp()
    status = SimpleNamespace(is_recording=False)

    def query_one(*_args: Any, **_kwargs: Any) -> SimpleNamespace:
        return status

    app.query_one = query_one
    app.session = SimpleNamespace(audio=SimpleNamespace(input=SimpleNamespace(turn_detection=None)))
    begun = asyncio.Event()
    sent: list[str] = []

    async def append(**_kwargs: Any) -> None:
        begun.set()
        await asyncio.Future[None]()
        sent.append("append")

    async def commit() -> None:
        sent.append("commit")

    async def create() -> None:
        sent.append("create")

    app.connection = SimpleNamespace(
        input_audio_buffer=SimpleNamespace(append=append, commit=commit),
        response=SimpleNamespace(create=create),
    )
    app.connected.set()
    await app.on_key(SimpleNamespace(key="k"))
    mic = asyncio.create_task(app.send_mic_audio())
    try:
        await asyncio.wait_for(begun.wait(), 2)
        mic.cancel()
        with pytest.raises(asyncio.CancelledError):
            await mic
        assert app._mic_stream is None
        await app.on_key(SimpleNamespace(key="k"))
        assert sent == []
    finally:
        mic.cancel()
        await asyncio.gather(mic, return_exceptions=True)
        await app.client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["normal", "abnormal", "unsent", "cancellation"])
async def test_disconnect_exits_and_user_cancellation_is_preserved(app_module: Any, failure: str) -> None:
    from websockets.exceptions import ConnectionClosedError

    from openai import WebSocketConnectionClosedError

    module, _ = app_module
    app = module.RealtimeApp()
    exited: list[dict[str, Any]] = []

    def capture_exit(**kwargs: Any) -> None:
        exited.append(kwargs)

    app.exit = capture_exit

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


@pytest.mark.asyncio
async def test_late_transcript_deltas_from_interrupted_response_do_not_replace_display(app_module: Any) -> None:
    module, _ = app_module
    app = module.RealtimeApp()
    display: list[str] = []

    class Log:
        def clear(self) -> None:
            display.clear()

        def write(self, message: str) -> None:
            display.append(message)

    def query_one(*_args: Any, **_kwargs: Any) -> Log:
        return Log()

    async def update(**_kwargs: Any) -> None:
        pass

    class Connection:
        session = SimpleNamespace(update=update)

        async def __aenter__(self) -> Any:
            return self

        async def __aexit__(self, *_args: Any) -> None:
            pass

        async def __aiter__(self) -> Any:
            yield SimpleNamespace(
                type="response.output_audio_transcript.delta",
                response_id="old",
                item_id="old",
                content_index=0,
                delta="first",
            )
            assert display == ["first"]
            app._interrupted_responses["old"] = {("old", 0)}
            yield SimpleNamespace(
                type="response.output_audio_transcript.delta",
                response_id="old",
                item_id="old",
                content_index=0,
                delta="late",
            )
            assert display == ["first"]
            yield SimpleNamespace(
                type="response.output_audio_transcript.delta",
                response_id="new",
                item_id="new",
                content_index=0,
                delta="new speech",
            )
            assert display == ["new speech"]

    app.query_one = query_one
    original_client = app.client

    def connect(**_kwargs: Any) -> Connection:
        return Connection()

    app.client = SimpleNamespace(realtime=SimpleNamespace(connect=connect))
    try:
        await app._receive_realtime_events()
        assert app._displayed_item == ("new", "new", 0)
    finally:
        await original_client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("new_audio_sent", [False, True])
@pytest.mark.parametrize("released", [False, True])
async def test_response_created_while_recording_before_or_after_first_append(
    app_module: Any, new_audio_sent: bool, released: bool
) -> None:
    module, mic_started = app_module
    app = module.RealtimeApp()
    status = SimpleNamespace(is_recording=False)
    display: list[str] = []
    sent: list[tuple[str, Any]] = []

    class Log:
        def clear(self) -> None:
            display.clear()

        def write(self, message: str) -> None:
            display.append(message)

    def query_one(*args: Any, **_kwargs: Any) -> Any:
        return status if args[0] is module.AudioStatusIndicator else Log()

    async def update(**_kwargs: Any) -> None:
        pass

    async def cancel(**kwargs: Any) -> None:
        sent.append(("cancel", kwargs))

    async def append(**_kwargs: Any) -> None:
        sent.append(("append", None))

    async def truncate(**kwargs: Any) -> None:
        sent.append(("truncate", kwargs))

    class Connection:
        session = SimpleNamespace(update=update)
        response = SimpleNamespace(cancel=cancel)
        input_audio_buffer = SimpleNamespace(append=append)
        conversation = SimpleNamespace(item=SimpleNamespace(truncate=truncate))

        async def __aenter__(self) -> Any:
            return self

        async def __aexit__(self, *_args: Any) -> None:
            pass

        async def __aiter__(self) -> Any:
            await app.on_key(SimpleNamespace(key="k"))
            if new_audio_sent:
                mic = asyncio.create_task(app.send_mic_audio())
                try:
                    await asyncio.wait_for(mic_started.wait(), 2)
                    for _ in range(100):
                        if any(name == "append" for name, _ in sent):
                            break
                        await asyncio.sleep(0)
                    assert ("append", None) in sent
                finally:
                    mic.cancel()
                    await asyncio.gather(mic, return_exceptions=True)
            if released:
                await app.on_key(SimpleNamespace(key="k"))
            yield SimpleNamespace(type="response.created", response=SimpleNamespace(id="response"))
            yield SimpleNamespace(
                type="response.output_audio.delta",
                response_id="response",
                item_id="item",
                content_index=0,
                delta="AAAAAAAAAAA=",
            )
            yield SimpleNamespace(
                type="response.output_audio_transcript.delta",
                response_id="response",
                item_id="item",
                content_index=0,
                delta="a response",
            )
            await app.workers.wait_for_complete()
            if new_audio_sent:
                # Server VAD may legitimately answer a pause during the current recording.
                assert sent == [("append", None)]
                assert app.audio_player.playing
                assert display == ["a response"]
            else:
                # No new audio has been offered, so this can only be an older response.
                assert sent == [
                    ("cancel", {"response_id": "response"}),
                    ("truncate", {"item_id": "item", "content_index": 0, "audio_end_ms": 0}),
                ]
                assert not app.audio_player.playing
                assert display == []
            yield SimpleNamespace(
                type="response.done",
                response=SimpleNamespace(id="response", status="completed", status_details=None),
            )
            assert not app._interrupted_responses

    app.query_one = query_one
    original_client = app.client

    def connect(**_kwargs: Any) -> Connection:
        return Connection()

    app.client = SimpleNamespace(realtime=SimpleNamespace(connect=connect))
    try:
        await app._receive_realtime_events()
    finally:
        await original_client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("response_before_k,played_frames", [(True, 0), (False, 0), (True, 480)])
@pytest.mark.parametrize("first_delta", ["response.output_audio.delta", "response.output_audio_transcript.delta"])
async def test_interruption_truncates_late_unheard_audio_once(
    app_module: Any, response_before_k: bool, played_frames: int, first_delta: str
) -> None:
    module, _ = app_module
    app = module.RealtimeApp()
    status = SimpleNamespace(is_recording=False)
    display: list[str] = []
    sent: list[tuple[str, dict[str, Any]]] = []

    class Log:
        def clear(self) -> None:
            display.clear()

        def write(self, message: str) -> None:
            display.append(message)

    def query_one(*args: Any, **_kwargs: Any) -> Any:
        return status if args[0] is module.AudioStatusIndicator else Log()

    async def update(**_kwargs: Any) -> None:
        pass

    async def cancel(**kwargs: Any) -> None:
        sent.append(("cancel", kwargs))

    async def truncate(**kwargs: Any) -> None:
        sent.append(("truncate", kwargs))

    def delta(kind: str) -> SimpleNamespace:
        return SimpleNamespace(
            type=kind,
            response_id="old-response",
            item_id="assistant-item",
            content_index=0,
            delta="AAAAAAAAAAA=" if kind == "response.output_audio.delta" else "unheard text",
        )

    class Connection:
        session = SimpleNamespace(update=update)
        response = SimpleNamespace(cancel=cancel)
        conversation = SimpleNamespace(item=SimpleNamespace(truncate=truncate))

        async def __aenter__(self) -> Any:
            return self

        async def __aexit__(self, *_args: Any) -> None:
            pass

        async def __aiter__(self) -> Any:
            created = SimpleNamespace(type="response.created", response=SimpleNamespace(id="old-response"))
            if response_before_k:
                yield created
                if played_frames:
                    app.audio_player.add_data(
                        bytes(1920), response_id="old-response", item_id="assistant-item", content_index=0
                    )
                    app.audio_player.stream.callback(
                        np.empty((played_frames, 1), dtype=np.int16), played_frames, None, None
                    )
            await app.on_key(SimpleNamespace(key="k"))
            if not response_before_k:
                yield created
            # Model multiple in-flight chunks, with either transcript or audio arriving first.
            for kind in (first_delta, "response.output_audio.delta", "response.output_audio_transcript.delta"):
                yield delta(kind)
            await app.workers.wait_for_complete()
            assert not app.audio_player.playing
            assert display == []
            assert sent == [
                ("cancel", {"response_id": "old-response"}),
                ("truncate", {"item_id": "assistant-item", "content_index": 0, "audio_end_ms": played_frames // 24}),
            ]
            yield SimpleNamespace(
                type="response.done",
                response=SimpleNamespace(id="old-response", status="cancelled", status_details=None),
            )

    app.query_one = query_one
    original_client = app.client

    def connect(**_kwargs: Any) -> Connection:
        return Connection()

    app.client = SimpleNamespace(realtime=SimpleNamespace(connect=connect))
    try:
        await app._receive_realtime_events()
    finally:
        app._stop_mic_stream()
        await original_client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("manual_turn", [False, True])
@pytest.mark.parametrize("contended", [False, True])
async def test_delayed_response_cancel_finishes_before_new_mic_audio(
    app_module: Any, manual_turn: bool, contended: bool
) -> None:
    module, mic_started = app_module
    app = module.RealtimeApp()
    status = SimpleNamespace(is_recording=False)

    def query_one(*_args: Any, **_kwargs: Any) -> SimpleNamespace:
        return status

    app.query_one = query_one
    if manual_turn:
        app.session = SimpleNamespace(audio=SimpleNamespace(input=SimpleNamespace(turn_detection=None)))
    waiting = asyncio.Event()
    release = asyncio.Event()
    appended = asyncio.Event()
    reception_done = asyncio.Event()
    delayed_may_arrive = asyncio.Event()
    delayed_delivered = asyncio.Event()
    sent: list[str] = []

    async def update(**_kwargs: Any) -> None:
        pass

    async def cancel(*, response_id: str) -> None:
        if not contended or response_id == "active-response":
            waiting.set()
            await release.wait()
        sent.append(f"cancel:{response_id}")

    async def append(**_kwargs: Any) -> None:
        sent.append("append")
        appended.set()

    async def commit() -> None:
        sent.append("commit")

    async def create() -> None:
        sent.append("create")

    class Connection:
        session = SimpleNamespace(update=update)
        response = SimpleNamespace(cancel=cancel, create=create)
        input_audio_buffer = SimpleNamespace(append=append, commit=commit)

        async def __aenter__(self) -> Any:
            return self

        async def __aexit__(self, *_args: Any) -> None:
            pass

        async def __aiter__(self) -> Any:
            if contended:
                yield SimpleNamespace(type="response.created", response=SimpleNamespace(id="active-response"))
            await app.on_key(SimpleNamespace(key="k"))
            if contended:
                await delayed_may_arrive.wait()
                # The server has completed the interrupted response before starting another.
                yield SimpleNamespace(
                    type="response.done", response=SimpleNamespace(id="active-response", status="completed")
                )
            delayed_delivered.set()
            yield SimpleNamespace(type="response.created", response=SimpleNamespace(id="old-response"))
            await reception_done.wait()

    def connect(**_kwargs: Any) -> Connection:
        return Connection()

    original_client = app.client
    app.client = SimpleNamespace(realtime=SimpleNamespace(connect=connect))
    receiver = asyncio.create_task(app._receive_realtime_events())
    mic: asyncio.Task[None] | None = None
    try:
        await asyncio.wait_for(waiting.wait(), 2)
        await asyncio.wait_for(mic_started.wait(), 2)
        mic = asyncio.create_task(app.send_mic_audio())
        for _ in range(100):
            if appended.is_set():
                break
            await asyncio.sleep(0)
        assert status.is_recording
        assert sent == []
        if contended:
            # The microphone already waits behind A when the receiver learns of B.
            delayed_may_arrive.set()
            await asyncio.wait_for(delayed_delivered.wait(), 2)
        release.set()
        await asyncio.wait_for(appended.wait(), 2)
        await app.on_key(SimpleNamespace(key="k"))
        await app.workers.wait_for_complete()
        assert sent == (
            (["cancel:active-response"] if contended else [])
            + ["cancel:old-response", "append"]
            + (["commit", "create"] if manual_turn else [])
        )
    finally:
        release.set()
        reception_done.set()
        if mic is not None:
            mic.cancel()
        receiver.cancel()
        await asyncio.gather(receiver, *([mic] if mic is not None else []), return_exceptions=True)
        await original_client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("waiter", ["microphone", "manual"])
@pytest.mark.parametrize("cancel_before_start", [False, True])
async def test_queued_interruption_precedes_runnable_sender(
    app_module: Any, waiter: str, cancel_before_start: bool
) -> None:
    module, _ = app_module
    app = module.RealtimeApp()
    status = SimpleNamespace(is_recording=False)
    sent: list[str] = []
    sent_first = asyncio.Event()
    cancel_started = asyncio.Event()
    release_cancel = asyncio.Event()

    def query_one(*_args: Any, **_kwargs: Any) -> SimpleNamespace:
        return status

    async def cancel(**_kwargs: Any) -> None:
        cancel_started.set()
        await release_cancel.wait()
        sent.append("cancel")

    async def append(**_kwargs: Any) -> None:
        sent.append("append")
        sent_first.set()

    async def commit() -> None:
        sent.append("commit")
        sent_first.set()

    async def create() -> None:
        sent.append("create")

    app.query_one = query_one
    app.connection = SimpleNamespace(
        response=SimpleNamespace(cancel=cancel, create=create),
        input_audio_buffer=SimpleNamespace(append=append, commit=commit),
    )
    app.connected.set()
    await app.on_key(SimpleNamespace(key="k"))
    await app._mic_send_lock.acquire()
    if waiter == "microphone":
        sender = asyncio.create_task(app.send_mic_audio())
    else:
        # Audio from an earlier recording is already queued for manual completion.
        sender = asyncio.create_task(app._finish_manual_recording(module.Recording(has_audio=True)))
    try:
        for _ in range(20):
            await asyncio.sleep(0)
        assert not sent
        # Make the sender runnable, then register a K interruption before it gets CPU.
        app._mic_send_lock.release()
        await app.on_key(SimpleNamespace(key="k"))
        app._active_response_id = "old-response"
        await app.on_key(SimpleNamespace(key="k"))
        if cancel_before_start:
            app.workers.cancel_group(app, "realtime-interruption")
        else:
            await asyncio.wait_for(cancel_started.wait(), 2)
            for _ in range(20):
                await asyncio.sleep(0)
            assert not sent
            release_cancel.set()
        await asyncio.wait_for(sent_first.wait(), 2)
        expected = ([] if cancel_before_start else ["cancel"]) + (
            ["append"] if waiter == "microphone" else ["commit", "create"]
        )
        assert sent == expected
    finally:
        release_cancel.set()
        sender.cancel()
        await asyncio.gather(sender, return_exceptions=True)
        await app.client.close()


@pytest.mark.asyncio
async def test_manual_recordings_do_not_share_buffer_after_interruption(
    app_module: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    import base64

    module, _ = app_module
    app = module.RealtimeApp()
    status = SimpleNamespace(is_recording=False)

    def query_one(*_args: Any, **_kwargs: Any) -> SimpleNamespace:
        return status

    app.query_one = query_one
    app.session = SimpleNamespace(audio=SimpleNamespace(input=SimpleNamespace(turn_detection=None)))
    first_started, first_release = asyncio.Event(), asyncio.Event()
    cancel_started, cancel_release = asyncio.Event(), asyncio.Event()
    second_appended = asyncio.Event()
    buffer: list[int] = []
    commits: list[list[int]] = []
    sent: list[str] = []

    device = sys.modules["sounddevice"]
    original_read = device.InputStream.read

    def read(stream: Any, frames: int) -> tuple[Any, bool]:
        data, overflow = original_read(stream, frames)
        data.fill(stream.marker)
        return data, overflow

    monkeypatch.setattr(device.InputStream, "read", read)

    async def append(*, audio: str) -> None:
        marker = int(np.frombuffer(base64.b64decode(audio), dtype=np.int16)[0])
        if marker == 1:
            first_started.set()
            await first_release.wait()
        buffer.append(marker)
        sent.append(f"append {marker}")
        if marker == 2:
            second_appended.set()

    async def cancel(**_kwargs: Any) -> None:
        cancel_started.set()
        await cancel_release.wait()
        sent.append("cancel")

    async def commit() -> None:
        commits.append(list(buffer))
        buffer.clear()
        sent.append("commit")

    async def create() -> None:
        sent.append("create")

    app.connection = SimpleNamespace(
        response=SimpleNamespace(cancel=cancel, create=create),
        input_audio_buffer=SimpleNamespace(append=append, commit=commit),
    )
    app.connected.set()
    mic = asyncio.create_task(app.send_mic_audio())
    try:
        await app.on_key(SimpleNamespace(key="k"))
        app._mic_stream.marker = 1
        await asyncio.wait_for(first_started.wait(), 2)
        await app.on_key(SimpleNamespace(key="k"))
        # The completed recording is waiting on its in-flight append; a new K
        # begins capture and interrupts an earlier server response immediately.
        app._active_response_id = "previous"
        await app.on_key(SimpleNamespace(key="k"))
        app._mic_stream.marker = 2
        assert status.is_recording
        for _ in range(20):
            await asyncio.sleep(0)
        assert not sent
        first_release.set()
        await asyncio.wait_for(cancel_started.wait(), 2)
        assert sent == ["append 1"]
        assert status.is_recording
        cancel_release.set()
        await asyncio.wait_for(second_appended.wait(), 2)
        await app.on_key(SimpleNamespace(key="k"))
        await asyncio.wait_for(app.workers.wait_for_complete(), 2)
        assert commits == [[1], [2]]
        assert sent == ["append 1", "cancel", "commit", "create", "append 2", "commit", "create"]
    finally:
        first_release.set()
        cancel_release.set()
        mic.cancel()
        await asyncio.gather(mic, return_exceptions=True)
        await app.client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel_before_start", [False, True])
async def test_pending_manual_finalize_precedes_already_runnable_mic(
    app_module: Any, cancel_before_start: bool
) -> None:
    module, _ = app_module
    app = module.RealtimeApp()
    status = SimpleNamespace(is_recording=False)

    def query_one(*_args: Any, **_kwargs: Any) -> SimpleNamespace:
        return status

    app.query_one = query_one
    app.session = SimpleNamespace(audio=SimpleNamespace(input=SimpleNamespace(turn_detection=None)))
    sent: list[str] = []
    appended = asyncio.Event()

    async def append(**_kwargs: Any) -> None:
        sent.append("append")
        appended.set()

    async def commit() -> None:
        sent.append("commit")

    async def create() -> None:
        sent.append("create")

    app.connection = SimpleNamespace(
        response=SimpleNamespace(create=create),
        input_audio_buffer=SimpleNamespace(append=append, commit=commit),
    )
    app.connected.set()
    await app.on_key(SimpleNamespace(key="k"))
    # Simulate audio already sent from the current recording. Hold the send lock
    # until its waiter is runnable, then dispatch both keys without yielding.
    app._recording.has_audio = True
    await app._mic_send_lock.acquire()
    mic = asyncio.create_task(app.send_mic_audio())
    try:
        for _ in range(20):
            await asyncio.sleep(0)
        app._mic_send_lock.release()
        await app.on_key(SimpleNamespace(key="k"))
        await app.on_key(SimpleNamespace(key="k"))
        if cancel_before_start:
            app.workers.cancel_group(app, "realtime-finalization")
        await asyncio.wait_for(appended.wait(), 2)
        await asyncio.wait_for(app.workers.wait_for_complete(), 2)
        assert sent == (["append"] if cancel_before_start else ["commit", "create", "append"])
    finally:
        mic.cancel()
        await asyncio.gather(mic, return_exceptions=True)
        await app.client.close()


@pytest.mark.parametrize("finish_response", [False, True])
@pytest.mark.parametrize("abort_return_delay", [0.0, 0.08])
def test_cutoff_accounts_after_stopping_without_counting_silence(
    app_module: Any, monkeypatch: pytest.MonkeyPatch, finish_response: bool, abort_return_delay: float
) -> None:
    import threading

    module, _ = app_module
    player = module.AudioPlayerAsync()
    key = ("response", "spoken", 0)
    player.add_data(bytes(1920), response_id=key[0], item_id=key[1], content_index=key[2])
    player.stream.time = 0.98
    player.stream.callback(
        np.empty((960, 1), dtype=np.int16),
        960,
        SimpleNamespace(outputBufferDacTime=1.0, currentTime=0.98),
        None,
    )
    if finish_response:
        player.finish_response(key[0])
    player.stream.time = 1.01
    stopped_at: float | None = None
    original_abort = player.stream.abort
    original_discard = player._discard_finished_counts

    def account(now: float) -> None:
        # Accounting a large queue takes time. Until abort, queued DAC audio
        # continues playing even though future callbacks have been silenced.
        player.stream.time += 0.02
        original_discard(now)

    def abort() -> None:
        nonlocal stopped_at
        # The driver can stop playback before its abort method returns. The
        # PortAudio stream clock continues afterward, even with no sound playing.
        stopped_at = player.stream.time
        out = np.full((480, 1), 99, dtype=np.int16)
        callback = threading.Thread(target=player.stream.callback, args=(out, 480, None, None), daemon=True)
        callback.start()
        callback.join(1)
        assert not callback.is_alive(), "abort held the lock required by the device callback"
        assert not np.any(out)
        player.stream.time += abort_return_delay
        original_abort()

    monkeypatch.setattr(player, "_discard_finished_counts", account)
    monkeypatch.setattr(player.stream, "abort", abort)
    result = player.stop(interrupted_response_id=None if finish_response else key[0])
    assert stopped_at is not None
    heard_frames = min(960, int((stopped_at - 1.0) * module.SAMPLE_RATE))
    expected = [] if finish_response and heard_frames == 960 else [(key, heard_frames)]
    assert result == expected
