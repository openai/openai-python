from __future__ import annotations

import os
import importlib
from typing import Any, Iterator, AsyncIterator
from contextlib import aclosing, nullcontext

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI, APITimeoutError, APIConnectionError
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


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("delivered", [False, True], ids=["before-first-event", "after-first-event"])
@pytest.mark.parametrize(
    ("error_name", "expected_error"),
    [
        ("ReadTimeout", APITimeoutError),
        ("RemoteProtocolError", APIConnectionError),
        ("DecodingError", APIConnectionError),
    ],
)
async def test_request_errors_are_wrapped(
    sync: bool, delivered: bool, error_name: str, expected_error: type[APIConnectionError], http_module: Any
) -> None:
    error = getattr(http_module, error_name)("synthetic stream failure")
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
