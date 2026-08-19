from __future__ import annotations

import asyncio
from typing import Iterator, AsyncIterator
from typing_extensions import override

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from openai._streaming import Stream, SSEDecoder, AsyncStream, ServerSentEvent, _SSELineDecoder


async def _aiter(chunks: list[bytes]) -> AsyncIterator[bytes]:
    for chunk in chunks:
        yield chunk


async def _decode(decoder: SSEDecoder, chunks: list[bytes], sync: bool) -> list[ServerSentEvent]:
    if sync:
        return list(decoder.iter_bytes(iter(chunks)))
    return [event async for event in decoder.aiter_bytes(_aiter(chunks))]


def _fragment(data: bytes, size: int) -> list[bytes]:
    return [data[i : i + size] for i in range(0, len(data), size)]


@pytest.mark.parametrize("sync", [True, False])
@pytest.mark.parametrize("line", [b":x\n", b"data:x\n", b"ignored:x\n"])
@pytest.mark.parametrize("fragment_size", [1, 97, 100000])
async def test_unterminated_event_limit(sync: bool, line: bytes, fragment_size: int) -> None:
    decoder = SSEDecoder(max_line_size=32, max_event_size=1024)
    with pytest.raises(ValueError, match="^SSE event exceeded maximum size$"):
        await _decode(decoder, _fragment(line * 2000, fragment_size), sync)
    assert decoder._data == []
    assert decoder._last_event_id is None


@pytest.mark.parametrize("sync", [True, False])
@pytest.mark.parametrize("suffix", [b"", b"\n", b"\n\n", b"\r\n\r\n"])
@pytest.mark.parametrize("fragment_size", [1, 17, 10000])
async def test_oversized_line(sync: bool, suffix: bytes, fragment_size: int) -> None:
    decoder = SSEDecoder(max_line_size=64, max_event_size=1024)
    with pytest.raises(ValueError, match="^SSE line exceeded maximum size$"):
        await _decode(decoder, _fragment(b"data:" + b"x" * 60 + suffix, fragment_size), sync)
    assert decoder._data == []


@pytest.mark.parametrize("sync", [True, False])
@pytest.mark.parametrize("ending", [b"\n", b"\r", b"\r\n"])
async def test_exact_limits_and_every_chunk_boundary(sync: bool, ending: bytes) -> None:
    frame = b"data:ok" + ending + ending
    for split in range(len(frame) + 1):
        events = await _decode(SSEDecoder(max_line_size=7, max_event_size=9), [frame[:split], b"", frame[split:]], sync)
        assert [event.data for event in events] == ["ok"]
        with pytest.raises(ValueError, match="SSE event exceeded"):
            await _decode(SSEDecoder(max_line_size=7, max_event_size=8), [frame[:split], frame[split:]], sync)


@pytest.mark.parametrize("sync", [True, False])
async def test_many_complete_events_reset_limit(sync: bool) -> None:
    events = await _decode(SSEDecoder(max_line_size=7, max_event_size=9), [b"data:ok\n\n" * 2000], sync)
    assert [event.data for event in events] == ["ok"] * 2000


@pytest.mark.parametrize("sync", [True, False])
async def test_large_legitimate_events(sync: bool) -> None:
    value = "x" * (2 * 1024 * 1024) + "известни\u2028"
    frame = ("data:" + value + "\r\n\r\n").encode()
    events = await _decode(SSEDecoder(), _fragment(frame, 4093), sync)
    assert [event.data for event in events] == [value]
    events = await _decode(SSEDecoder(), [b"data:x\n" * 10000 + b"\n"], sync)
    assert [event.data for event in events] == ["\n".join(["x"] * 10000)]


@pytest.mark.parametrize("sync", [True, False])
async def test_mixed_endings_utf8_and_eof(sync: bool) -> None:
    frame = "id:one\r\ndata:известни\r\n\ndata:two\n\rdata:unfinished".encode()
    events = await _decode(SSEDecoder(), _fragment(frame, 1), sync)
    assert [(event.data, event.id) for event in events] == [("известни", "one"), ("two", "one")]


