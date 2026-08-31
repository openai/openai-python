from __future__ import annotations

import gzip
from collections.abc import Iterator, AsyncIterator

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
        etag: str | None = None,
        misalign_content_range: bool = False,
    ) -> None:
        self.accept_ranges = accept_ranges
        self.honor_range = honor_range
        self.cut_first_attempt_at = cut_first_attempt_at
        self.etag = etag
        self.misalign_content_range = misalign_content_range
        self.requests: list[httpx2.Request] = []

    def _handle(self, request: httpx2.Request, *, is_async: bool) -> httpx2.Response:
        self.requests.append(request)
        first_attempt = len(self.requests) == 1
        headers = {"content-type": "application/binary"}
        if self.accept_ranges:
            headers["accept-ranges"] = "bytes"
        if self.etag:
            headers["etag"] = self.etag

        range_header = request.headers.get("range")
        if not first_attempt and range_header and self.honor_range:
            start = int(range_header.removeprefix("bytes=").split("-")[0])
            if self.misalign_content_range:
                # claims a range that does not match what we asked for
                headers["content-range"] = f"bytes 0-{len(DATA) - 1}/{len(DATA)}"
                start = 0
            else:
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
                    "content-disposition": 'attachment; filename="result.jsonl"',
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


class GzipServer:
    """Serves a gzip-encoded body — byte ranges don't apply to decoded bytes."""

    def __init__(self) -> None:
        self.encoded = gzip.compress(DATA)
        self.requests: list[httpx2.Request] = []

    def _handle(self, request: httpx2.Request, *, is_async: bool) -> httpx2.Response:
        self.requests.append(request)
        cut_at = len(self.encoded) // 2 if len(self.requests) == 1 else None
        return httpx2.Response(
            200,
            headers={
                "content-type": "application/binary",
                "accept-ranges": "bytes",
                "content-encoding": "gzip",
            },
            request=request,
            stream=_stream_cls(is_async)(self.encoded, cut_at),
        )

    def handle(self, request: httpx2.Request) -> httpx2.Response:
        return self._handle(request, is_async=False)

    async def handle_async(self, request: httpx2.Request) -> httpx2.Response:
        return self._handle(request, is_async=True)


def _sync_client(server: RangeServer | GzipServer) -> openai.OpenAI:
    return openai.OpenAI(
        base_url=base_url,
        api_key=api_key,
        max_retries=2,
        http_client=httpx2.Client(transport=httpx2.MockTransport(server.handle)),
    )


def _async_client(server: RangeServer | GzipServer) -> openai.AsyncOpenAI:
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

    def test_416_completion_preserves_original_response_headers(self) -> None:
        server = CutAtVeryEndServer()
        with _sync_client(server) as client:
            response = client.with_raw_response.files.content("file_abc")

        assert response.content == DATA
        assert response.headers.get("content-type") == "application/binary"
        assert response.headers.get("content-disposition") == 'attachment; filename="result.jsonl"'
        assert "content-range" not in response.headers

    def test_resume_sends_if_range_with_strong_etag(self) -> None:
        server = RangeServer(etag='"version-1"')
        with _sync_client(server) as client:
            content = client.files.content("file_abc").content

        assert content == DATA
        assert server.requests[1].headers.get("if-range") == '"version-1"'

    def test_weak_etag_is_not_used_as_validator(self) -> None:
        server = RangeServer(etag='W/"version-1"')
        with _sync_client(server) as client:
            content = client.files.content("file_abc").content

        assert content == DATA
        assert server.requests[1].headers.get("if-range") is None

    def test_restarts_when_content_range_does_not_match_offset(self) -> None:
        server = RangeServer(misalign_content_range=True)
        with _sync_client(server) as client:
            content = client.files.content("file_abc").content

        assert content == DATA
        # attempt 2 returned a 206 that starts at the wrong offset, so the
        # partial state was dropped and attempt 3 downloaded from scratch
        assert len(server.requests) == 3
        assert server.requests[1].headers.get("range") == f"bytes={CUT}-"
        assert server.requests[2].headers.get("range") is None

    def test_encoded_bodies_are_not_resumed(self) -> None:
        server = GzipServer()
        with _sync_client(server) as client:
            content = client.files.content("file_abc").content

        assert content == DATA
        assert len(server.requests) == 2
        # byte ranges address the encoded representation, so a gzip body is
        # never resumed — the retry restarts from the first byte
        assert server.requests[1].headers.get("range") is None

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
