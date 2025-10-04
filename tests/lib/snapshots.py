from __future__ import annotations

import os
import json
from typing import Any, Callable, Awaitable
from typing_extensions import TypeVar

import httpx
from respx import MockRouter
from inline_snapshot import get_snapshot_value

from openai import OpenAI, AsyncOpenAI

_T = TypeVar("_T")


def make_snapshot_request(
    func: Callable[[OpenAI], _T],
    *,
    content_snapshot: Any,
    respx_mock: MockRouter,
    mock_client: OpenAI,
    path: str,
) -> _T:
    live = os.environ.get("OPENAI_LIVE") == "1"
    if live:

        def _on_response(response: httpx.Response) -> None:
            # update the content snapshot
            assert json.dumps(json.loads(response.read())) == content_snapshot

        respx_mock.stop()

        client = OpenAI(
            http_client=httpx.Client(
                event_hooks={
                    "response": [_on_response],
                }
            )
        )
    else:
        respx_mock.post(path).mock(
            return_value=httpx.Response(
                200,
                content=get_snapshot_value(content_snapshot),
                headers={"content-type": "application/json"},
            )
        )

        client = mock_client

    result = func(client)

    if live:
        client.close()

    return result


async def make_async_snapshot_request(
    func: Callable[[AsyncOpenAI], Awaitable[_T]],
    *,
    content_snapshot: Any,
    respx_mock: MockRouter,
    mock_client: AsyncOpenAI,
    path: str,
) -> _T:
    live = os.environ.get("OPENAI_LIVE") == "1"
    if live:

        async def _on_response(response: httpx.Response) -> None:
            # update the content snapshot
            assert json.dumps(json.loads(await response.aread())) == content_snapshot

        respx_mock.stop()

        client = AsyncOpenAI(
            http_client=httpx.AsyncClient(
                event_hooks={
                    "response": [_on_response],
                }
            )
        )
    else:
        respx_mock.post(path).mock(
            return_value=httpx.Response(
                200,
                content=get_snapshot_value(content_snapshot),
                headers={"content-type": "application/json"},
            )
        )

        client = mock_client

    result = await func(client)

    if live:
        await client.close()

    return result
