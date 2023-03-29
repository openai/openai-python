import io
from typing import Optional


class CancelledError(Exception):
    def __init__(self, msg: str):
        self.msg = msg
        Exception.__init__(self, msg)

    def __str__(self):
        return self.msg

    __repr__ = __str__


class BufferReader(io.BytesIO):
    def __init__(self, buf: bytes = b"", desc: Optional[str] = None):
        self._len = len(buf)
        io.BytesIO.__init__(self, buf)
        self._progress = 0
        self._callback = progress(len(buf), desc=desc)

    def __len__(self):
        return self._len

    def read(self, n=-1):
        chunk = io.BytesIO.read(self, n)
        self._progress += len(chunk)
        if self._callback:
            try:
                self._callback(self._progress)
            except Exception as e:  # catches exception from the callback
                raise CancelledError("The upload was cancelled: {}".format(e))
        return chunk


def progress(total: float, desc: Optional[str]):
    import tqdm  # type: ignore

    meter = tqdm.tqdm(total=total, unit_scale=True, desc=desc)

    def incr(progress):
        meter.n = progress
        if progress == total:
            meter.close()
        else:
            meter.refresh()

    return incr


def MB(i: float) -> float:
    return int(i // 1024**2)
