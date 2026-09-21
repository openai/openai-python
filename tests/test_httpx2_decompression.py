from __future__ import annotations

import gzip
import json
import zlib
from typing import Any, Callable, Iterator, AsyncIterator
from typing_extensions import override

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI

from .test_large_payload_contract import PAYLOAD_SIZE, assert_intact, response_body


class CompressedStream(httpx2.SyncByteStream):
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.closed = False

    @override
    def __iter__(self) -> Iterator[bytes]:
        # One small network chunk must not inflate into one enormous chunk.
        yield self.data

    @override
    def close(self) -> None:
        self.closed = True


class AsyncCompressedStream(httpx2.AsyncByteStream):
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.closed = False

    @override
    async def __aiter__(self) -> AsyncIterator[bytes]:
        yield self.data

    @override
    async def aclose(self) -> None:
        self.closed = True


def compressed_response(
    stream: CompressedStream | AsyncCompressedStream, encoding: str, content_type: str = "application/json"
) -> httpx2.Response:
    # Passing a stream avoids eager decoding in Response's constructor.
    return httpx2.Response(200, headers={"content-encoding": encoding, "content-type": content_type}, stream=stream)


async def check_large_compressed_responses(encoding: str, compress: Callable[[bytes], bytes]) -> None:
    text = "x" * PAYLOAD_SIZE
    body = json.dumps(response_body(text)).encode()
    data = compress(body)
    stream = CompressedStream(data)
    with OpenAI(
        api_key="test-key",
        max_retries=0,
        http_client=httpx2.Client(transport=httpx2.MockTransport(lambda _: compressed_response(stream, encoding))),
    ) as client:
        with client.responses.with_streaming_response.create(model="gpt-4o-mini", input="Hello") as response:
            size = 0
            for chunk in response.iter_bytes():
                # The upstream decoder's chunk bound is not a response-size cap.
                assert len(chunk) <= 1024 * 1024
                size += len(chunk)
            assert size == len(body)
        assert stream.closed
        stream = CompressedStream(data)
        assert_intact(client.responses.create(model="gpt-4o-mini", input="Hello").output_text, text)
        assert stream.closed

    async_stream = AsyncCompressedStream(data)
    async with AsyncOpenAI(
        api_key="test-key",
        max_retries=0,
        http_client=httpx2.AsyncClient(
            transport=httpx2.MockTransport(lambda _: compressed_response(async_stream, encoding))
        ),
    ) as async_client:
        async with async_client.responses.with_streaming_response.create(
            model="gpt-4o-mini", input="Hello"
        ) as async_response:
            size = 0
            async for chunk in async_response.iter_bytes():
                assert len(chunk) <= 1024 * 1024
                size += len(chunk)
            assert size == len(body)
        assert async_stream.closed
        async_stream = AsyncCompressedStream(data)
        result = await async_client.responses.create(model="gpt-4o-mini", input="Hello")
        assert_intact(result.output_text, text)
        assert async_stream.closed

    event: dict[str, Any] = {
        "type": "response.output_text.delta",
        "delta": text,
        "item_id": "msg_test",
        "output_index": 0,
        "content_index": 0,
        "sequence_number": 0,
        "logprobs": [],
    }
    data = compress(b"data: " + json.dumps(event).encode() + b"\n\ndata: [DONE]\n\n")
    stream = CompressedStream(data)
    with OpenAI(
        api_key="test-key",
        max_retries=0,
        http_client=httpx2.Client(
            transport=httpx2.MockTransport(lambda _: compressed_response(stream, encoding, "text/event-stream"))
        ),
    ) as client:
        with client.responses.create(model="gpt-4o-mini", input="Hello", stream=True) as events:
            received = list(events)
            assert len(received) == 1 and received[0].type == "response.output_text.delta"
            assert_intact(received[0].delta, text)
        assert stream.closed

    async_stream = AsyncCompressedStream(data)
    async with AsyncOpenAI(
        api_key="test-key",
        max_retries=0,
        http_client=httpx2.AsyncClient(
            transport=httpx2.MockTransport(lambda _: compressed_response(async_stream, encoding, "text/event-stream"))
        ),
    ) as async_client:
        async with await async_client.responses.create(model="gpt-4o-mini", input="Hello", stream=True) as async_events:
            received = [event async for event in async_events]
            assert len(received) == 1 and received[0].type == "response.output_text.delta"
            assert_intact(received[0].delta, text)
        assert async_stream.closed


async def test_large_compressed_responses() -> None:
    # Keep all high-memory cases sequential, including under pytest-xdist.
    await check_large_compressed_responses("gzip", gzip.compress)
    await check_large_compressed_responses("deflate", zlib.compress)


@pytest.mark.parametrize("encoding", ["gzip", "deflate"])
async def test_decoding_failure_closes_response_stream(encoding: str) -> None:
    stream = CompressedStream(b"not a compressed stream")
    with OpenAI(
        api_key="test-key",
        max_retries=0,
        http_client=httpx2.Client(transport=httpx2.MockTransport(lambda _: compressed_response(stream, encoding))),
    ) as client:
        with client.responses.with_streaming_response.create(model="gpt-4o-mini", input="Hello") as response:
            with pytest.raises(httpx2.DecodingError):
                list(response.iter_bytes())
            # Check before context-manager cleanup can hide an upstream leak.
            assert stream.closed
            assert response.http_response.is_closed

    async_stream = AsyncCompressedStream(b"not a compressed stream")
    async with AsyncOpenAI(
        api_key="test-key",
        max_retries=0,
        http_client=httpx2.AsyncClient(
            transport=httpx2.MockTransport(lambda _: compressed_response(async_stream, encoding))
        ),
    ) as async_client:
        async with async_client.responses.with_streaming_response.create(
            model="gpt-4o-mini", input="Hello"
        ) as async_response:
            with pytest.raises(httpx2.DecodingError):
                _ = [chunk async for chunk in async_response.iter_bytes()]
            assert async_stream.closed
            assert async_response.http_response.is_closed
