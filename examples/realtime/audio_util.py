from __future__ import annotations

import io
import base64
import asyncio
import threading
from typing import Callable, Awaitable

import numpy as np
import pyaudio
import sounddevice as sd
from pydub import AudioSegment

from openai.resources.realtime.realtime import AsyncRealtimeConnection

CHUNK_LENGTH_S = 0.05  # 50ms
SAMPLE_RATE = 24000
FORMAT = pyaudio.paInt16
CHANNELS = 1


def audio_to_pcm16_base64(audio_bytes: bytes) -> bytes:
    # load the audio file from the byte stream
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
    print(f"Loaded audio: {audio.frame_rate=} {audio.channels=} {audio.sample_width=} {audio.frame_width=}")
    # resample to 24kHz mono pcm16
    pcm_audio = audio.set_frame_rate(SAMPLE_RATE).set_channels(CHANNELS).set_sample_width(2).raw_data
    return pcm_audio


class AudioPlayerAsync:
    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()
        self.stream = sd.OutputStream(
            callback=self.callback,
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=np.int16,
            blocksize=int(CHUNK_LENGTH_S * SAMPLE_RATE),
        )
        self.playing = False
        self._frame_count = 0
        self._played_by_item: dict[tuple[str, str, int], int] = {}
        # Item, scheduled DAC time, frames submitted before this span, span length.
        self._scheduled: list[tuple[tuple[str, str, int], float, int, int]] = []
        self._finished_responses: set[str] = set()

    def callback(self, outdata, frames, time, status):  # noqa
        with self.lock:
            if not self.playing:
                outdata.fill(0)
                return
            data = np.empty(0, dtype=np.int16)

            # get next item from queue if there is still space in the buffer
            while len(data) < frames and len(self.queue) > 0:
                item, item_key = self.queue.pop(0)
                frames_needed = frames - len(data)
                played = item[:frames_needed]
                before = self._played_by_item.get(item_key, 0)
                self._scheduled.append(
                    (item_key, time.outputBufferDacTime + len(data) / SAMPLE_RATE, before, len(played))
                )
                data = np.concatenate((data, played))
                self._played_by_item[item_key] = before + len(played)
                if len(item) > frames_needed:
                    self.queue.insert(0, (item[frames_needed:], item_key))

            self._frame_count += len(data)
            self._discard_finished_counts(time.currentTime)

            # fill the rest of the frames with zeros if there is no more data
            if len(data) < frames:
                data = np.concatenate((data, np.zeros(frames - len(data), dtype=np.int16)))

        outdata[:] = data.reshape(-1, 1)

    def get_frame_count(self):
        return self._frame_count

    def finish_response(self, response_id: str):
        with self.lock:
            self._finished_responses.add(response_id)
            self._discard_finished_counts(self.stream.time)

    def _discard_finished_counts(self, now: float):
        self._scheduled = [span for span in self._scheduled if span[1] + span[3] / SAMPLE_RATE > now]
        pending = {key for _, key in self.queue}
        pending.update(key for key, _, _, _ in self._scheduled)
        for key in list(self._played_by_item):
            if key[0] in self._finished_responses and key not in pending:
                del self._played_by_item[key]
        self._finished_responses.intersection_update(key[0] for key in pending)

    def note_transcript(self, response_id: str, item_id: str, content_index: int):
        with self.lock:
            self._played_by_item.setdefault((response_id, item_id, content_index), 0)

    def add_data(self, data: bytes, *, response_id: str, item_id: str, content_index: int):
        with self.lock:
            # bytes is pcm16 single channel audio data, convert to numpy array
            np_data = np.frombuffer(data, dtype=np.int16)
            self.queue.append((np_data, (response_id, item_id, content_index)))
            if not self.playing:
                self.start()

    def start(self):
        self.playing = True
        self.stream.start()

    def stop(self, *, interrupted_response_id: str | None = None):
        with self.lock:
            was_playing = self.playing
            self.playing = False
        # Silence new callbacks before stopping the device; abort must not hold
        # the lock a callback may need. Do accounting only after stopping sound.
        # PortAudio's clock advances while stopped, so use the last known playing
        # time immediately before abort, not the time after it returns.
        now = self.stream.time
        if was_playing:
            self.stream.abort()
        with self.lock:
            self._discard_finished_counts(now)
            pending = dict.fromkeys(key for _, key in self.queue)
            pending.update(dict.fromkeys(key for key, _, _, _ in self._scheduled))
            pending.update(dict.fromkeys(key for key in self._played_by_item if key[0] == interrupted_response_id))
            heard = {key: self._played_by_item.get(key, 0) for key in pending}
            for key, start, before, frames in self._scheduled:
                played = max(0, min(frames, int((now - start) * SAMPLE_RATE)))
                heard[key] = min(heard[key], before + played)
            self.queue = []
            self._played_by_item.clear()
            self._scheduled.clear()
            self._finished_responses.clear()
            self._frame_count = 0
        return list(heard.items())

    def terminate(self):
        self.stream.close()


async def send_audio_worker_sounddevice(
    connection: AsyncRealtimeConnection,
    should_send: Callable[[], bool] | None = None,
    start_send: Callable[[], Awaitable[None]] | None = None,
):
    sent_audio = False

    device_info = sd.query_devices()
    print(device_info)

    read_size = int(SAMPLE_RATE * 0.02)

    stream = sd.InputStream(
        channels=CHANNELS,
        samplerate=SAMPLE_RATE,
        dtype="int16",
    )
    stream.start()

    try:
        while True:
            if stream.read_available < read_size:
                await asyncio.sleep(0)
                continue

            data, _ = stream.read(read_size)

            if should_send() if should_send else True:
                if not sent_audio and start_send:
                    await start_send()
                await connection.send(
                    {"type": "input_audio_buffer.append", "audio": base64.b64encode(data).decode("utf-8")}
                )
                sent_audio = True

            elif sent_audio:
                print("Done, triggering inference")
                await connection.send({"type": "input_audio_buffer.commit"})
                await connection.send({"type": "response.create", "response": {}})
                sent_audio = False

            await asyncio.sleep(0)

    except KeyboardInterrupt:
        pass
    finally:
        stream.stop()
        stream.close()
