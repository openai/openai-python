from __future__ import annotations

import asyncio
from email import policy
from typing import Any, AsyncIterator, cast
from unittest import mock
from collections import deque
from dataclasses import field, dataclass
from email.parser import BytesParser

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI, NotFoundError, BadRequestError
from openai._types import Omit, omit
from openai.types.video import Video

# The existing video helpers are deprecated, but their compatibility still matters.
# pyright: reportDeprecated=false

VIDEO_ID = "video_synthetic"


@dataclass
class Transport:
    responses: deque[httpx2.Response] = field(default_factory=deque[httpx2.Response])
    requests: list[httpx2.Request] = field(default_factory=list[httpx2.Request])

    def send(self, request: httpx2.Request) -> httpx2.Response:
        self.requests.append(request)
        return self.responses.popleft()


@pytest.fixture
def transport() -> Transport:
    return Transport()


@pytest.fixture(params=[False, True], ids=["sync", "async"])
async def sdk_client(request: pytest.FixtureRequest, transport: Transport) -> AsyncIterator[OpenAI | AsyncOpenAI]:
    options: dict[str, Any] = {
        "api_key": "fake-test-key",
        "base_url": "https://example.test/v1",
        "max_retries": 0,
        "timeout": 11.0,
        "default_headers": {"X-Client-Option": "client"},
        "default_query": {"client_query": "inherited"},
    }
    if request.param:
        async with AsyncOpenAI(
            **options, http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport.send), trust_env=False)
        ) as client:
            yield client
    else:
        with OpenAI(
            **options, http_client=httpx2.Client(transport=httpx2.MockTransport(transport.send), trust_env=False)
        ) as client:
            yield client


def video_response(status: str, *, headers: dict[str, str] | None = None) -> httpx2.Response:
    return httpx2.Response(
        200,
        headers=headers,
        json={
            "id": VIDEO_ID,
            "created_at": 123,
            "model": "sora-2",
            "object": "video",
            "progress": 100 if status == "completed" else 0,
            "seconds": "4",
            "size": "720x1280",
            "status": status,
            "error": {"code": "synthetic_failure", "message": "Synthetic failure"} if status == "failed" else None,
        },
    )


async def poll(client: OpenAI | AsyncOpenAI, interval: int | Omit = omit) -> Video:
    with pytest.warns(DeprecationWarning, match="Sora API"):
        if isinstance(client, AsyncOpenAI):
            return await client.videos.poll(VIDEO_ID, poll_interval_ms=interval)
        return client.videos.poll(VIDEO_ID, poll_interval_ms=interval)


async def create_and_poll(client: OpenAI | AsyncOpenAI, **kwargs: Any) -> Video:
    with pytest.warns(DeprecationWarning, match="Sora API"):
        if isinstance(client, AsyncOpenAI):
            return await client.videos.create_and_poll(**kwargs)
        return client.videos.create_and_poll(**kwargs)


@pytest.mark.parametrize("status", ["completed", "failed", "future_terminal_status"])
async def test_terminal_status_returns_without_sleeping(
    sdk_client: OpenAI | AsyncOpenAI, transport: Transport, status: str
) -> None:
    transport.responses.append(video_response(status))
    with mock.patch.object(sdk_client.videos, "_sleep") as sleep:
        result = await poll(sdk_client)
    assert isinstance(result, Video)
    assert result.id == VIDEO_ID
    assert result.status == status
    if status == "failed":
        assert result.error is not None
        assert result.error.code == "synthetic_failure"
    sleep.assert_not_called()
    assert len(transport.requests) == 1
    assert transport.requests[0].headers["X-Stainless-Poll-Helper"] == "true"


@pytest.mark.parametrize(
    ("interval", "first_headers", "seconds"),
    [(omit, {}, 1.0), (omit, {"openai-poll-after-ms": "2000"}, 2.0), (250, {}, 0.25), (0, {}, 0.0)],
    ids=["default", "server-hint", "explicit", "zero"],
)
async def test_pending_statuses_preserve_poll_interval_and_headers(
    sdk_client: OpenAI | AsyncOpenAI,
    transport: Transport,
    interval: int | Omit,
    first_headers: dict[str, str],
    seconds: float,
) -> None:
    transport.responses.extend(
        [
            video_response("queued", headers=first_headers),
            video_response("in_progress", headers={"openai-poll-after-ms": "9000"}),
            video_response("completed"),
        ]
    )
    with mock.patch.object(sdk_client.videos, "_sleep") as sleep:
        result = await poll(sdk_client, interval)
    assert result.status == "completed"
    assert sleep.call_args_list == [mock.call(seconds)] * 2
    if isinstance(sdk_client, AsyncOpenAI):
        cast(mock.AsyncMock, sleep).assert_has_awaits([mock.call(seconds)] * 2)
    assert len(transport.requests) == 3
    for request in transport.requests:
        assert request.method == "GET"
        assert request.url.path == f"/v1/videos/{VIDEO_ID}"
        assert request.headers["X-Stainless-Poll-Helper"] == "true"
        assert request.headers.get("X-Stainless-Custom-Poll-Interval") == (
            str(interval) if isinstance(interval, int) else None
        )


