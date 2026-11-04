from __future__ import annotations

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI

from .test_large_payload_contract import CompressedStream, AsyncCompressedStream, compressed_response


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
