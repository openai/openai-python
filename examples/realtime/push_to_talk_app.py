#!/usr/bin/env -S uv run

# Sample TUI app with a push to talk interface to the Realtime API #
# If you have `uv` installed and the `OPENAI_API_KEY`              #
# environment variable set, you can run this example with just     #

# `./examples/realtime/push_to_talk_app.py`                        #

# On Mac, you'll also need `brew install portaudio ffmpeg`           #


# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "textual",
#     "numpy",
#     "pyaudio",
#     "pydub",
#     "sounddevice",
#     "openai[realtime]",
# ]
#
# [tool.uv]
# exclude-newer = "P8D"
#
# [tool.uv.sources]
# openai = { path = "../../", editable = true }
# ///
from __future__ import annotations

import base64
import asyncio
from typing import Any, cast
from functools import partial
from dataclasses import dataclass
from typing_extensions import override

from textual import events
from audio_util import CHANNELS, SAMPLE_RATE, AudioPlayerAsync
from textual.app import App, ComposeResult
from textual.widgets import Static, RichLog
from textual.reactive import reactive
from textual.containers import Container
from websockets.exceptions import ConnectionClosed

from openai import AsyncOpenAI, WebSocketConnectionClosedError
from openai.resources.realtime.realtime import AsyncRealtimeConnection
from openai.types.realtime.session_created_event import Session


class SessionDisplay(Static):
    """A widget that shows the current session ID."""

    session_id = reactive("")

    @override
    def render(self) -> str:
        return f"Session ID: {self.session_id}" if self.session_id else "Connecting..."


class AudioStatusIndicator(Static):
    """A widget that shows the current audio recording status."""

    is_recording = reactive(False)

    @override
    def render(self) -> str:
        status = (
            "🔴 Recording... (Press K to stop)" if self.is_recording else "⚪ Press K to start recording (Q to quit)"
        )
        return status


@dataclass
class Recording:
    has_audio: bool = False


