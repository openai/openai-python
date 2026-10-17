from __future__ import annotations

import asyncio
import threading
from typing import Any, List, Union, AsyncGenerator

import pytest

np = pytest.importorskip("numpy")

from openai.helpers import local_audio_player


class FakeCallbackStop(Exception):
    """Stand-in for `sounddevice.CallbackStop`."""


class FakeOutputStream:
    """Minimal `sounddevice.OutputStream` replacement.

    A real `sounddevice` stream invokes the user supplied `callback` from a
    dedicated audio thread while the event loop is free to run. We mirror that
    here so the code under test exercises its real control flow without needing
    an audio device.
    """

    def __init__(self, *, samplerate: int, callback: Any, dtype: Any, channels: int) -> None:
        self.samplerate = samplerate
        self.callback = callback
        self.dtype = dtype
        self.channels = channels
        self.written: List[Any] = []
        self.error: BaseException | None = None
        self._thread: threading.Thread | None = None
        self._frame_count = 2

    def _run(self) -> None:
        while True:
            outdata = np.zeros((self._frame_count, self.channels), dtype=self.dtype)
            try:
                self.callback(outdata, self._frame_count, None, None)
            except FakeCallbackStop:
                break
            except BaseException as exc:  # pragma: no cover - only hit by the bug being fixed
                self.error = exc
                break
            self.written.append(outdata.copy())

    def __enter__(self) -> "FakeOutputStream":
        self._thread = threading.Thread(target=self._run)
        self._thread.start()
        return self

    def __exit__(self, *_args: Any) -> None:
        if self._thread is not None:
            self._thread.join()


class FakeSD:
    CallbackStop = FakeCallbackStop

    def __init__(self) -> None:
        self.streams: List[FakeOutputStream] = []

    def OutputStream(self, **kwargs: Any) -> FakeOutputStream:
        stream = FakeOutputStream(**kwargs)
        self.streams.append(stream)
        return stream


@pytest.fixture()
def fake_sd(monkeypatch: pytest.MonkeyPatch) -> FakeSD:
    sd = FakeSD()
    monkeypatch.setattr(local_audio_player, "sd", sd)
    return sd


async def test_play_accepts_one_dimensional_float32(fake_sd: FakeSD) -> None:
    # A 1-D float32 array (e.g. a mono waveform from soundfile / librosa) is a
    # valid input per the `play()` type signature. Before the fix this raised
    # `IndexError: tuple index out of range` because float32 input was not
    # reshaped to `(frames, channels)` like int16 input is.
    samples = np.array([0.1, 0.2, 0.3, -0.4, -0.5, 0.6], dtype=np.float32)

    await asyncio.wait_for(local_audio_player.LocalAudioPlayer().play(samples), timeout=5)

    assert len(fake_sd.streams) == 1
    stream = fake_sd.streams[0]
    assert stream.error is None
    assert stream.channels == 1

    played = np.concatenate(stream.written)[: len(samples)]
    assert played.shape == (len(samples), 1)
    assert np.allclose(played[:, 0], samples)


async def test_play_accepts_one_dimensional_int16(fake_sd: FakeSD) -> None:
    # Regression guard: the pre-existing int16 path must keep working.
    samples = np.array([1000, -2000, 3000, -4000], dtype=np.int16)

    await asyncio.wait_for(local_audio_player.LocalAudioPlayer().play(samples), timeout=5)

    stream = fake_sd.streams[0]
    assert stream.error is None
    played = np.concatenate(stream.written)[: len(samples)]
    assert played.shape == (len(samples), 1)
    assert np.allclose(played[:, 0], samples.astype(np.float32) / 32767.0)


async def test_play_stream_accepts_one_dimensional_float32(fake_sd: FakeSD) -> None:
    # `play_stream` has the same root cause: float32 buffers were not reshaped
    # to `(frames, channels)`, so the callback raised a broadcasting error.
    samples = np.array([0.1, 0.2, 0.3, -0.4, -0.5, 0.6], dtype=np.float32)

    async def buffer_stream() -> AsyncGenerator[Union[Any, None], None]:
        yield samples
        yield None

    await asyncio.wait_for(local_audio_player.LocalAudioPlayer().play_stream(buffer_stream()), timeout=5)

    stream = fake_sd.streams[0]
    assert stream.error is None

    played = np.concatenate(stream.written)
    # drop any leading zero-fill frames emitted before the producer delivered data
    nonzero = played[played[:, 0] != 0]
    assert np.allclose(nonzero[:, 0], samples)
