from __future__ import annotations

import queue
import asyncio
import threading
from types import SimpleNamespace
from typing import Any, AsyncGenerator
from typing_extensions import override

import numpy as np
import pytest
import numpy.typing as npt

from openai.helpers import LocalAudioPlayer, local_audio_player


class CallbackStop(Exception):
    pass


@pytest.mark.parametrize("explicit_stop", [False, True], ids=["exhausted", "none-sentinel"])
@pytest.mark.parametrize(
    "chunks,expected",
    [
        ([], [[0, 0, 0, 0]]),
        ([[32767, -32767]], [[1, -1, 0, 0]]),
        ([[32767, 0, -32767, 0]], [[1, 0, -1, 0], [0, 0, 0, 0]]),
        ([[32767], [0, -32767, 0, 32767]], [[1, 0, -1, 0], [1, 0, 0, 0]]),
    ],
    ids=["empty", "partial", "exact", "split"],
)
async def test_play_stream_silences_eof_buffer(
    monkeypatch: pytest.MonkeyPatch,
    chunks: list[list[int]],
    expected: list[list[int]],
    explicit_stop: bool,
) -> None:
    blocks: list[npt.NDArray[np.float32]] = []
    errors: list[BaseException] = []
    stopped = threading.Event()
    input_ready = threading.Event()

    class AudioQueue(queue.Queue[Any]):
        @override
        def put(self, item: Any, block: bool = True, timeout: float | None = None) -> None:
            super().put(item, block=block, timeout=timeout)
            if item is None:
                # Wait for actual EOF enqueueing, not just generator exhaustion.
                input_ready.set()

    class OutputStream:
        def __init__(self, *, callback: Any, channels: int, dtype: Any, samplerate: int) -> None:
            assert channels == 1
            assert dtype == np.float32
            assert samplerate == 24000
            self.callback = callback
            self.worker = threading.Thread(target=self.run, daemon=True)

        def run(self) -> None:
            try:
                assert input_ready.wait(timeout=5)
                for _ in range(len(expected)):
                    buffer: npt.NDArray[np.float32] = np.full((4, 1), 0.8125, dtype=np.float32)
                    try:
                        self.callback(buffer, len(buffer), None, None)
                    except CallbackStop:
                        stopped.set()
                    finally:
                        # PortAudio plays the final buffer even after CallbackStop.
                        blocks.append(buffer)
                    if stopped.is_set():
                        return
            except BaseException as exc:
                errors.append(exc)

        def __enter__(self) -> OutputStream:
            self.worker.start()
            return self

        def __exit__(self, *args: Any) -> None:
            self.worker.join(timeout=5)
            assert not self.worker.is_alive()

    async def audio() -> AsyncGenerator[npt.NDArray[np.int16] | None, None]:
        for chunk in chunks:
            yield np.array([[sample] for sample in chunk], dtype=np.int16)
        if explicit_stop:
            yield None

    monkeypatch.setattr(local_audio_player, "queue", SimpleNamespace(Queue=AudioQueue, Empty=queue.Empty))
    # Replace the adapter before resolving the optional sounddevice proxy, so the
    # regression uses no PortAudio library or audio hardware.
    monkeypatch.setattr(local_audio_player, "sd", SimpleNamespace(OutputStream=OutputStream, CallbackStop=CallbackStop))
    await asyncio.wait_for(LocalAudioPlayer().play_stream(audio()), timeout=10)

    assert not errors
    assert stopped.is_set()
    assert len(blocks) == len(expected)
    for buffer, expected_block in zip(blocks, expected, strict=True):
        np.testing.assert_array_equal(buffer, [[sample] for sample in expected_block])