class RealtimeApp(App[None]):
    CSS = """
        Screen {
            background: #1a1b26;  /* Dark blue-grey background */
        }

        Container {
            border: double rgb(91, 164, 91);
        }

        Horizontal {
            width: 100%;
        }

        #input-container {
            height: 5;  /* Explicit height for input container */
            margin: 1 1;
            padding: 1 2;
        }

        Input {
            width: 80%;
            height: 3;  /* Explicit height for input */
        }

        #bottom-pane {
            width: 100%;
            height: 82%;  /* Reduced to make room for session display */
            border: round rgb(205, 133, 63);
            content-align: center middle;
        }

        #status-indicator {
            height: 3;
            content-align: center middle;
            background: #2a2b36;
            border: solid rgb(91, 164, 91);
            margin: 1 1;
        }

        #session-display {
            height: 3;
            content-align: center middle;
            background: #2a2b36;
            border: solid rgb(91, 164, 91);
            margin: 1 1;
        }

        Static {
            color: white;
        }
    """

    client: AsyncOpenAI
    should_send_audio: asyncio.Event
    audio_player: AudioPlayerAsync
    connection: AsyncRealtimeConnection | None
    session: Session | None
    connected: asyncio.Event

    def __init__(self) -> None:
        super().__init__()
        self.connection = None
        self.session = None
        self.client = AsyncOpenAI()
        self.audio_player = AudioPlayerAsync()
        self._active_response_id: str | None = None
        self._displayed_item: tuple[str, str, int] | None = None
        self._interrupted_responses: dict[str, set[tuple[str, int]]] = {}
        self.should_send_audio = asyncio.Event()
        self._mic_send_lock = asyncio.Lock()
        self._pending_interruptions = 0
        self._awaiting_new_input = False
        self.connected = asyncio.Event()
        self._mic_stream: Any = None
        self._recording = Recording()

    @override
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        with Container():
            yield SessionDisplay(id="session-display")
            yield AudioStatusIndicator(id="status-indicator")
            yield RichLog(id="bottom-pane", wrap=True, highlight=True)

    async def on_mount(self) -> None:
        self.run_worker(self.handle_realtime_connection())
        self.run_worker(self.send_mic_audio())

    async def on_unmount(self) -> None:
        self.audio_player.terminate()
        await self.client.close()

    async def handle_realtime_connection(self) -> None:
        try:
            await self._receive_realtime_events()
        except (ConnectionClosed, WebSocketConnectionClosedError):
            # End the app with the same message for normal and abnormal socket closure.
            pass
        self.exit(return_code=1, message="The Realtime connection closed.")

    async def _receive_realtime_events(self) -> None:
        async with self.client.realtime.connect(model="gpt-realtime") as conn:
            self.connection = conn
            self.connected.set()

            # note: this is the default and can be omitted
            # if you want to manually handle VAD yourself, then set `'turn_detection': None`
            await conn.session.update(
                session={
                    "audio": {
                        "input": {"turn_detection": {"type": "server_vad"}},
                    },
                    "model": "gpt-realtime",
                    "type": "realtime",
                }
            )

            acc_items: dict[str, Any] = {}

            async for event in conn:
                if event.type == "session.created":
                    self.session = event.session
                    session_display = self.query_one(SessionDisplay)
                    # The session ID is returned as an extra field on the session configuration.
                    session_id = getattr(event.session, "id", None)
                    assert isinstance(session_id, str)
                    session_display.session_id = session_id
                    continue

                if event.type == "session.updated":
                    self.session = event.session
                    continue

                if event.type == "error":
                    self.query_one(RichLog).write(f"Realtime error: {event.error.message}")
                    continue

                if event.type == "response.created":
                    if self._active_response_id is not None and self._active_response_id != event.response.id:
                        self.audio_player.finish_response(self._active_response_id)
                    if self._awaiting_new_input and event.response.id is not None:
                        # Nothing from a new recording has been offered since K
                        # interrupted playback, so this response belongs to an
                        # earlier turn (even if K was already released).
                        self._active_response_id = None
                        self._interrupted_responses[event.response.id] = set()
                        await self._interrupt_response(event.response.id, [])
                        continue
                    self._active_response_id = event.response.id
                    continue

                if event.type == "response.done":
                    if self._active_response_id == event.response.id:
                        self._active_response_id = None
                    if event.response.id is not None:
                        self._interrupted_responses.pop(event.response.id, None)
                        self.audio_player.finish_response(event.response.id)
                    if event.response.status in {"failed", "incomplete"}:
                        details = event.response.status_details
                        message = details.error.message if details and details.error else None
                        reason = message or (details.reason if details else None)
                        text = f"Response {event.response.status}"
                        self.query_one(RichLog).write(f"{text}: {reason}" if reason else text)
                    continue

                if event.type in {"response.output_audio.delta", "response.output_audio_transcript.delta"}:
                    handled = self._interrupted_responses.get(event.response_id)
                    if handled is not None:
                        part = (event.item_id, event.content_index)
                        if part not in handled:
                            # This item arrived after playback was stopped; none of it was heard.
                            # Reserve it before the worker runs so later chunks cannot truncate it twice.
                            handled.add(part)
                            self.run_worker(
                                partial(
                                    self._interrupt_response,
                                    None,
                                    [((event.response_id, event.item_id, event.content_index), 0)],
                                ),
                                group="realtime-interruption",
                            )
                        continue

                if event.type == "response.output_audio.delta":
                    bytes_data = base64.b64decode(event.delta)
                    self.audio_player.add_data(
                        bytes_data,
                        response_id=event.response_id,
                        item_id=event.item_id,
                        content_index=event.content_index,
                    )
                    continue

                if event.type == "response.output_audio_transcript.delta":
                    try:
                        text = acc_items[event.item_id]
                    except KeyError:
                        acc_items[event.item_id] = event.delta
                    else:
                        acc_items[event.item_id] = text + event.delta

                    # Clear and update the entire content because RichLog otherwise treats each delta as a new line
                    bottom_pane = self.query_one("#bottom-pane", RichLog)
                    bottom_pane.clear()
                    bottom_pane.write(acc_items[event.item_id])
                    self.audio_player.note_transcript(event.response_id, event.item_id, event.content_index)
                    self._displayed_item = (event.response_id, event.item_id, event.content_index)
                    continue

    async def _get_connection(self) -> AsyncRealtimeConnection:
        await self.connected.wait()
        assert self.connection is not None
        return self.connection

    async def send_mic_audio(self) -> None:
        read_size = int(SAMPLE_RATE * 0.02)

        try:
            while True:
                await self.should_send_audio.wait()
                connection = await self._get_connection()
                if not self.should_send_audio.is_set():
                    continue

                stream = self._mic_stream
                recording = self._recording
                if stream is None:
                    continue
                if stream.read_available < read_size:
                    await asyncio.sleep(0)
                    continue

                async with self._mic_send_lock:
                    if stream is not self._mic_stream or not self.should_send_audio.is_set():
                        continue
                    if not self._interruptions_pending() and not any(
                        worker.group == "realtime-finalization" and not worker.is_finished for worker in self.workers
                    ):
                        data, _ = stream.read(read_size)
                        self._awaiting_new_input = False
                        try:
                            await connection.input_audio_buffer.append(
                                audio=base64.b64encode(cast(Any, data)).decode("utf-8")
                            )
                            recording.has_audio = True
                        except BaseException:
                            if recording is self._recording:
                                self._awaiting_new_input = True
                            raise

                # Let registered interruption or finalization work start before retrying.
                await asyncio.sleep(0)
        except KeyboardInterrupt:
            pass
        finally:
            self._stop_mic_stream()

    def _stop_mic_stream(self) -> None:
        if self._mic_stream is not None:
            try:
                self._mic_stream.abort()
            finally:
                self._mic_stream.close()
                self._mic_stream = None

    async def on_key(self, event: events.Key) -> None:
        """Handle key press events."""
        if event.key == "q":
            self.exit()
            return

        if event.key == "k":
            status_indicator = self.query_one(AudioStatusIndicator)
            if status_indicator.is_recording:
                self.should_send_audio.clear()
                self._stop_mic_stream()
                status_indicator.is_recording = False

                if (
                    self.session
                    and self.session.audio
                    and self.session.audio.input
                    and self.session.audio.input.turn_detection is None
                ):
                    # The default in the API is that the model will automatically detect when the user has
                    # stopped talking and then start responding itself.

                    # However if we're in manual `turn_detection` mode then we need to
                    # manually tell the model to commit the audio buffer and start responding.
                    # Reserve the shared server buffer before the next K can send.
                    # Capture can start immediately; appends wait for this recording.
                    self.run_worker(
                        partial(self._finish_manual_recording, self._recording), group="realtime-finalization"
                    )
            else:
                import sounddevice as sd

                self._recording = Recording()
                self._awaiting_new_input = True
                # Open each recording at K, even while an earlier send is blocked.
                self._mic_stream = sd.InputStream(channels=CHANNELS, samplerate=SAMPLE_RATE, dtype="int16")
                self._mic_stream.start()
                status_indicator.is_recording = True
                response_id = self._active_response_id
                self._active_response_id = None
                unheard = self.audio_player.stop(interrupted_response_id=response_id)
                if response_id is not None:
                    # Preserve the cutoff of partially played items, even while cancellation is pending.
                    self._interrupted_responses[response_id] = {
                        (item_id, content_index)
                        for (owner, item_id, content_index), _ in unheard
                        if owner == response_id
                    }
                if any(key == self._displayed_item for key, _ in unheard):
                    bottom_pane = self.query_one("#bottom-pane", RichLog)
                    bottom_pane.clear()
                    bottom_pane.write("Response interrupted.")
                    self._displayed_item = None
                # Queue ordering work before waking the mic sender. Textual owns
                # worker cancellation on exit; no WebSocket writes hold the UI.
                if response_id is not None or unheard:
                    self.run_worker(
                        partial(self._interrupt_response, response_id, unheard), group="realtime-interruption"
                    )
                self.should_send_audio.set()

    def _interruptions_pending(self) -> bool:
        # Inline receiver work reserves before taking the lock. Textual registers
        # workers immediately and removes them even when cancelled before starting.
        return self._pending_interruptions > 0 or any(
            worker.group == "realtime-interruption" and not worker.is_finished for worker in self.workers
        )

    async def _finish_manual_recording(self, recording: Recording) -> None:
        conn = await self._get_connection()
        while True:
            async with self._mic_send_lock:
                if not self._interruptions_pending():
                    if recording.has_audio:
                        await conn.input_audio_buffer.commit()
                        await conn.response.create()
                    return
            await asyncio.sleep(0)

    async def _interrupt_response(
        self, response_id: str | None, unheard: list[tuple[tuple[str, str, int], int]]
    ) -> None:
        # Reserve before waiting: an older mic waiter must yield to new interruption work.
        self._pending_interruptions += 1
        try:
            async with self._mic_send_lock:
                if self.connection is None:
                    return
                if response_id is not None:
                    await self.connection.response.cancel(response_id=response_id)
                for (_, item_id, content_index), frames in unheard:
                    if content_index != 0:
                        self.query_one(RichLog).write("Cannot truncate audio: the API only supports content part 0.")
                        continue
                    await self.connection.conversation.item.truncate(
                        item_id=item_id, content_index=content_index, audio_end_ms=frames * 1000 // SAMPLE_RATE
                    )
        finally:
            self._pending_interruptions -= 1


if __name__ == "__main__":
    app = RealtimeApp()
    app.run()
    raise SystemExit(app.return_code)
