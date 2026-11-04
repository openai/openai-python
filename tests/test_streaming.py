from __future__ import annotations

import os
import ssl
import time
import socket
import asyncio
import importlib
import threading
from typing import Any, Iterator, AsyncIterator
from contextlib import aclosing, nullcontext
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing_extensions import override

import anyio
import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI, APITimeoutError, APIConnectionError, DefaultAioHttpClient
from openai._streaming import Stream, AsyncStream, ServerSentEvent


@pytest.fixture(
    params=[
        "httpx2",
        pytest.param(
            "httpx",
            marks=pytest.mark.skipif(
                os.environ.get("OPENAI_TEST_LEGACY_HTTPX") != "1", reason="requires the legacy HTTPX compatibility lane"
            ),
        ),
    ]
)
def http_module(request: pytest.FixtureRequest) -> Any:
    return importlib.import_module(request.param)


@pytest.mark.parametrize("mode", ["async", "aiohttp"])
@pytest.mark.parametrize("ending", ["complete", "truncate", "stall", "trickle"])
async def test_done_http11_connection_reuse(mode: str, ending: str, http_module: Any) -> None:
    if mode == "aiohttp" and http_module.__name__ == "httpx":
        pytest.skip("aiohttp uses HTTPX2")
    connections = 0
    requests = 0
    release = threading.Event()

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        @override
        def setup(self) -> None:
            nonlocal connections
            super().setup()
            connections += 1
            self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        def do_POST(self) -> None:
            nonlocal requests
            self.rfile.read(int(self.headers["Content-Length"]))
            requests += 1
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Transfer-Encoding", "chunked")
            self.end_headers()
            payload = (
                b'data: {"id":"synthetic","object":"chat.completion.chunk","created":0,"model":"synthetic",'
                b'"choices":[{"index":0,"delta":{"content":"hello"}}]}\n\ndata: [DONE]\n\n'
            )
            try:
                self.wfile.write(f"{len(payload):x}\r\n".encode() + payload + b"\r\n")
                if requests == 1:
                    if ending == "truncate":
                        self.close_connection = True
                        return
                    if ending == "stall":
                        release.wait(timeout=0.6)
                    if ending == "trickle":
                        # Trailer bytes do not yield body chunks, but must still
                        # obey the total cleanup deadline, not a per-read timeout.
                        self.wfile.write(b"0\r\nX-Synthetic: ")
                        for _ in range(15):
                            if release.wait(timeout=0.04):
                                return
                            self.wfile.write(b"a")
                        self.wfile.write(b"\r\n\r\n")
                        return
                self.wfile.write(b"0\r\n\r\n")
            except ConnectionError:
                self.close_connection = True

        @override
        def log_message(self, format: str, *args: object) -> None:  # noqa: A002
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01})
    thread.start()
    options: dict[str, Any] = {
        "api_key": "synthetic",
        "base_url": f"http://127.0.0.1:{server.server_port}/v1",
        "max_retries": 0,
        "timeout": http_module.Timeout(5, read=None),
    }
    transport_options: dict[str, Any] = {"trust_env": False, "limits": http_module.Limits(max_connections=1)}
    try:
        http_client = (
            DefaultAioHttpClient(**transport_options)
            if mode == "aiohttp"
            else http_module.AsyncClient(**transport_options)
        )
        async with AsyncOpenAI(**options, http_client=http_client) as async_client:
            for _ in range(2):
                async with await async_client.chat.completions.create(
                    model="synthetic", messages=[], stream=True
                ) as async_stream:
                    assert (await async_stream.__anext__()).choices[0].delta.content == "hello"
                    start = time.monotonic()
                    assert [chunk async for chunk in async_stream] == []
                    assert time.monotonic() - start < 0.4
    finally:
        release.set()
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()

    assert not thread.is_alive()
    assert requests == 2
    # A failed drain must discard the connection and release the only pool slot.
    assert connections == (1 if ending == "complete" else 2)


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("http_version", [b"HTTP/1.1", b"HTTP/2"])
async def test_done_discards_bytes_only_for_async_http11(
    sync: bool, http_version: bytes, http_module: Any, client: OpenAI, async_client: AsyncOpenAI
) -> None:
    read_tail = False

    def body() -> Iterator[bytes]:
        nonlocal read_tail
        yield b"data: [DONE]\n\n"
        read_tail = True
        yield b"\xff\n\n"  # Trailing data must not be decoded as SSE.

    iterator = body()
    async_iterator = to_aiter(iterator)

    class Body(http_module.SyncByteStream, http_module.AsyncByteStream):
        def __iter__(self) -> Iterator[bytes]:
            return iterator

        def __aiter__(self) -> AsyncIterator[bytes]:
            return async_iterator

    response = http_module.Response(200, stream=Body(), extensions={"http_version": http_version})
    if sync:
        assert list(Stream(cast_to=object, response=response, client=client)) == []
    else:
        assert [event async for event in AsyncStream(cast_to=object, response=response, client=async_client)] == []
    assert response.is_closed
    assert read_tail == (not sync and http_version == b"HTTP/1.1")


