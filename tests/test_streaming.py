from __future__ import annotations

from typing import Iterator, AsyncIterator

import httpx
import pytest

from openai import OpenAI, AsyncOpenAI
from openai._streaming import Stream, AsyncStream, ServerSentEvent
from openai._exceptions import APIError


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
async def test_thread_error_event(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    """Test that thread.error events are properly handled and raise APIError."""
    def body() -> Iterator[bytes]:
        yield b"event: thread.error\n"
        yield b'data: {"error": {"message": "Something went wrong"}}\n'
        yield b"\n"

    # Create a proper request object for the response
    request = httpx.Request("POST", "https://api.openai.com/v1/test")

    if sync:
        response = httpx.Response(200, content=body(), request=request)
        stream = Stream(cast_to=object, client=client, response=response)

        with pytest.raises(APIError) as exc_info:
            next(iter(stream))

        assert "Something went wrong" in str(exc_info.value)
    else:
        response = httpx.Response(200, content=to_aiter(body()), request=request)
        stream = AsyncStream(cast_to=object, client=async_client, response=response)

        with pytest.raises(APIError) as exc_info:
            await stream.__anext__()

        assert "Something went wrong" in str(exc_info.value)


@pytest.mark.asyncio
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_thread_non_error_event(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    """Test that thread.* events (non-error) are processed correctly."""
    def body() -> Iterator[bytes]:
        yield b"event: thread.run.created\n"
        yield b'data: {"id": "run_123", "status": "in_progress"}\n'
        yield b"\n"
        yield b"data: [DONE]\n"
        yield b"\n"

    # Create a proper request object for the response
    request = httpx.Request("POST", "https://api.openai.com/v1/test")

    if sync:
        response = httpx.Response(200, content=body(), request=request)
        stream = Stream(cast_to=object, client=client, response=response)

        result = next(iter(stream))
        assert result["event"] == "thread.run.created"
        assert result["data"]["id"] == "run_123"
    else:
        response = httpx.Response(200, content=to_aiter(body()), request=request)
        stream = AsyncStream(cast_to=object, client=async_client, response=response)

        result = await stream.__anext__()
        assert result["event"] == "thread.run.created"
        assert result["data"]["id"] == "run_123"


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


def make_stream_iterator(
    content: Iterator[bytes],
    *,
    sync: bool,
    client: OpenAI,
    async_client: AsyncOpenAI,
) -> Iterator[object] | AsyncIterator[object]:
    """Create a Stream or AsyncStream iterator for testing the full stream processing."""
    if sync:
        return iter(Stream(cast_to=object, client=client, response=httpx.Response(200, content=content)))

    return AsyncStream(
        cast_to=object, client=async_client, response=httpx.Response(200, content=to_aiter(content))
    ).__aiter__()
