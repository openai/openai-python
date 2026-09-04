from __future__ import annotations

from typing import Any
from collections.abc import Iterator, AsyncIterator

import httpx2
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


def test_done_closes_response_sync(client: OpenAI) -> None:
    """Sync stream closes response after [DONE]."""

    def body() -> Iterator[bytes]:
        yield b'data: {"foo":true}\n\n'
        yield b"data: [DONE]\n\n"
        yield b": trailing comment after done\n\n"

    response = httpx2.Response(200, content=body())
    stream: Stream[object] | AsyncStream[object] = Stream(cast_to=object, client=client, response=response)
    chunks = list(stream)

    assert chunks == [{"foo": True}]
    assert response.is_closed is True


@pytest.mark.asyncio
async def test_done_drains_remaining_body_async(async_client: AsyncOpenAI) -> None:
    """After [DONE], async drains remaining body for connection reuse."""
    exhausted = False

    def body() -> Iterator[bytes]:
        nonlocal exhausted
        yield b'data: {"foo":true}\n\n'
        yield b"data: [DONE]\n\n"
        yield b": trailing comment after done\n\n"
        exhausted = True

    async_body = to_aiter(body())
    response = httpx2.Response(200, content=async_body)
    stream = AsyncStream(cast_to=object, client=async_client, response=response)
    chunks = [chunk async for chunk in stream]

    assert chunks == [{"foo": True}]
    assert exhausted is True
    assert response.is_closed is True


@pytest.mark.asyncio
async def test_early_exit_without_done_doesnt_drain_async(async_client: AsyncOpenAI) -> None:
    """Early exit before [DONE] should not consume trailing body and close promptly."""
    drained = False
    exhausted = False

    async def patched_drain(*_args: Any, **_kwargs: Any) -> None:
        """Track if drain was called."""
        nonlocal drained
        drained = True

    def body() -> Iterator[bytes]:
        nonlocal exhausted
        yield b'data: {"foo":true}\n\n'
        # No [DONE] sent, consumer will exit early
        yield b": trailing comment that should not be consumed\n\n"
        exhausted = True

    async_body = to_aiter(body())
    response = httpx2.Response(200, content=async_body)

    # Patch drain_async_iterator to track if it's called
    import openai._streaming as streaming_module

    original_drain = streaming_module.drain_async_iterator
    streaming_module.drain_async_iterator = patched_drain

    try:
        stream = AsyncStream(cast_to=object, client=async_client, response=response)

        # Only consume the first chunk, exit early before [DONE]
        first_chunk = await stream.__anext__()
        assert first_chunk == {"foo": True}

        # Trailing body should NOT be exhausted since _done_seen is False
        assert exhausted is False

        # Explicitly close the generator to trigger finally block
        await stream._iterator.aclose()  # type: ignore[attr-defined]

        # Drain should NOT have been called since we didn't see [DONE]
        assert drained is False
        # Response should be closed
        assert response.is_closed is True
    finally:
        # Restore original drain function
        streaming_module.drain_async_iterator = original_drain


@pytest.mark.asyncio
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_drain_failure_after_done_preserves_result(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    """Transport errors while draining after [DONE] must not fail an already-complete stream."""

    def body() -> Iterator[bytes]:
        yield b'data: {"foo":true}\n\n'
        yield b"data: [DONE]\n\n"
        raise httpx2.RemoteProtocolError("peer closed connection")

    response = httpx2.Response(200, content=body() if sync else to_aiter(body()))

    if sync:
        stream: Stream[object] | AsyncStream[object] = Stream(cast_to=object, client=client, response=response)
        chunks = list(stream)
    else:
        stream = AsyncStream(cast_to=object, client=async_client, response=response)
        chunks = [chunk async for chunk in stream]

    assert chunks == [{"foo": True}]
    assert response.is_closed is True


@pytest.mark.asyncio
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_drain_decode_error_after_done_preserves_result(
    sync: bool, client: OpenAI, async_client: AsyncOpenAI
) -> None:
    """Malformed trailing bytes after [DONE] must not fail an already-complete stream."""

    def body() -> Iterator[bytes]:
        yield b'data: {"foo":true}\n\n'
        yield b"data: [DONE]\n\n"
        # Truncated multi-byte UTF-8 sequence that the SSE decoder will reject.
        yield b"data: \xff\n\n"

    response = httpx2.Response(200, content=body() if sync else to_aiter(body()))

    if sync:
        stream: Stream[object] | AsyncStream[object] = Stream(cast_to=object, client=client, response=response)
        chunks = list(stream)
    else:
        stream = AsyncStream(cast_to=object, client=async_client, response=response)
        chunks = [chunk async for chunk in stream]

    assert chunks == [{"foo": True}]
    assert response.is_closed is True


@pytest.mark.asyncio
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_drain_is_bounded_and_doesnt_block_indefinitely(
    sync: bool, client: OpenAI, async_client: AsyncOpenAI
) -> None:
    """Drain after [DONE] must timeout rather than wait for slow/infinite iterators."""

    class SyncSlowIterator:
        """Sync iterator that yields slowly after content to force timeout."""

        def __init__(self, content: Iterator[bytes]) -> None:
            self._content = content
            self._content_exhausted = False

        def __iter__(self) -> Iterator[bytes]:
            return self

        def __next__(self) -> bytes:
            if not self._content_exhausted:
                try:
                    return next(self._content)
                except StopIteration:
                    self._content_exhausted = True
            # After content is exhausted, yield slowly to force timeout during drain
            import time

            time.sleep(0.1)  # 100ms per item; 50ms drain timeout will hit after <1 item
            return b": heartbeat\n\n"

    class AsyncSlowIterator:
        """Async iterator that yields slowly after content to force timeout."""

        def __init__(self, content: AsyncIterator[bytes]) -> None:
            self._content = content
            self._content_exhausted = False

        def __aiter__(self) -> AsyncIterator[bytes]:
            return self

        async def __anext__(self) -> bytes:
            if not self._content_exhausted:
                try:
                    return await self._content.__anext__()
                except StopAsyncIteration:
                    self._content_exhausted = True
            # After content is exhausted, yield slowly to force timeout during drain
            import asyncio

            await asyncio.sleep(0.1)  # 100ms per item; 50ms drain timeout will hit after <1 item
            return b": heartbeat\n\n"

    def body() -> Iterator[bytes]:
        yield b'data: {"foo":true}\n\n'
        yield b"data: [DONE]\n\n"

    if sync:
        slow_iter = SyncSlowIterator(body())
        response = httpx2.Response(200, content=slow_iter)
        stream: Stream[object] | AsyncStream[object] = Stream(cast_to=object, client=client, response=response)
        chunks = list(stream)
    else:
        async_body = to_aiter(body())
        slow_iter = AsyncSlowIterator(async_body)
        response = httpx2.Response(200, content=slow_iter)
        stream = AsyncStream(cast_to=object, client=async_client, response=response)
        chunks = [chunk async for chunk in stream]

    # Stream should complete quickly with just the first item, not wait for the slow iterator
    assert chunks == [{"foo": True}]
    assert response.is_closed is True


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
        return Stream(cast_to=object, client=client, response=httpx2.Response(200, content=content))._iter_events()

    return AsyncStream(
        cast_to=object, client=async_client, response=httpx2.Response(200, content=to_aiter(content))
    )._iter_events()
