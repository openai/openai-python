from __future__ import annotations

from typing import Iterator, AsyncIterator

import httpx
import pytest

from openai import OpenAI, AsyncOpenAI
from openai._exceptions import APIError
from openai._streaming import Stream, AsyncStream


@pytest.mark.asyncio
@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_thread_event_error_raises(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    def body() -> Iterator[bytes]:
        yield b"event: thread.error\n"
        yield b'data: {"error": {"message": "boom"}}\n'
        yield b"\n"

    iterator = make_stream_iterator(content=body(), sync=sync, client=client, async_client=async_client)

    with pytest.raises(APIError, match="boom"):
        await iter_next(iterator)


async def to_aiter(iter: Iterator[bytes]) -> AsyncIterator[bytes]:
    for chunk in iter:
        yield chunk


async def iter_next(iter: Iterator[object] | AsyncIterator[object]) -> object:
    if isinstance(iter, AsyncIterator):
        return await iter.__anext__()

    return next(iter)


def make_stream_iterator(
    content: Iterator[bytes],
    *,
    sync: bool,
    client: OpenAI,
    async_client: AsyncOpenAI,
) -> Iterator[object] | AsyncIterator[object]:
    request = httpx.Request("GET", "http://test")
    if sync:
        response = httpx.Response(200, request=request, content=content)
        return iter(Stream(cast_to=object, client=client, response=response))

    response = httpx.Response(200, request=request, content=to_aiter(content))
    return AsyncStream(cast_to=object, client=async_client, response=response).__aiter__()