@pytest.mark.parametrize("sync", [True, False])
async def test_comments_are_discarded_incrementally(sync: bool) -> None:
    decoder = SSEDecoder(max_event_size=100000)

    def chunks() -> Iterator[bytes]:
        for _ in range(10000):
            yield b":x\n"
            assert decoder._data == []
        yield b"data:ok\n"
        assert decoder._data == ["ok"]
        yield b"\n"

    async def achunks() -> AsyncIterator[bytes]:
        for chunk in chunks():
            yield chunk

    events = list(decoder.iter_bytes(chunks())) if sync else [e async for e in decoder.aiter_bytes(achunks())]
    assert [event.data for event in events] == ["ok"]


def test_partial_line_uses_bounded_mutable_buffer() -> None:
    decoder = _SSELineDecoder(max_line_size=4096, max_event_size=8192)
    for _ in range(4096):
        assert list(decoder.feed(b"x")) == []
    assert isinstance(decoder._buffer, bytearray)
    assert len(decoder._buffer) == 4096
    with pytest.raises(ValueError, match="SSE line exceeded"):
        list(decoder.feed(b"x" * 10000))
    assert len(decoder._buffer) == 4096


@pytest.mark.parametrize("sync", [True, False])
async def test_custom_limits_and_validation(sync: bool) -> None:
    for limits in [{"max_line_size": 0}, {"max_event_size": -1}]:
        with pytest.raises(ValueError, match="must be positive"):
            SSEDecoder(**limits)
    events = await _decode(
        SSEDecoder(max_line_size=1024, max_event_size=2048), [b"data:" + b"x" * 1000 + b"\n\n"], sync
    )
    assert events[0].data == "x" * 1000


class _SyncBody(httpx2.SyncByteStream):
    closed = False
    reads = 0

    @override
    def __iter__(self) -> Iterator[bytes]:
        while True:
            self.reads += 1
            yield b"data:x\n"

    @override
    def close(self) -> None:
        self.closed = True


class _AsyncBody(httpx2.AsyncByteStream):
    closed = False
    reads = 0

    @override
    async def __aiter__(self) -> AsyncIterator[bytes]:
        while True:
            self.reads += 1
            yield b"data:x\n"

    @override
    async def aclose(self) -> None:
        self.closed = True


def test_sync_limit_closes_response(client: OpenAI) -> None:
    body = _SyncBody()
    response = httpx2.Response(200, stream=body, request=httpx2.Request("GET", "https://example.invalid"))
    stream = Stream(cast_to=object, client=client, response=response)
    stream._decoder = SSEDecoder(max_event_size=21)
    with pytest.raises(ValueError, match="SSE event exceeded"):
        next(stream)
    assert response.is_closed and body.closed
    assert body.reads == 4
    assert stream._decoder._data == []


async def test_async_limit_closes_response(async_client: AsyncOpenAI) -> None:
    body = _AsyncBody()
    response = httpx2.Response(200, stream=body, request=httpx2.Request("GET", "https://example.invalid"))
    stream = AsyncStream(cast_to=object, client=async_client, response=response)
    decoder = SSEDecoder(max_event_size=21)
    stream._decoder = decoder
    with pytest.raises(ValueError, match="SSE event exceeded"):
        await stream.__anext__()
    assert response.is_closed and body.closed
    assert body.reads == 4
    assert decoder._data == []


async def test_cancellation_clears_partial_event_and_closes_response(async_client: AsyncOpenAI) -> None:
    started = asyncio.Event()

    class PausedBody(_AsyncBody):
        @override
        async def __aiter__(self) -> AsyncIterator[bytes]:
            yield b"data:partial\n"
            started.set()
            await asyncio.Event().wait()

    body = PausedBody()
    response = httpx2.Response(200, stream=body, request=httpx2.Request("GET", "https://example.invalid"))
    stream = AsyncStream(cast_to=object, client=async_client, response=response)
    decoder = SSEDecoder()
    stream._decoder = decoder
    task = asyncio.create_task(stream.__anext__())
    await started.wait()
    assert decoder._data == ["partial"]
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert response.is_closed and body.closed
    assert decoder._data == []


@pytest.mark.parametrize("sync", [True, False])
async def test_context_exit_after_event(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    if sync:
        response = httpx2.Response(200, content=iter([b"data:{}\n\n", b"data:partial"]))
        with Stream(cast_to=object, client=client, response=response) as stream:
            assert next(stream) == {}
    else:
        response = httpx2.Response(200, content=_aiter([b"data:{}\n\n", b"data:partial"]))
        async with AsyncStream(cast_to=object, client=async_client, response=response) as astream:
            assert await astream.__anext__() == {}
    assert response.is_closed
