import io


class CancelledError(Exception):
    def __init__(self, msg):
        self.msg = msg
        Exception.__init__(self, msg)

    def __str__(self):
        return self.msg

    __repr__ = __str__


class BufferReader(io.BytesIO):
    def __init__(self, buf=b"", desc=None):
        self._len = len(buf)
        io.BytesIO.__init__(self, buf)
        self._progress = 0
        self._callback = progress(len(buf), desc=desc)

    def __len__(self):
        return self._len

    def read(self, n=-1):
        try:
            result = io.BytesIO.read(self, n)
            self._progress += len(result)
            self._callback(self._progress)
            return result
        except Exception as e:
            pass


def progress(total, desc):
    import tqdm  # type: ignore

    meter = tqdm.tqdm(total=total, unit_scale=True, desc=desc)

    def incr(progress):
        meter.n = progress
        if progress == total:
            meter.close()
        else:
            meter.refresh()

    return incr


def MB(i):
    return int(i // 1024**2)
