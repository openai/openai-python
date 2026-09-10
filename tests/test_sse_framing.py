from __future__ import annotations

import asyncio
from typing import Iterable, Iterator, AsyncIterator
from typing_extensions import override

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from openai._streaming import Stream, SSEDecoder, AsyncStream, ServerSentEvent, _SSELineDecoder


async def _aiter(chunks: Iterable[bytes]) -> AsyncIterator[bytes]:
    for chunk in chunks:
        yield chunk


async def _decode(decoder: SSEDecoder, chunks: Iterable[bytes], sync: bool) -> list[ServerSentEvent]:
    if sync:
        return list(decoder.iter_bytes(iter(chunks)))
    return [event async for event in decoder.aiter_bytes(_aiter(chunks))]


def _fragment(data: bytes, size: int) -> list[bytes]:
    return [data[i : i + size] for i in range(0, len(data), size)]


@pytest.mark.parametrize("sync", [True, False])
@pytest.mark.parametrize("line", [b":x\n", b"data:x\n", b"ignored:x\n"])
@pytest.mark.parametrize("fragment_size", [1, 97, 100000])
async def test_unterminated_event(sync: bool, line: bytes, fragment_size: int) -> None:
    decoder = SSEDecoder()
    assert await _decode(decoder, _fragment(line * 2000, fragment_size), sync) == []
    assert decoder._data == []
    assert decoder._last_event_id is None


@pytest.mark.parametrize("sync", [True, False])
@pytest.mark.parametrize("ending", [b"\n", b"\r", b"\r\n"])
async def test_every_chunk_boundary(sync: bool, ending: bytes) -> None:
    frame = b"data:ok" + ending + ending
    for split in range(len(frame) + 1):
        events = await _decode(SSEDecoder(), [frame[:split], b"", frame[split:]], sync)
        assert [event.data for event in events] == ["ok"]


@pytest.mark.parametrize("sync", [True, False])
async def test_many_complete_events(sync: bool) -> None:
    events = await _decode(SSEDecoder(), [b"data:ok\n\n" * 2000], sync)
    assert [event.data for event in events] == ["ok"] * 2000


@pytest.mark.parametrize("sync", [True, False])
async def test_event_larger_than_64_mib(sync: bool) -> None:
    # A fixed regression for the rejected 64 MiB ceiling, not a stress sweep.
    # Reuse the input chunk and avoid allocating a second full expected payload.
    def chunks() -> Iterator[bytes]:
        yield b"data:"
        chunk = b"x" * (1024 * 1024)
        for _ in range(64):
            yield chunk
        yield b"x\n\n"

    events = await _decode(SSEDecoder(), chunks(), sync)
    assert len(events) == 1
    assert len(events[0].data) == 64 * 1024 * 1024 + 1
    assert events[0].data.count("x") == len(events[0].data)


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
@pytest.mark.parametrize("line", [b":x\n", b"ignored:x\n"])
async def test_ignored_lines_are_discarded_incrementally(sync: bool, line: bytes) -> None:
    decoder = SSEDecoder()

    def chunks() -> Iterator[bytes]:
        for _ in range(10000):
            yield line
            assert decoder._data == []
        yield b"data:ok\n"
        assert decoder._data == ["ok"]
        yield b"\n"

    async def achunks() -> AsyncIterator[bytes]:
        for chunk in chunks():
            yield chunk

    events = list(decoder.iter_bytes(chunks())) if sync else [e async for e in decoder.aiter_bytes(achunks())]
    assert [event.data for event in events] == ["ok"]


def test_partial_line_uses_mutable_buffer() -> None:
    decoder = _SSELineDecoder()
    for _ in range(4096):
        assert list(decoder.feed(b"x")) == []
    assert isinstance(decoder._buffer, bytearray)
    assert len(decoder._buffer) == 4096
    assert list(decoder.feed(b"\n")) == [b"x" * 4096]
    assert not decoder._buffer


class _SyncBody(httpx2.SyncByteStream):
    closed = False

    @override
    def __iter__(self) -> Iterator[bytes]:
        yield b"data:partial\n"
        raise RuntimeError("stream interrupted")

    @override
    def close(self) -> None:
        self.closed = True


class _AsyncBody(httpx2.AsyncByteStream):
    closed = False

    @override
    async def __aiter__(self) -> AsyncIterator[bytes]:
        yield b"data:partial\n"
        raise RuntimeError("stream interrupted")

    @override
    async def aclose(self) -> None:
        self.closed = True


def test_sync_interruption_closes_response(client: OpenAI) -> None:
    body = _SyncBody()
    response = httpx2.Response(200, stream=body, request=httpx2.Request("GET", "https://example.invalid"))
    stream = Stream(cast_to=object, client=client, response=response)
    stream._decoder = SSEDecoder()
    with pytest.raises(RuntimeError, match="stream interrupted"):
        next(stream)
    assert response.is_closed and body.closed
    assert stream._decoder._data == []


async def test_async_interruption_closes_response(async_client: AsyncOpenAI) -> None:
    body = _AsyncBody()
    response = httpx2.Response(200, stream=body, request=httpx2.Request("GET", "https://example.invalid"))
    stream = AsyncStream(cast_to=object, client=async_client, response=response)
    decoder = SSEDecoder()
    stream._decoder = decoder
    with pytest.raises(RuntimeError, match="stream interrupted"):
        await stream.__anext__()
    assert response.is_closed and body.closed
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
