from __future__ import annotations

import io
from typing import Callable, Iterator, AsyncIterator, cast
from unittest import mock
from typing_extensions import override

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI, APIStatusError, APITimeoutError, APIConnectionError
from openai._types import BinaryTypes, RequestFiles, AsyncBinaryTypes


@pytest.fixture(autouse=True)
def immediate_retries() -> Iterator[None]:
    with mock.patch("openai._base_client.BaseClient._calculate_retry_timeout", return_value=0):
        yield


async def post_body(
    sync: bool,
    handler: Callable[[httpx2.Request], httpx2.Response],
    *,
    content: BinaryTypes | AsyncBinaryTypes | None = None,
    files: RequestFiles | None = None,
) -> httpx2.Response:
    transport = httpx2.MockTransport(handler)
    if sync:
        with OpenAI(
            api_key="test-key",
            base_url="https://example.test/v1",
            max_retries=2,
            http_client=httpx2.Client(transport=transport, trust_env=False),
        ) as client:
            return client.post("/upload", content=cast(BinaryTypes, content), files=files, cast_to=httpx2.Response)
    async with AsyncOpenAI(
        api_key="test-key",
        base_url="https://example.test/v1",
        max_retries=2,
        http_client=httpx2.AsyncClient(transport=transport, trust_env=False),
    ) as client:
        return await client.post(
            "/upload", content=cast(AsyncBinaryTypes, content), files=files, cast_to=httpx2.Response
        )


class TrackedFile(io.BytesIO):
    def __init__(self, content: bytes) -> None:
        super().__init__(content)
        self.seeks: list[tuple[int, int]] = []

    @override
    def seek(self, offset: int, whence: int = 0) -> int:
        self.seeks.append((offset, whence))
        return super().seek(offset, whence)


class NonSeekableFile(io.BytesIO):
    @override
    def seekable(self) -> bool:
        return False

    @override
    def seek(self, offset: int, whence: int = 0) -> int:
        raise io.UnsupportedOperation("seek")

    @override
    def tell(self) -> int:
        raise io.UnsupportedOperation("tell")


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_ineligible_later_multipart_file_does_not_rewind_earlier_file(sync: bool) -> None:
    first = TrackedFile(b"first file")
    later = NonSeekableFile(b"later file")
    request_bodies: list[bytes] = []
    seeks_after_send: list[tuple[int, int]] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        request_bodies.append(request.content)
        # HTTPX2 itself seeks while measuring and rendering the first file.
        # Only additional seeks after that completed send would be retry work.
        seeks_after_send[:] = first.seeks
        return httpx2.Response(500, json={"error": {"message": "original failure"}})

    with pytest.raises(APIStatusError):
        await post_body(
            sync,
            handler,
            files=[("first", ("first.txt", first)), ("later", ("later.txt", later))],
        )

    assert len(request_bodies) == 1
    assert b"first file" in request_bodies[0] and b"later file" in request_bodies[0]
    assert first.seeks == seeks_after_send
    assert first.tell() == len(b"first file")


class SeekableBody:
    def __init__(self, content: bytes) -> None:
        self.buffer = io.BytesIO(content)
        self.fail_rewind = False
        self.seeks: list[tuple[int, int]] = []

    def read(self, size: int = -1) -> bytes:
        return self.buffer.read(size)

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.buffer.tell()

    def seek(self, position: int, whence: int = 0) -> int:
        self.seeks.append((position, whence))
        if self.fail_rewind:
            raise OSError("rewind failed")
        return self.buffer.seek(position, whence)


class SyncSeekableBody(SeekableBody):
    def __iter__(self) -> Iterator[bytes]:
        while chunk := self.read(8192):
            yield chunk


class AsyncSeekableBody(SeekableBody):
    async def __aiter__(self) -> AsyncIterator[bytes]:
        while chunk := self.read(8192):
            yield chunk


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("failure", ["status", "timeout", "connection"])
async def test_failed_rewind_preserves_original_request_failure(sync: bool, failure: str) -> None:
    body = SyncSeekableBody(b"payload") if sync else AsyncSeekableBody(b"payload")
    originals: list[httpx2.Response | httpx2.RequestError] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        assert request.content == b"payload"
        body.seeks.clear()  # Exclude HTTPX2's content-length probe on the first send.
        body.fail_rewind = True
        if failure == "status":
            response = httpx2.Response(500, json={"error": {"message": "original failure"}})
            originals.append(response)
            return response
        error = (
            httpx2.ReadTimeout("original timeout", request=request)
            if failure == "timeout"
            else httpx2.ConnectError("original connection failure", request=request)
        )
        originals.append(error)
        raise error

    expected_error = {"status": APIStatusError, "timeout": APITimeoutError, "connection": APIConnectionError}[failure]
    with pytest.raises(expected_error) as exc_info:
        await post_body(sync, handler, content=body)

    assert len(originals) == 1
    assert body.seeks == [(0, 0)]
    if failure == "status":
        assert isinstance(exc_info.value, APIStatusError)
        assert exc_info.value.response is originals[0]
        assert exc_info.value.body == {"message": "original failure"}
    else:
        assert exc_info.value.__cause__ is originals[0]


@pytest.mark.parametrize(
    "sync,kind",
    [(True, "bytes"), (False, "bytes"), (True, "list"), (True, "tuple"), (True, "seekable"), (False, "seekable")],
)
async def test_replayable_raw_body_survives_multiple_retries(sync: bool, kind: str) -> None:
    payload = b"expected payload"
    body: BinaryTypes | AsyncBinaryTypes
    seekable: SyncSeekableBody | AsyncSeekableBody | None = None
    if kind == "seekable":
        seekable = SyncSeekableBody(b"prefix" + payload) if sync else AsyncSeekableBody(b"prefix" + payload)
        seekable.seek(len(b"prefix"))
        seekable.seeks.clear()
        body = seekable
    elif kind == "list":
        body = [b"expected ", b"payload"]
    elif kind == "tuple":
        body = (b"expected ", b"payload")
    else:
        body = payload
    request_bodies: list[bytes] = []
    retry_counts: list[str] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        request_bodies.append(request.content)
        retry_counts.append(request.headers["x-stainless-retry-count"])
        return httpx2.Response(200 if len(request_bodies) == 3 else 500)

    response = await post_body(sync, handler, content=body)

    assert response.status_code == 200
    assert request_bodies == [payload] * 3
    assert retry_counts == ["0", "1", "2"]


class RepeatableBody:
    def __iter__(self) -> Iterator[bytes]:
        yield b"repeatable"


class AsyncRepeatableBody:
    async def __aiter__(self) -> AsyncIterator[bytes]:
        yield b"repeatable"


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
async def test_opaque_repeatable_iterable_is_conservatively_not_retried(sync: bool) -> None:
    body = RepeatableBody() if sync else AsyncRepeatableBody()
    request_bodies: list[bytes] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        request_bodies.append(request.content)
        return httpx2.Response(500)

    with pytest.raises(APIStatusError):
        await post_body(sync, handler, content=body)

    assert request_bodies == [b"repeatable"]
    # This object really is reusable. The SDK deliberately cannot infer that
    # guarantee from the general iterable protocol and declines an automatic retry.
    if isinstance(body, RepeatableBody):
        assert list(body) == [b"repeatable"]
    else:
        assert [chunk async for chunk in body] == [b"repeatable"]
