from __future__ import annotations

import json
from typing import Iterator, AsyncIterator

import httpx
import pytest

from openai import OpenAI, AsyncOpenAI
from openai._streaming import Stream, AsyncStream, ServerSentEvent, _check_stream_error, _parse_sse_data
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


class TestServerSentEventJson:
    """Tests for ServerSentEvent.json() error handling."""

    def test_valid_json(self) -> None:
        sse = ServerSentEvent(data='{"foo": true}', event="completion")
        assert sse.json() == {"foo": True}

    def test_empty_data_raises_json_decode_error(self) -> None:
        sse = ServerSentEvent(data="", event="completion")
        with pytest.raises(json.JSONDecodeError, match="Failed to parse SSE event data"):
            sse.json()

    def test_malformed_json_raises_descriptive_error(self) -> None:
        sse = ServerSentEvent(data="{invalid json}", event="completion")
        with pytest.raises(json.JSONDecodeError) as exc_info:
            sse.json()
        assert "completion" in str(exc_info.value)
        assert "invalid json" in str(exc_info.value)

    def test_truncated_json_raises_descriptive_error(self) -> None:
        sse = ServerSentEvent(data='{"key": "val', event="data")
        with pytest.raises(json.JSONDecodeError, match="Failed to parse SSE event data"):
            sse.json()


class TestCheckStreamError:
    """Tests for _check_stream_error helper."""

    def test_no_error_does_not_raise(self) -> None:
        data = {"choices": [{"delta": {"content": "hello"}}]}
        sse = ServerSentEvent(data='{}', event="completion")
        request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
        # Should not raise
        _check_stream_error(data, sse, request)

    def test_error_event_raises(self) -> None:
        data = {"error": {"message": "rate limit exceeded", "type": "rate_limit_error"}}
        sse = ServerSentEvent(data='{}', event="error")
        request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
        with pytest.raises(APIError, match="rate limit exceeded"):
            _check_stream_error(data, sse, request)

    def test_data_with_error_field_raises(self) -> None:
        data = {"error": {"message": "server error", "type": "server_error"}}
        sse = ServerSentEvent(data='{}', event="completion")
        request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
        with pytest.raises(APIError, match="server error"):
            _check_stream_error(data, sse, request)

    def test_error_with_top_level_message(self) -> None:
        """Test that top-level message field is used as fallback per API spec."""
        data = {"error": {"type": "server_error"}, "message": "Something went wrong"}
        sse = ServerSentEvent(data='{}', event="error")
        request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
        with pytest.raises(APIError, match="Something went wrong"):
            _check_stream_error(data, sse, request)

    def test_error_without_message_uses_default(self) -> None:
        data = {"error": {"type": "unknown_error"}}
        sse = ServerSentEvent(data='{}', event="completion")
        request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
        with pytest.raises(APIError, match="An error occurred during streaming"):
            _check_stream_error(data, sse, request)

    def test_error_with_string_error_field(self) -> None:
        data = {"error": "something broke"}
        sse = ServerSentEvent(data='{}', event="completion")
        request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
        with pytest.raises(APIError, match="An error occurred during streaming"):
            _check_stream_error(data, sse, request)

    def test_error_event_with_none_data_raises(self) -> None:
        """An error event with no payload should still raise, not be skipped."""
        sse = ServerSentEvent(data="", event="error")
        request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
        with pytest.raises(APIError, match="An error occurred during streaming"):
            _check_stream_error(None, sse, request)


class TestParseSSEData:
    """Tests for _parse_sse_data helper."""

    def test_valid_json_data(self) -> None:
        sse = ServerSentEvent(data='{"foo": "bar"}', event="completion")
        result = _parse_sse_data(sse)
        assert result == {"foo": "bar"}

    def test_empty_data_returns_none(self) -> None:
        sse = ServerSentEvent(data="", event="ping")
        result = _parse_sse_data(sse)
        assert result is None

    def test_none_data_returns_none(self) -> None:
        sse = ServerSentEvent(data=None, event="ping")
        result = _parse_sse_data(sse)
        assert result is None

    def test_malformed_json_raises_api_error(self) -> None:
        sse = ServerSentEvent(data="not valid json", event="completion")
        with pytest.raises(APIError, match="Failed to parse streaming response data"):
            _parse_sse_data(sse)