@pytest.mark.parametrize("cancel", [True, False], ids=["caller-cancel", "deadline"])
async def test_cancellation_during_done_drain_closes_response(
    cancel: bool, http_module: Any, async_client: AsyncOpenAI
) -> None:
    draining = asyncio.Event()

    class Body(http_module.AsyncByteStream):
        closed = False

        async def __aiter__(self) -> AsyncIterator[bytes]:
            yield b"data: [DONE]\n\n"
            draining.set()
            await asyncio.Event().wait()

        async def aclose(self) -> None:
            await anyio.sleep(0)
            self.closed = True

    body = Body()
    response = http_module.Response(200, stream=body)
    stream = AsyncStream(cast_to=object, response=response, client=async_client)
    task = asyncio.create_task(stream.__anext__())
    try:
        await asyncio.wait_for(draining.wait(), timeout=5)
        if cancel:
            task.cancel()
        with pytest.raises(asyncio.CancelledError if cancel else StopAsyncIteration):
            await task
        assert response.is_closed
        assert body.closed
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("delivered", [False, True], ids=["before-first-event", "after-first-event"])
@pytest.mark.parametrize(
    ("error_name", "expected_error"),
    [
        ("ReadTimeout", APITimeoutError),
        ("RemoteProtocolError", APIConnectionError),
        ("DecodingError", APIConnectionError),
        (ssl.SSLError, APIConnectionError),
        (anyio.EndOfStream, APIConnectionError),
    ],
)
async def test_request_errors_are_wrapped(
    sync: bool,
    delivered: bool,
    error_name: str | type[Exception],
    expected_error: type[APIConnectionError],
    http_module: Any,
) -> None:
    error_type = getattr(http_module, error_name) if isinstance(error_name, str) else error_name
    error = error_type("synthetic stream failure")
    requests: list[Any] = []
    first = (
        b'data: {"id":"synthetic","object":"chat.completion.chunk","created":0,"model":"synthetic",'
        b'"choices":[{"index":0,"delta":{"content":"hello"},"finish_reason":null}]}\n\n'
    )

    def body() -> Iterator[bytes]:
        if delivered:
            yield first
        raise error

    async def async_body() -> AsyncIterator[bytes]:
        for chunk in body():
            yield chunk

    def handler(request: Any) -> Any:
        requests.append(request)
        return http_module.Response(
            200, headers={"content-type": "text/event-stream"}, content=body() if sync else async_body()
        )

    received: list[str | None] = []
    if sync:
        with OpenAI(
            api_key="synthetic",
            max_retries=2,
            http_client=http_module.Client(transport=http_module.MockTransport(handler), trust_env=False),
        ) as client:
            stream = client.chat.completions.create(model="synthetic", messages=[], stream=True)
            with pytest.raises(expected_error) as caught:
                for chunk in stream:
                    received.append(chunk.choices[0].delta.content)
            assert stream.response.is_closed
    else:
        async with AsyncOpenAI(
            api_key="synthetic",
            max_retries=2,
            http_client=http_module.AsyncClient(transport=http_module.MockTransport(handler), trust_env=False),
        ) as async_client:
            async_stream = await async_client.chat.completions.create(model="synthetic", messages=[], stream=True)
            with pytest.raises(expected_error) as caught:
                async for chunk in async_stream:
                    received.append(chunk.choices[0].delta.content)
            assert async_stream.response.is_closed

    assert received == (["hello"] if delivered else [])
    assert len(requests) == 1
    assert caught.value.request is requests[0]
    assert caught.value.__cause__ is error


