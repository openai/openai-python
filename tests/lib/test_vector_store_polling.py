from __future__ import annotations

import pytest

from openai import PollingTimeoutError
from openai._models import construct_type_unchecked
from openai.resources.vector_stores.files import Files, AsyncFiles
from openai.resources.vector_stores.file_batches import FileBatches, AsyncFileBatches
from openai.types.vector_stores.vector_store_file import VectorStoreFile
from openai.types.vector_stores.vector_store_file_batch import VectorStoreFileBatch


class _RawResponse:
    headers: dict[str, str] = {}

    def __init__(self, value: object) -> None:
        self._value = value

    def parse(self) -> object:
        return self._value


class _RawResponses:
    def __init__(self, value: object) -> None:
        self._value = value

    def retrieve(self, *_args: object, **_kwargs: object) -> _RawResponse:
        return _RawResponse(self._value)


class _AsyncRawResponses:
    def __init__(self, value: object) -> None:
        self._value = value

    async def retrieve(self, *_args: object, **_kwargs: object) -> _RawResponse:
        return _RawResponse(self._value)


def _in_progress_file() -> VectorStoreFile:
    return construct_type_unchecked(
        type_=VectorStoreFile,
        value={
            "id": "file_123",
            "created_at": 1,
            "last_error": None,
            "object": "vector_store.file",
            "status": "in_progress",
            "usage_bytes": 0,
            "vector_store_id": "vs_123",
        },
    )


def _in_progress_batch() -> VectorStoreFileBatch:
    return construct_type_unchecked(
        type_=VectorStoreFileBatch,
        value={
            "id": "batch_123",
            "created_at": 1,
            "file_counts": {"cancelled": 0, "completed": 0, "failed": 0, "in_progress": 1, "total": 1},
            "object": "vector_store.files_batch",
            "status": "in_progress",
            "vector_store_id": "vs_123",
        },
    )


def test_vector_store_file_poll_times_out() -> None:
    files = object.__new__(Files)
    files.with_raw_response = _RawResponses(_in_progress_file())

    with pytest.raises(PollingTimeoutError, match="file file_123 is still in_progress"):
        files.poll("file_123", vector_store_id="vs_123", max_wait_seconds=0)


async def test_async_vector_store_file_poll_times_out() -> None:
    files = object.__new__(AsyncFiles)
    files.with_raw_response = _AsyncRawResponses(_in_progress_file())

    with pytest.raises(PollingTimeoutError, match="file file_123 is still in_progress"):
        await files.poll("file_123", vector_store_id="vs_123", max_wait_seconds=0)


def test_vector_store_file_batch_poll_times_out() -> None:
    batches = object.__new__(FileBatches)
    batches.with_raw_response = _RawResponses(_in_progress_batch())

    with pytest.raises(PollingTimeoutError, match="file batch batch_123 is still in_progress"):
        batches.poll("batch_123", vector_store_id="vs_123", max_wait_seconds=0)


async def test_async_vector_store_file_batch_poll_times_out() -> None:
    batches = object.__new__(AsyncFileBatches)
    batches.with_raw_response = _AsyncRawResponses(_in_progress_batch())

    with pytest.raises(PollingTimeoutError, match="file batch batch_123 is still in_progress"):
        await batches.poll("batch_123", vector_store_id="vs_123", max_wait_seconds=0)
