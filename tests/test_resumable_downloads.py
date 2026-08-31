from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

import httpx2
import pytest
from httpx2._types import SyncByteStream, AsyncByteStream

import openai

base_url = "http://localhost:7123/v1"
api_key = "test-api-key"

DATA = b"".join(bytes([i % 256]) * 64 for i in range(160))  # 10240 bytes
CUT = 4096


class CutOffStream(SyncByteStream):
    """Simulates a connection that dies part-way through the response body."""

    def __init__(self, data: bytes, cut_at: int | None) -> None:
        self.data = data
        self.cut_at = cut_at

    def __iter__(self) -> Iterator[bytes]:
        if self.cut_at is None:
            yield self.data
            return
        yield self.data[: self.cut_at]
        raise httpx2.RemoteProtocolError("peer closed connection without sending complete message body")


class AsyncCutOffStream(AsyncByteStream):
    def __init__(self, data: bytes, cut_at: int | None) -> None:
        self.data = data
        self.cut_at = cut_at

    async def __aiter__(self) -> AsyncIterator[bytes]:
        if self.cut_at is None:
            yield self.data
            return
        yield self.data[: self.cut_at]
        raise httpx2.RemoteProtocolError("peer closed connection without sending complete message body")


def _stream_cls(is_async: bool) -> type[CutOffStream] | type[AsyncCutOffStream]:
    return AsyncCutOffStream if is_async else CutOffStream


class RangeServer:
    """Stateful handler that serves `DATA`, cutting the first transfer short.

    Mirrors the failure mode from https://github.com/openai/openai-python/issues/2959:
    the first response dies mid-body; the server supports byte ranges so a later
    attempt can request only the missing bytes.
    """

    def __init__(
        self,
        *,
        accept_ranges: bool = True,
        honor_range: bool = True,
        cut_first_attempt_at: int | None = CUT,
    ) -> None:
        self.accept_ranges = accept_ranges
        self.honor_range = honor_range
        self.cut_first_attempt_at = cut_first_attempt_at
        self.requests: list[httpx2.Request] = []

    def _handle(self, request: httpx2.Request, *, is_async: bool) -> httpx2.Response:
        self.requests.append(request)
        first_attempt = len(self.requests) == 1
        headers = {"content-type": "application/binary"}
        if self.accept_ranges:
            headers["accept-ranges"] = "bytes"

        range_header = request.headers.get("range")
        if not first_attempt and range_header and self.honor_range:
            start = int(range_header.removeprefix("bytes=").split("-")[0])
            headers["content-range"] = f"bytes {start}-{len(DATA) - 1}/{len(DATA)}"
            return httpx2.Response(
                206,
                headers=headers,
                request=request,
                stream=_stream_cls(is_async)(DATA[start:], None),
            )

        # first attempt (or a range-ignoring server): full body, possibly cut short
        cut_at = self.cut_first_attempt_at if first_attempt else None
        return httpx2.Response(
            200,
            headers=headers,
            request=request,
            stream=_stream_cls(is_async)(DATA, cut_at),
        )

    def handle(self, request: httpx2.Request) -> httpx2.Response:
        return self._handle(request, is_async=False)

    async def handle_async(self, request: httpx2.Request) -> httpx2.Response:
        return self._handle(request, is_async=True)


class AlwaysCutsServer(RangeServer):
    """Every attempt is cut off at the same byte, so retries can never finish."""

    def _handle(self, request: httpx2.Request, *, is_async: bool) -> httpx2.Response:
        self.requests.append(request)
        return httpx2.Response(
            200,
            headers={
                "content-type": "application/binary",
                "accept-ranges": "bytes",
            },
            request=request,
            stream=_stream_cls(is_async)(DATA, CUT),
        )