@pytest.mark.asyncio
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize(
    "error_type",
    [
        httpx2.ReadTimeout,
        httpx2.RemoteProtocolError,
        ValueError,
    ],
)
async def test_request_errors_from_response_processing_are_not_wrapped(
    sync: bool,
    error_type: type[Exception],
    client: OpenAI,
    async_client: AsyncOpenAI,
) -> None:
    error = error_type("response processing failure")
    request = httpx2.Request("POST", "https://example.com")

    class FailingModelBuilder:
        @classmethod
        def build(
            cls,
            *,
            response: httpx2.Response,
            data: object,
        ) -> FailingModelBuilder:
            assert response.request is request
            assert data == {"foo": True}
            raise error

    if sync:
        response = httpx2.Response(
            200,
            request=request,
            content=b'data: {"foo": true}\n\n',
        )
        stream = Stream(
            cast_to=FailingModelBuilder,
            client=client,
            response=response,
        )

        with pytest.raises(error_type) as exc_info:
            next(stream)
    else:
        response = httpx2.Response(
            200,
            request=request,
            content=b'data: {"foo": true}\n\n',
        )
        stream = AsyncStream(
            cast_to=FailingModelBuilder,
            client=async_client,
            response=response,
        )

        with pytest.raises(error_type) as exc_info:
            await stream.__anext__()

    assert exc_info.value is error


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
async def test_async_stream_aclose(async_client: AsyncOpenAI) -> None:
    def body() -> Iterator[bytes]:
        yield b"data: [DONE]\n\n"

    response = httpx2.Response(200, content=to_aiter(body()))
    stream = AsyncStream(cast_to=object, client=async_client, response=response)

    assert not response.is_closed
    await stream.aclose()
    assert response.is_closed

    # Either spelling remains safe after the response has already been closed.
    await stream.close()
    await stream.aclose()


@pytest.mark.asyncio
@pytest.mark.parametrize("raise_error", [False, True], ids=["early-exit", "exception"])
async def test_async_stream_aclosing(raise_error: bool) -> None:
    def body() -> Iterator[bytes]:
        yield (
            b'data: {"id":"chatcmpl-test","object":"chat.completion.chunk","created":0,'
            b'"model":"test-model","choices":[{"index":0,"delta":{"content":"hello"},'
            b'"finish_reason":null}]}\n\n'
        )
        yield b"data: [DONE]\n\n"

    response = httpx2.Response(200, content=to_aiter(body()), headers={"content-type": "text/event-stream"})
    async with AsyncOpenAI(
        api_key="fake-test-key",
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(lambda _request: response)),
    ) as client:
        stream = await client.chat.completions.create(model="test-model", messages=[], stream=True)
        with pytest.raises(ValueError, match="test exception") if raise_error else nullcontext():
            async with aclosing(stream):
                async for chunk in stream:
                    assert chunk.choices[0].delta.content == "hello"
                    assert not response.is_closed
                    if raise_error:
                        raise ValueError("test exception")
                    break

        assert response.is_closed


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
