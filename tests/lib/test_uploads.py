from __future__ import annotations

import io
import json
from email import policy
from typing import Any, Literal, Callable, AsyncGenerator, cast
from pathlib import Path
from contextlib import asynccontextmanager
from email.parser import BytesParser
from email.message import EmailMessage

import anyio
import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI, InternalServerError
from openai.types.upload import Upload


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def asynchronous(request: pytest.FixtureRequest) -> bool:
    return cast(bool, request.param)


@asynccontextmanager
async def upload_client(
    asynchronous: bool, handler: Callable[[httpx2.Request], httpx2.Response]
) -> AsyncGenerator[OpenAI | AsyncOpenAI, None]:
    options: dict[str, Any] = {
        "api_key": "synthetic-test-key",
        "base_url": "https://example.test/v1",
        "max_retries": 0,
        "default_headers": {"x-test-option": "retained"},
        "default_query": {"test-option": "retained"},
    }
    if asynchronous:
        async with AsyncOpenAI(
            **options, http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
        ) as async_client:
            yield async_client
    else:
        with OpenAI(**options, http_client=httpx2.Client(transport=httpx2.MockTransport(handler))) as client:
            yield client


async def upload(client: OpenAI | AsyncOpenAI, **kwargs: Any) -> Upload:
    if isinstance(client, AsyncOpenAI):
        return await client.uploads.upload_file_chunked(**kwargs)
    return client.uploads.upload_file_chunked(**kwargs)


def upload_response(*, completed: bool = False) -> httpx2.Response:
    return httpx2.Response(
        200,
        json={
            "id": "upload-synthetic",
            "object": "upload",
            "bytes": 8,
            "created_at": 0,
            "expires_at": 3600,
            "filename": "example.bin",
            "purpose": "assistants",
            "status": "completed" if completed else "pending",
        },
    )


def part_data(request: httpx2.Request) -> bytes:
    message = BytesParser(_class=EmailMessage, policy=policy.default).parsebytes(
        ("Content-Type: " + request.headers["content-type"] + "\r\n\r\n").encode() + request.read()
    )
    parts = list(message.iter_parts())
    assert len(parts) == 1
    assert parts[0].get_param("name", header="content-disposition") == "data"
    return cast(bytes, parts[0].get_payload(decode=True))


@pytest.mark.parametrize("source", ["bytes", "path", "path-overrides", "empty"])
async def test_chunk_order_metadata_and_client_options(asynchronous: bool, source: str, tmp_path: Path) -> None:
    payload = b"abcdefgh" if source != "empty" else b""
    kwargs: dict[str, Any] = {"file": payload, "filename": "example.bin", "bytes": len(payload)}
    filename = "example.bin"
    declared_bytes = len(payload)
    if source.startswith("path"):
        path = tmp_path / "source.bin"
        path.write_bytes(payload)
        kwargs = {"file": path}
        filename = path.name
        if source == "path-overrides":
            # Explicit metadata remains authoritative even when it differs from the local file.
            kwargs.update(filename="override.bin", bytes=123)
            filename, declared_bytes = "override.bin", 123

    chunks: list[bytes] = []
    operations: list[str] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        assert request.method == "POST"
        assert request.headers["x-test-option"] == "retained"
        assert request.url.params["test-option"] == "retained"
        path = request.url.path
        if path == "/v1/uploads":
            assert operations == []
            assert json.loads(request.read()) == {
                "bytes": declared_bytes,
                "filename": filename,
                "mime_type": "application/octet-stream",
                "purpose": "assistants",
            }
            operations.append("create")
            return upload_response()
        if path == "/v1/uploads/upload-synthetic/parts":
            chunks.append(part_data(request))
            operations.append("part")
            return httpx2.Response(
                200,
                json={
                    "id": f"part-{len(chunks)}",
                    "object": "upload.part",
                    "created_at": 0,
                    "upload_id": "upload-synthetic",
                },
            )
        assert path == "/v1/uploads/upload-synthetic/complete"
        assert json.loads(request.read()) == {
            "part_ids": [f"part-{index + 1}" for index in range(len(chunks))],
            "md5": "synthetic-md5",
        }
        operations.append("complete")
        return upload_response(completed=True)

    async with upload_client(asynchronous, handler) as client:
        result = await upload(
            client,
            **kwargs,
            mime_type="application/octet-stream",
            purpose="assistants",
            part_size=3,
            md5="synthetic-md5",
        )
    assert isinstance(result, Upload)
    assert result.id == "upload-synthetic"
    assert result.status == "completed"
    expected = [payload[index : index + 3] for index in range(0, len(payload), 3)]
    assert chunks == expected
    assert operations == ["create", *["part" for _ in expected], "complete"]


@pytest.mark.parametrize("missing", ["filename", "bytes"])
async def test_memory_upload_requires_metadata_before_requests(asynchronous: bool, missing: str) -> None:
    calls: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        calls.append(request)
        raise AssertionError("invalid metadata must fail before making a request")

    kwargs: dict[str, Any] = {"file": b"synthetic", "filename": "example.bin", "bytes": 9}
    del kwargs[missing]
    async with upload_client(asynchronous, handler) as client:
        with pytest.raises(TypeError, match=f"The `{missing}` argument must be given for in-memory files"):
            await upload(client, **kwargs, mime_type="application/octet-stream", purpose="assistants")
    assert calls == []


@pytest.mark.parametrize("fail_part", [False, True], ids=["success", "part-failure"])
async def test_path_handle_closes_and_failure_skips_completion(
    asynchronous: bool, fail_part: bool, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "example.bin"
    path.write_bytes(b"synthetic")
    handles: list[Any] = []
    if asynchronous:
        original_open = anyio.Path.open

        async def track_async_open(self: anyio.Path, mode: Literal["rb"]) -> anyio.AsyncFile[bytes]:
            handle = await original_open(self, mode)
            handles.append(handle)
            return handle

        monkeypatch.setattr(anyio.Path, "open", track_async_open)
    else:
        original_file = io.FileIO

        def track_open(*args: Any, **kwargs: Any) -> io.FileIO:
            handle = original_file(*args, **kwargs)
            handles.append(handle)
            return handle

        monkeypatch.setattr(io, "FileIO", track_open)

    operations: list[str] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        operations.append(request.url.path)
        if request.url.path == "/v1/uploads":
            return upload_response()
        if request.url.path.endswith("/parts"):
            assert len(handles) == 1 and not handles[0].closed
            if fail_part:
                return httpx2.Response(500, json={"error": {"message": "synthetic part failure"}})
            return httpx2.Response(
                200, json={"id": "part-1", "object": "upload.part", "created_at": 0, "upload_id": "upload-synthetic"}
            )
        assert request.url.path.endswith("/complete")
        assert handles[0].closed
        assert json.loads(request.read()) == {"part_ids": ["part-1"]}
        return upload_response(completed=True)

    async with upload_client(asynchronous, handler) as client:
        if fail_part:
            with pytest.raises(InternalServerError, match="synthetic part failure"):
                await upload(client, file=path, mime_type="application/octet-stream", purpose="assistants")
        else:
            await upload(client, file=path, mime_type="application/octet-stream", purpose="assistants")
    assert len(handles) == 1 and handles[0].closed
    assert operations == ["/v1/uploads", "/v1/uploads/upload-synthetic/parts"] + (
        [] if fail_part else ["/v1/uploads/upload-synthetic/complete"]
    )