def multipart_fields(request: httpx2.Request) -> dict[str, str]:
    message = BytesParser(policy=policy.default).parsebytes(
        f"Content-Type: {request.headers['content-type']}\r\n\r\n".encode() + request.content
    )
    fields: dict[str, str] = {}
    for part in message.iter_parts():
        name = part.get_param("name", header="content-disposition")
        value = part.get_payload(decode=True)
        assert isinstance(name, str) and isinstance(value, bytes)
        fields[name] = value.decode()
    return fields


async def test_create_options_are_forwarded_to_creation_and_poll_uses_created_id(
    sdk_client: OpenAI | AsyncOpenAI, transport: Transport
) -> None:
    transport.responses.extend([video_response("queued"), video_response("completed")])
    with mock.patch.object(sdk_client.videos, "_sleep") as sleep:
        result = await create_and_poll(
            sdk_client,
            prompt="Synthetic video",
            input_reference=("reference.png", b"synthetic-reference", "image/png"),
            model="sora-2",
            seconds="4",
            size="720x1280",
            poll_interval_ms=25,
            extra_headers={"X-Create-Only": "creation"},
            extra_query={"create_query": "creation"},
            extra_body={"extension_field": "creation"},
            timeout=3.25,
        )
    assert result.id == VIDEO_ID
    assert result.status == "completed"
    sleep.assert_not_called()
    assert len(transport.requests) == 2
    create, retrieve = transport.requests
    assert create.method == "POST" and create.url.path == "/v1/videos"
    assert multipart_fields(create) == {
        "prompt": "Synthetic video",
        "input_reference": "synthetic-reference",
        "model": "sora-2",
        "seconds": "4",
        "size": "720x1280",
        "extension_field": "creation",
    }
    assert dict(create.url.params) == {"client_query": "inherited", "create_query": "creation"}
    assert create.headers["X-Create-Only"] == "creation"
    assert create.extensions["timeout"] == {"connect": 3.25, "read": 3.25, "write": 3.25, "pool": 3.25}
    assert retrieve.method == "GET" and retrieve.url.path == f"/v1/videos/{VIDEO_ID}"
    assert dict(retrieve.url.params) == {"client_query": "inherited"}
    assert "X-Create-Only" not in retrieve.headers
    assert retrieve.headers["X-Stainless-Custom-Poll-Interval"] == "25"
    assert retrieve.extensions["timeout"] == {"connect": 11.0, "read": 11.0, "write": 11.0, "pool": 11.0}
    assert all(request.headers["X-Client-Option"] == "client" for request in transport.requests)


async def test_poll_propagates_retrieval_error(sdk_client: OpenAI | AsyncOpenAI, transport: Transport) -> None:
    transport.responses.append(httpx2.Response(404, json={"error": {"message": "Synthetic missing video"}}))
    with mock.patch.object(sdk_client.videos, "_sleep") as sleep:
        with pytest.raises(NotFoundError):
            await poll(sdk_client)
    assert len(transport.requests) == 1
    sleep.assert_not_called()


async def test_create_failure_prevents_polling(sdk_client: OpenAI | AsyncOpenAI, transport: Transport) -> None:
    transport.responses.append(httpx2.Response(400, json={"error": {"message": "Synthetic creation failure"}}))
    with pytest.raises(BadRequestError):
        await create_and_poll(sdk_client, prompt="Synthetic video")
    assert len(transport.requests) == 1
    assert transport.requests[0].method == "POST"


@pytest.mark.parametrize("sdk_client", [True], indirect=True, ids=["async"])
async def test_poll_propagates_async_cancellation(sdk_client: AsyncOpenAI, transport: Transport) -> None:
    transport.responses.append(video_response("queued"))
    cancellation = asyncio.CancelledError()
    with mock.patch.object(sdk_client.videos, "_sleep", side_effect=cancellation):
        with pytest.raises(asyncio.CancelledError) as caught:
            await poll(sdk_client)
    assert caught.value is cancellation
    assert len(transport.requests) == 1