@pytest.mark.asyncio
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_invalid_utf8_skipped(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    """Test that invalid UTF-8 bytes in SSE data are skipped gracefully."""

    def body() -> Iterator[bytes]:
        # Valid event first
        yield b'data: {"content":"hello"}\n'
        yield b"\n"
        # Invalid UTF-8 line (0xff is never valid in UTF-8)
        yield b"data: \xff\xfe invalid\n"
        yield b"\n"
        # Another valid event after the invalid one
        yield b'data: {"content":"world"}\n'
        yield b"\n"

    iterator = make_event_iterator(content=body(), sync=sync, client=client, async_client=async_client)

    sse = await iter_next(iterator)
    assert sse.json() == {"content": "hello"}

    # The invalid UTF-8 line should be skipped, so we get the next valid event
    sse = await iter_next(iterator)
    assert sse.json() == {"content": "world"}

    await assert_empty_iter(iterator)


@pytest.mark.asyncio
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_error_event_handling(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    """Test that explicit error events (sse.event == 'error') are properly detected.

    This validates the fix for the previously unreachable error check that was
    nested inside the thread.* branch.
    """

    def body() -> Iterator[bytes]:
        yield b"event: error\n"
        yield b'data: {"error": {"message": "stream interrupted", "type": "server_error"}}\n'
        yield b"\n"

    iterator = make_event_iterator(content=body(), sync=sync, client=client, async_client=async_client)

    # The error event should be detected and we get an SSE with event="error"
    sse = await iter_next(iterator)
    assert sse.event == "error"
    assert sse.json()["error"]["message"] == "stream interrupted"


@pytest.mark.asyncio
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_error_event_empty_payload_at_sse_level(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    """Test that a bare error event with no data is properly yielded by the SSE decoder."""

    def body() -> Iterator[bytes]:
        yield b'data: {"content":"hello"}\n'
        yield b"\n"
        yield b"event: error\n"
        yield b"\n"

    iterator = make_event_iterator(content=body(), sync=sync, client=client, async_client=async_client)

    sse = await iter_next(iterator)
    assert sse.json() == {"content": "hello"}

    # The bare error event (empty data) should still be yielded by the decoder
    sse = await iter_next(iterator)
    assert sse.event == "error"
    assert sse.data == ""


def test_stream_error_event_empty_payload_raises(client: OpenAI) -> None:
    """Test that Stream.__stream__ raises APIError for error events with no payload.

    This ensures empty error events from backends/proxies are not silently skipped.
    """

    def body() -> Iterator[bytes]:
        yield b'data: {"content":"hello"}\n'
        yield b"\n"
        yield b"event: error\n"
        yield b"\n"

    request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
    response = httpx.Response(200, content=body(), request=request)

    stream: Stream[object] = Stream(
        cast_to=object,
        client=client,
        response=response,
    )

    with pytest.raises(APIError, match="An error occurred during streaming"):
        for _item in stream:
            pass


@pytest.mark.asyncio
async def test_async_stream_error_event_empty_payload_raises(async_client: AsyncOpenAI) -> None:
    """Test that AsyncStream.__stream__ raises APIError for error events with no payload."""

    async def body() -> AsyncIterator[bytes]:
        yield b'data: {"content":"hello"}\n'
        yield b"\n"
        yield b"event: error\n"
        yield b"\n"

    request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
    response = httpx.Response(200, content=body(), request=request)

    stream: AsyncStream[object] = AsyncStream(
        cast_to=object,
        client=async_client,
        response=response,
    )

    with pytest.raises(APIError, match="An error occurred during streaming"):
        async for _item in stream:
            pass


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
