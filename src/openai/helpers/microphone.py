# mypy: ignore-errors
from __future__ import annotations

import io
import time
import wave
import asyncio
from typing import Any, Type, Union, Generic, TypeVar, Callable, overload
from typing_extensions import TYPE_CHECKING, Literal

from .._types import FileTypes, FileContent
from .._extras import numpy as np, sounddevice as sd

if TYPE_CHECKING:
    import numpy.typing as npt

SAMPLE_RATE = 24000

DType = TypeVar("DType", bound=np.generic)


class Microphone(Generic[DType]):
    def __init__(
        self,
        channels: int = 1,
        dtype: Type[DType] = np.int16,
        should_record: Union[Callable[[], bool], None] = None,
        timeout: Union[float, None] = None,
    ):
        self.channels = channels
        self.dtype = dtype
        self.should_record = should_record
        self.buffer_chunks = []
        self.timeout = timeout
        self.has_record_function = callable(should_record)

    def _ndarray_to_wav(self, audio_data: npt.NDArray[DType]) -> FileTypes:
        buffer: FileContent = io.BytesIO()
        with wave.open(buffer, "w") as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(np.dtype(self.dtype).itemsize)
            wav_file.setframerate(SAMPLE_RATE)
            wav_file.writeframes(audio_data.tobytes())
        buffer.seek(0)
        return ("audio.wav", buffer, "audio/wav")

    @overload
    async def record(self, return_ndarray: Literal[True]) -> npt.NDArray[DType]: ...

    @overload
    async def record(self, return_ndarray: Literal[False]) -> FileTypes: ...

    @overload
    async def record(self, return_ndarray: None = ...) -> FileTypes: ...

    async def record(self, return_ndarray: Union[bool, None] = False) -> Union[npt.NDArray[DType], FileTypes]:
        loop = asyncio.get_event_loop()
        event = asyncio.Event()
        self.buffer_chunks: list[npt.NDArray[DType]] = []
        start_time = time.perf_counter()

        def callback(
            indata: npt.NDArray[DType],
            _frame_count: int,
            _time_info: Any,
            _status: Any,
        ):
            execution_time = time.perf_counter() - start_time
            reached_recording_timeout = execution_time > self.timeout if self.timeout is not None else False
            if reached_recording_timeout:
                loop.call_soon_threadsafe(event.set)
                raise sd.CallbackStop

            should_be_recording = self.should_record() if callable(self.should_record) else True
            if not should_be_recording:
                loop.call_soon_threadsafe(event.set)
                raise sd.CallbackStop

            self.buffer_chunks.append(indata.copy())

        stream = sd.InputStream(
            callback=callback,
            dtype=self.dtype,
            samplerate=SAMPLE_RATE,
            channels=self.channels,
        )
        with stream:
            await event.wait()

        # Concatenate all chunks into a single buffer, handle empty case
        concatenated_chunks: npt.NDArray[DType] = (
            np.concatenate(self.buffer_chunks, axis=0)
            if len(self.buffer_chunks) > 0
            else np.array([], dtype=self.dtype)
        )

        if return_ndarray:
            return concatenated_chunks
        else:
            return self._ndarray_to_wav(concatenated_chunks)
