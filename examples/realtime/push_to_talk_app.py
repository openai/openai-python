#!/usr/bin/env -S uv run
####################################################################
# Sample TUI app with a push to talk interface to the Realtime API #
# If you have `uv` installed and the `OPENAI_API_KEY`              #
# environment variable set, you can run this example with just     #
#                                                                  #
# `./examples/realtime/push_to_talk_app.py`                        #
#                                                                  #
# On Mac, you'll also need `brew install portaudio ffmpeg`           #
####################################################################
#
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
        self._interrupted_response_ids: set[str] = set()
        self.should_send_audio = asyncio.Event()
        self._mic_send_lock = asyncio.Lock()
        self.connected = asyncio.Event()
        self._mic_stream: Any = None

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
                    self._active_response_id = event.response.id
                    continue

                if event.type == "response.done":
                    if self._active_response_id == event.response.id:
                        self._active_response_id = None
                    if event.response.id is not None:
                        self._interrupted_response_ids.discard(event.response.id)
                        self.audio_player.finish_response(event.response.id)
                    if event.response.status in {"failed", "incomplete"}:
                        details = event.response.status_details
                        message = details.error.message if details and details.error else None
                        reason = message or (details.reason if details else None)
                        text = f"Response {event.response.status}"
                        self.query_one(RichLog).write(f"{text}: {reason}" if reason else text)
                    continue

                if event.type == "response.output_audio.delta":
                    if event.response_id in self._interrupted_response_ids:
                        continue
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
                    continue

    async def _get_connection(self) -> AsyncRealtimeConnection:
        await self.connected.wait()
        assert self.connection is not None
        return self.connection

    async def send_mic_audio(self) -> None:
        import sounddevice as sd  # type: ignore

        device_info = sd.query_devices()
        print(device_info)

        read_size = int(SAMPLE_RATE * 0.02)

        try:
            while True:
                await self.should_send_audio.wait()
                connection = await self._get_connection()
                if not self.should_send_audio.is_set():
                    continue

                if self._mic_stream is None:
                    # Use a fresh stream for each recording so buffered audio from
                    # a previous recording cannot be sent when recording resumes.
                    self._mic_stream = sd.InputStream(
                        channels=CHANNELS,
                        samplerate=SAMPLE_RATE,
                        dtype="int16",
                    )
                    self._mic_stream.start()

                stream = self._mic_stream
                if stream.read_available < read_size:
                    await asyncio.sleep(0)
                    continue

                async with self._mic_send_lock:
                    if stream is not self._mic_stream or not self.should_send_audio.is_set():
                        continue
                    data, _ = stream.read(read_size)
                    await connection.input_audio_buffer.append(audio=base64.b64encode(cast(Any, data)).decode("utf-8"))

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
                    #
                    # However if we're in manual `turn_detection` mode then we need to
                    # manually tell the model to commit the audio buffer and start responding.
                    conn = await self._get_connection()
                    async with self._mic_send_lock:
                        await conn.input_audio_buffer.commit()
                        await conn.response.create()
            else:
                async with self._mic_send_lock:
                    self.should_send_audio.set()
                    status_indicator.is_recording = True
                    unheard = (
                        self.audio_player.stop(interrupted_response_id=self._active_response_id)
                        if self.audio_player.playing
                        else []
                    )
                    if self.connection is not None:
                        if self._active_response_id is not None:
                            response_id = self._active_response_id
                            self._active_response_id = None
                            self._interrupted_response_ids.add(response_id)
                            await self.connection.response.cancel(response_id=response_id)
                        for (_, item_id, content_index), frames in unheard:
                            if content_index != 0:
                                self.query_one(RichLog).write(
                                    "Cannot truncate audio: the API only supports content part 0."
                                )
                                continue
                            await self.connection.conversation.item.truncate(
                                item_id=item_id,
                                content_index=content_index,
                                audio_end_ms=frames * 1000 // SAMPLE_RATE,
                            )


if __name__ == "__main__":
    app = RealtimeApp()
    app.run()
    raise SystemExit(app.return_code)