class CutAtVeryEndServer(RangeServer):
    """Delivers every byte, then the connection dies before the terminator.

    The next attempt's `Range` is unsatisfiable (`416`), but the `Content-Range`
    total proves the download is already complete.
    """

    def _handle(self, request: httpx2.Request, *, is_async: bool) -> httpx2.Response:
        self.requests.append(request)
        if len(self.requests) == 1:
            return httpx2.Response(
                200,
                headers={
                    "content-type": "application/binary",
                    "accept-ranges": "bytes",
                },
                request=request,
                stream=_stream_cls(is_async)(DATA, len(DATA)),
            )
        assert request.headers.get("range") == f"bytes={len(DATA)}-"
        return httpx2.Response(
            416,
            headers={"content-range": f"bytes */{len(DATA)}"},
            request=request,
            content=b"",
        )


def _sync_client(server: RangeServer) -> openai.OpenAI:
    return openai.OpenAI(
        base_url=base_url,
        api_key=api_key,
        max_retries=2,
        http_client=httpx2.Client(transport=httpx2.MockTransport(server.handle)),
    )


def _async_client(server: RangeServer) -> openai.AsyncOpenAI:
    return openai.AsyncOpenAI(
        base_url=base_url,
        api_key=api_key,
        max_retries=2,
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(server.handle_async)),
    )


@pytest.fixture(autouse=True)
def fast_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "openai._base_client.BaseClient._calculate_retry_timeout",
        lambda *_args, **_kwargs: 0.01,
    )


class TestResumableDownloads:
    def test_resumes_interrupted_download_sync(self) -> None:
        server = RangeServer()
        with _sync_client(server) as client:
            content = client.files.content("file_abc").content

        assert content == DATA
        assert len(server.requests) == 2
        assert server.requests[1].headers.get("range") == f"bytes={CUT}-"

    @pytest.mark.asyncio
    async def test_resumes_interrupted_download_async(self) -> None:
        server = RangeServer()
        async with _async_client(server) as client:
            content = (await client.files.content("file_abc")).content

        assert content == DATA
        assert len(server.requests) == 2
        assert server.requests[1].headers.get("range") == f"bytes={CUT}-"

    def test_restarts_from_scratch_when_server_has_no_ranges(self) -> None:
        server = RangeServer(accept_ranges=False)
        with _sync_client(server) as client:
            content = client.files.content("file_abc").content

        assert content == DATA
        assert len(server.requests) == 2
        # without `accept-ranges` we can't resume, so no `Range` is sent
        assert server.requests[1].headers.get("range") is None

    def test_recovers_when_range_is_ignored(self) -> None:
        server = RangeServer(honor_range=False)
        with _sync_client(server) as client:
            content = client.files.content("file_abc").content

        assert content == DATA
        assert len(server.requests) == 2

    def test_completes_download_that_was_cut_at_the_very_end(self) -> None:
        server = CutAtVeryEndServer()
        with _sync_client(server) as client:
            content = client.files.content("file_abc").content

        assert content == DATA
        assert len(server.requests) == 2

    def test_raises_when_retries_are_exhausted(self) -> None:
        server = AlwaysCutsServer()
        with _sync_client(server) as client:
            with pytest.raises(openai.APIConnectionError):
                client.files.content("file_abc")

        # max_retries=2 -> three attempts, each resuming where the last one died
        assert len(server.requests) == 3
        assert [r.headers.get("range") for r in server.requests] == [
            None,
            f"bytes={CUT}-",
            f"bytes={CUT}-",
        ]

    def test_plain_get_is_unaffected(self) -> None:
        # a JSON endpoint that never advertises ranges keeps today's behaviour
        def handler(request: httpx2.Request) -> httpx2.Response:
            assert request.headers.get("range") is None
            return httpx2.Response(200, json={"data": [], "object": "list"})

        with openai.OpenAI(
            base_url=base_url,
            api_key=api_key,
            http_client=httpx2.Client(transport=httpx2.MockTransport(handler)),
        ) as client:
            page = client.models.list()

        assert page.data == []
