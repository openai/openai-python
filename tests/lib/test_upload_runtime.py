from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock, call

import httpx2
import pytest

from openai import AsyncOpenAI
from openai.lib._uploads import upload_file_chunked, async_upload_file_chunked
from openai.types.upload import Upload
from openai.resources.uploads import uploads as uploads_module

from . import test_uploads as upload_contracts
from .test_uploads import (
    upload,
    asynchronous as asynchronous,
    upload_client,
    upload_response,
)

# Pytest collects these aliases and preserves the original parameterization.
# They rerun the released contracts under this module's implementation fixture.
test_chunk_order_metadata_and_client_options = upload_contracts.test_chunk_order_metadata_and_client_options
test_memory_upload_requires_metadata_before_requests = (
    upload_contracts.test_memory_upload_requires_metadata_before_requests
)
test_path_handle_closes_and_failure_skips_completion = (
    upload_contracts.test_path_handle_closes_and_failure_skips_completion
)


@pytest.fixture(autouse=True, params=["released", "extracted"])
def implementation(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    # Run the released public-entrypoint contracts against both implementations.
    # Production resources keep their existing methods until compiler regeneration.
    if request.param == "extracted":
        monkeypatch.setattr(uploads_module.Uploads, "upload_file_chunked", upload_file_chunked)
        monkeypatch.setattr(uploads_module.AsyncUploads, "upload_file_chunked", async_upload_file_chunked)


def unexpected_request(request: httpx2.Request) -> httpx2.Response:
    raise AssertionError(f"overridden resource methods must handle {request.method} {request.url.path}")


@pytest.mark.parametrize("change_default", [False, True], ids=["64MiB-boundary", "lazy-default-and-logger"])
async def test_subclass_overrides_default_boundary_and_logger(
    asynchronous: bool, change_default: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A real payload crosses the released 64 MiB boundary without multipart copies.
    # The small case changes module bindings during dispatch, preserving their timing.
    boundary = 64 * 1024 * 1024
    payload = b"abcdefgh" if change_default else b"x" * boundary + b"z"
    operations: list[str] = []
    sizes: list[int] = []
    endings: list[bytes] = []
    first_logger, second_logger = Mock(), Mock()
    monkeypatch.setattr(uploads_module, "log", first_logger)
    if change_default:
        monkeypatch.setattr(uploads_module, "DEFAULT_PART_SIZE", 7)

    def create(resource: Any, **kwargs: Any) -> Upload:
        assert resource is target
        assert kwargs == {
            "bytes": len(payload),
            "filename": "synthetic.bin",
            "mime_type": "application/octet-stream",
            "purpose": "assistants",
        }
        operations.append("create")
        if change_default:
            monkeypatch.setattr(uploads_module, "DEFAULT_PART_SIZE", 3)
        return Upload(**upload_response().json())

    def create_part(*, upload_id: str, data: bytes) -> SimpleNamespace:
        assert upload_id == "upload-synthetic"
        operations.append("part")
        sizes.append(len(data))
        endings.append(data[-1:])
        if change_default:
            # The selected part size stays fixed, but the module logger remains live.
            monkeypatch.setattr(uploads_module, "DEFAULT_PART_SIZE", 1)
            monkeypatch.setattr(uploads_module, "log", second_logger)
        return SimpleNamespace(id=f"part-{len(sizes)}")

    def complete(resource: Any, **kwargs: Any) -> Upload:
        assert resource is target
        assert kwargs == {
            "upload_id": "upload-synthetic",
            "part_ids": [f"part-{index + 1}" for index in range(len(sizes))],
            "md5": uploads_module.omit,
        }
        operations.append("complete")
        return Upload(**upload_response(completed=True).json())

    async def async_create(resource: Any, **kwargs: Any) -> Upload:
        return create(resource, **kwargs)

    async def async_create_part(*, upload_id: str, data: bytes) -> SimpleNamespace:
        return create_part(upload_id=upload_id, data=data)

    async def async_complete(resource: Any, **kwargs: Any) -> Upload:
        return complete(resource, **kwargs)

    async with upload_client(asynchronous, unexpected_request) as client:
        base = uploads_module.AsyncUploads if isinstance(client, AsyncOpenAI) else uploads_module.Uploads
        # Dynamic subclassing exercises the actual extension boundary without changing
        # the generated create/complete endpoint signatures just for test doubles.
        subclass = type(
            "OverriddenUploads",
            (base,),
            {
                "create": async_create if asynchronous else create,
                "complete": async_complete if asynchronous else complete,
            },
        )
        target = subclass(client)
        target.parts = SimpleNamespace(create=async_create_part if asynchronous else create_part)
        monkeypatch.setattr(client, "uploads", target)
        result = await upload(
            client,
            file=payload,
            filename="synthetic.bin",
            bytes=len(payload),
            mime_type="application/octet-stream",
            purpose="assistants",
        )

    assert result.status == "completed"
    assert sizes == ([3, 3, 2] if change_default else [boundary, 1])
    assert endings == ([b"c", b"f", b"h"] if change_default else [b"x", b"z"])
    assert operations == ["create", *["part" for _ in sizes], "complete"]
    logger = second_logger if change_default else first_logger
    assert logger.info.call_args_list == [
        call("Uploaded part %s for upload %s", f"part-{index + 1}", "upload-synthetic") for index in range(len(sizes))
    ]
    if change_default:
        first_logger.info.assert_not_called()
