# Vendored from https://github.com/leenr/gzip-stream
import gzip
import io


class GZIPCompressedStream(io.RawIOBase):
    def __init__(self, stream, compression_level):
        assert 1 <= compression_level <= 9

        self._compression_level = compression_level
        self._stream = stream

        self._compressed_stream = io.BytesIO()
        self._compressor = gzip.GzipFile(
            mode="wb", fileobj=self._compressed_stream, compresslevel=compression_level
        )

        # because of the GZIP header written by `GzipFile.__init__`:
        self._compressed_stream.seek(0)

    @property
    def compression_level(self):
        return self._compression_level

    @property
    def stream(self):
        return self._stream

    def readable(self):
        return True

    def _read_compressed_into(self, b):
        buf = self._compressed_stream.read(len(b))
        b[: len(buf)] = buf
        return len(buf)

    def readinto(self, b):
        b = memoryview(b)

        offset = 0
        size = len(b)
        while offset < size:
            offset += self._read_compressed_into(b[offset:])
            if offset < size:
                # self._compressed_buffer now empty
                if self._compressor.closed:
                    # nothing to compress anymore
                    break
                # compress next bytes
                self._read_n_compress(size)

        return offset

    def _read_n_compress(self, size):
        assert size > 0

        data = self._stream.read(size)

        # rewind buffer to the start to free up memory
        # (because anything currently in the buffer should be already
        #  streamed off the object)
        self._compressed_stream.seek(0)
        self._compressed_stream.truncate(0)

        if data:
            self._compressor.write(data)
        else:
            # this will write final data (will flush zlib with Z_FINISH)
            self._compressor.close()

        # rewind to the buffer start
        self._compressed_stream.seek(0)

    def __repr__(self):
        return (
            "{self.__class__.__name__}("
            "{self.stream!r}, "
            "compression_level={self.compression_level!r}"
            ")"
        ).format(self=self)


__all__ = ("GZIPCompressedStream",)
