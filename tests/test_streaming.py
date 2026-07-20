from __future__ import annotations

import asyncio
from typing import Iterator, Generator, AsyncIterator, AsyncGenerator, cast

import httpx
import pytest

from openai import OpenAI, AsyncOpenAI
from openai._streaming import Stream, AsyncStream, ServerSentEvent


@pytest.mark.asyncio
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_basic(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    def body() -> Iterator[bytes]:
        yield b"event: completion\n"
        yield b'data: {"foo":true}\n'
        yield b"\n"

    iterator = make_event_iterator(content=body(), sync=sync, client=client, async_client=async_client)

    sse = await iter_next(iterator)
    assert sse.event == "completion"
    assert sse.json() == {"foo": True}

    await assert_empty_iter(iterator)


@pytest.mark.asyncio
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_data_missing_event(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    def body() -> Iterator[bytes]:
        yield b'data: {"foo":true}\n'
        yield b"\n"

    iterator = make_event_iterator(content=body(), sync=sync, client=client, async_client=async_client)

    sse = await iter_next(iterator)
    assert sse.event is None
    assert sse.json() == {"foo": True}

    await assert_empty_iter(iterator)


@pytest.mark.asyncio
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_event_missing_data(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    def body() -> Iterator[bytes]:
        yield b"event: ping\n"
        yield b"\n"

    iterator = make_event_iterator(content=body(), sync=sync, client=client, async_client=async_client)

    sse = await iter_next(iterator)
    assert sse.event == "ping"
    assert sse.data == ""

    await assert_empty_iter(iterator)


@pytest.mark.asyncio
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_multiple_events(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    def body() -> Iterator[bytes]:
        yield b"event: ping\n"
        yield b"\n"
        yield b"event: completion\n"
        yield b"\n"

    iterator = make_event_iterator(content=body(), sync=sync, client=client, async_client=async_client)

    sse = await iter_next(iterator)
    assert sse.event == "ping"
    assert sse.data == ""

    sse = await iter_next(iterator)
    assert sse.event == "completion"
    assert sse.data == ""

    await assert_empty_iter(iterator)


@pytest.mark.asyncio
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_multiple_events_with_data(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    def body() -> Iterator[bytes]:
        yield b"event: ping\n"
        yield b'data: {"foo":true}\n'
        yield b"\n"
        yield b"event: completion\n"
        yield b'data: {"bar":false}\n'
        yield b"\n"

    iterator = make_event_iterator(content=body(), sync=sync, client=client, async_client=async_client)

    sse = await iter_next(iterator)
    assert sse.event == "ping"
    assert sse.json() == {"foo": True}

    sse = await iter_next(iterator)
    assert sse.event == "completion"
    assert sse.json() == {"bar": False}

    await assert_empty_iter(iterator)


@pytest.mark.asyncio
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_multiple_data_lines_with_empty_line(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    def body() -> Iterator[bytes]:
        yield b"event: ping\n"
        yield b"data: {\n"
        yield b'data: "foo":\n'
        yield b"data: \n"
        yield b"data:\n"
        yield b"data: true}\n"
        yield b"\n\n"

    iterator = make_event_iterator(content=body(), sync=sync, client=client, async_client=async_client)

    sse = await iter_next(iterator)
    assert sse.event == "ping"
    assert sse.json() == {"foo": True}
    assert sse.data == '{\n"foo":\n\n\ntrue}'

    await assert_empty_iter(iterator)


@pytest.mark.asyncio
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_data_json_escaped_double_new_line(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    def body() -> Iterator[bytes]:
        yield b"event: ping\n"
        yield b'data: {"foo": "my long\\n\\ncontent"}'
        yield b"\n\n"

    iterator = make_event_iterator(content=body(), sync=sync, client=client, async_client=async_client)

    sse = await iter_next(iterator)
    assert sse.event == "ping"
    assert sse.json() == {"foo": "my long\n\ncontent"}

    await assert_empty_iter(iterator)


@pytest.mark.asyncio
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_multiple_data_lines(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    def body() -> Iterator[bytes]:
        yield b"event: ping\n"
        yield b"data: {\n"
        yield b'data: "foo":\n'
        yield b"data: true}\n"
        yield b"\n\n"

    iterator = make_event_iterator(content=body(), sync=sync, client=client, async_client=async_client)

    sse = await iter_next(iterator)
    assert sse.event == "ping"
    assert sse.json() == {"foo": True}

    await assert_empty_iter(iterator)


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_special_new_line_character(
    sync: bool,
    client: OpenAI,
    async_client: AsyncOpenAI,
) -> None:
    def body() -> Iterator[bytes]:
        yield b'data: {"content":" culpa"}\n'
        yield b"\n"
        yield b'data: {"content":" \xe2\x80\xa8"}\n'
        yield b"\n"
        yield b'data: {"content":"foo"}\n'
        yield b"\n"

    iterator = make_event_iterator(content=body(), sync=sync, client=client, async_client=async_client)

    sse = await iter_next(iterator)
    assert sse.event is None
    assert sse.json() == {"content": " culpa"}

    sse = await iter_next(iterator)
    assert sse.event is None
    assert sse.json() == {"content": "  "}

    sse = await iter_next(iterator)
    assert sse.event is None
    assert sse.json() == {"content": "foo"}

    await assert_empty_iter(iterator)


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_multi_byte_character_multiple_chunks(
    sync: bool,
    client: OpenAI,
    async_client: AsyncOpenAI,
) -> None:
    def body() -> Iterator[bytes]:
        yield b'data: {"content":"'
        # bytes taken from the string 'известни' and arbitrarily split
        # so that some multi-byte characters span multiple chunks
        yield b"\xd0"
        yield b"\xb8\xd0\xb7\xd0"
        yield b"\xb2\xd0\xb5\xd1\x81\xd1\x82\xd0\xbd\xd0\xb8"
        yield b'"}\n'
        yield b"\n"

    iterator = make_event_iterator(content=body(), sync=sync, client=client, async_client=async_client)

    sse = await iter_next(iterator)
    assert sse.event is None
    assert sse.json() == {"content": "известни"}


@pytest.mark.asyncio
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_drains_remaining_bytes_after_done(
    sync: bool,
    client: OpenAI,
    async_client: AsyncOpenAI,
) -> None:
    """After a normal `[DONE]` termination the trailing bytes are consumed so that
    the underlying connection can be returned to the pool."""
    consumed: list[bytes] = []

    def body() -> Iterator[bytes]:
        for chunk in [b'data: {"foo":true}\n\n', b"data: [DONE]\n\n", b"\n"]:
            consumed.append(chunk)
            yield chunk

    stream = make_stream(content=body(), sync=sync, client=client, async_client=async_client)

    items = await iter_all(stream)
    assert len(items) == 1

    # the whole body, including the bytes trailing `[DONE]`, was drained
    assert consumed == [b'data: {"foo":true}\n\n', b"data: [DONE]\n\n", b"\n"]


@pytest.mark.asyncio
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_drain_failure_after_done_preserves_result(
    sync: bool,
    client: OpenAI,
    async_client: AsyncOpenAI,
) -> None:
    """A transport error while draining must not fail an already-completed stream.

    The server sent a valid `[DONE]`, so the result is complete; a connection drop
    while consuming the trailing bytes is cleanup noise and must still close the
    response rather than propagating to the caller.
    """

    def body() -> Iterator[bytes]:
        yield b'data: {"foo":true}\n\n'
        yield b"data: [DONE]\n\n"
        raise httpx.RemoteProtocolError("peer closed connection")

    stream = make_stream(content=body(), sync=sync, client=client, async_client=async_client)

    items = await iter_all(stream)
    assert len(items) == 1

    assert stream.response.is_closed


@pytest.mark.asyncio
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_drain_cancellation_after_done_still_closes_response(
    sync: bool,
    client: OpenAI,
    async_client: AsyncOpenAI,
) -> None:
    """Cancellation while draining must still release the connection.

    `[DONE]` has already been observed, so the drain is best-effort cleanup. If the
    caller cancels while we wait on the trailing bytes -- e.g. an `asyncio` timeout
    shorter than the HTTPX read timeout -- `CancelledError` is a `BaseException` and
    so bypasses the `httpx.HTTPError` handler around the drain. The close has to sit
    in a `finally` or the connection is leaked.
    """

    def body() -> Iterator[bytes]:
        yield b'data: {"foo":true}\n\n'
        yield b"data: [DONE]\n\n"
        raise asyncio.CancelledError

    stream = make_stream(content=body(), sync=sync, client=client, async_client=async_client)

    with pytest.raises(asyncio.CancelledError):
        await iter_all(stream)

    assert stream.response.is_closed


@pytest.mark.asyncio
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_does_not_drain_on_premature_termination(
    sync: bool,
    client: OpenAI,
    async_client: AsyncOpenAI,
) -> None:
    """A caller that stops before `[DONE]` must not drain the rest of the stream.

    Draining here would block until the server finished sending, which for a
    long-running or stalled completion defeats the point of breaking out early.
    """
    trailing = 100
    consumed: list[bytes] = []

    def body() -> Iterator[bytes]:
        for chunk in [b'data: {"foo":true}\n\n', *([b'data: {"bar":true}\n\n'] * trailing), b"data: [DONE]\n\n"]:
            consumed.append(chunk)
            yield chunk

    stream = make_stream(content=body(), sync=sync, client=client, async_client=async_client)

    # consume a single event, then abandon iteration and let the stream be collected
    await iter_next_item(stream)
    await close_stream(stream)

    # the remaining events were left on the wire rather than being drained
    assert len(consumed) < trailing, f"stream was drained: consumed {len(consumed)} chunks"


async def iter_all(stream: Stream[object] | AsyncStream[object]) -> list[object]:
    if isinstance(stream, AsyncStream):
        return [item async for item in stream]

    return list(stream)


async def iter_next_item(stream: Stream[object] | AsyncStream[object]) -> object:
    if isinstance(stream, AsyncStream):
        return await stream.__anext__()

    return next(iter(stream))


async def close_stream(stream: Stream[object] | AsyncStream[object]) -> None:
    """Close the underlying generator, mirroring what happens when an abandoned
    stream object is garbage collected."""
    if isinstance(stream, AsyncStream):
        await cast("AsyncGenerator[object, None]", stream._iterator).aclose()
    else:
        cast("Generator[object, None, None]", stream._iterator).close()


def make_stream(
    content: Iterator[bytes],
    *,
    sync: bool,
    client: OpenAI,
    async_client: AsyncOpenAI,
) -> Stream[object] | AsyncStream[object]:
    if sync:
        return Stream(cast_to=object, client=client, response=httpx.Response(200, content=content))

    return AsyncStream(cast_to=object, client=async_client, response=httpx.Response(200, content=to_aiter(content)))


async def to_aiter(iter: Iterator[bytes]) -> AsyncIterator[bytes]:
    for chunk in iter:
        yield chunk


async def iter_next(iter: Iterator[ServerSentEvent] | AsyncIterator[ServerSentEvent]) -> ServerSentEvent:
    if isinstance(iter, AsyncIterator):
        return await iter.__anext__()

    return next(iter)


async def assert_empty_iter(iter: Iterator[ServerSentEvent] | AsyncIterator[ServerSentEvent]) -> None:
    with pytest.raises((StopAsyncIteration, RuntimeError)):
        await iter_next(iter)


def make_event_iterator(
    content: Iterator[bytes],
    *,
    sync: bool,
    client: OpenAI,
    async_client: AsyncOpenAI,
) -> Iterator[ServerSentEvent] | AsyncIterator[ServerSentEvent]:
    if sync:
        return Stream(cast_to=object, client=client, response=httpx.Response(200, content=content))._iter_events()

    return AsyncStream(
        cast_to=object, client=async_client, response=httpx.Response(200, content=to_aiter(content))
    )._iter_events()
