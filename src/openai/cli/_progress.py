from __future__ import annotations
import io
from typing import Callable
from typing_extensions import override
import tqdm

class CancelledError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)

class BufferReader(io.BytesIO):
    def __init__(self, buf: bytes = b"", desc: str | None = None) -> None:
        super().__init__(buf)
        self._progress = 0
        self._callback = progress(len(buf), desc=desc)

    def __len__(self) -> int:
        return len(self.getvalue())

    @override
    def read(self, n: int | None = -1) -> bytes:
        chunk = super().read(n)
        self._progress += len(chunk)

        try:
            self._callback(self._progress)
        except Exception as e:
            raise CancelledError(f"The upload was cancelled: {e}")

        return chunk

def progress(total: float, desc: str | None) -> Callable[[float], None]:
    meter = tqdm.tqdm(total=total, unit_scale=True, desc=desc)

    def incr(progress: float) -> None:
        meter.n = progress
        if progress == total:
            meter.close()
        else:
            meter.refresh()

    return incr

def MB(i: int) -> int:
    return i // 1024**2
