from __future__ import annotations

import math
import time
from typing import TYPE_CHECKING, Mapping
from typing_extensions import assert_never

from .._types import Omit, omit
from .._utils import is_given
from ..types.vector_stores.vector_store_file import VectorStoreFile
from ..types.vector_stores.vector_store_file_batch import VectorStoreFileBatch

if TYPE_CHECKING:
    from ..resources.vector_stores.files import Files, AsyncFiles
    from ..resources.vector_stores.file_batches import FileBatches, AsyncFileBatches


def _get_poll_interval_ms(headers: Mapping[str, str]) -> int:
    """Use the server hint or the existing one-second default."""
    from_header = headers.get("openai-poll-after-ms")
    if from_header is not None:
        return int(from_header)
    return 1000


def validate_max_wait_seconds(max_wait_seconds: float | Omit) -> None:
    if is_given(max_wait_seconds) and (not math.isfinite(max_wait_seconds) or max_wait_seconds < 0):
        raise ValueError("Expected a finite, non-negative value for `max_wait_seconds`")


def _remaining_poll_time(deadline: float, file_id: str) -> float:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError(f"Timed out waiting for vector store file {file_id!r} to finish processing")
    return remaining


def poll_vector_store_file(
    resource: Files,
    file_id: str,
    *,
    vector_store_id: str,
    poll_interval_ms: int | Omit,
    max_wait_seconds: float | Omit = omit,
) -> VectorStoreFile:
    """Poll a vector-store file using the caller's resource hooks."""
    validate_max_wait_seconds(max_wait_seconds)
    deadline = time.monotonic() + max_wait_seconds if is_given(max_wait_seconds) else None
    headers: dict[str, str] = {"X-Stainless-Poll-Helper": "true"}
    if is_given(poll_interval_ms):
        headers["X-Stainless-Custom-Poll-Interval"] = str(poll_interval_ms)

    while True:
        if deadline is not None:
            _remaining_poll_time(deadline, file_id)

        response = resource.with_raw_response.retrieve(
            file_id,
            vector_store_id=vector_store_id,
            extra_headers=headers,
        )

        file = response.parse()
        if file.status == "in_progress":
            if not is_given(poll_interval_ms):
                poll_interval_ms = _get_poll_interval_ms(response.headers)

            sleep_seconds = poll_interval_ms / 1000
            if deadline is not None:
                sleep_seconds = min(sleep_seconds, _remaining_poll_time(deadline, file_id))
            resource._sleep(sleep_seconds)
        elif file.status == "cancelled" or file.status == "completed" or file.status == "failed":
            return file
        else:
            if TYPE_CHECKING:  # type: ignore[unreachable]
                assert_never(file.status)
            else:
                return file


async def async_poll_vector_store_file(
    resource: AsyncFiles,
    file_id: str,
    *,
    vector_store_id: str,
    poll_interval_ms: int | Omit,
    max_wait_seconds: float | Omit = omit,
) -> VectorStoreFile:
    """Poll a vector-store file using the caller's async resource hooks."""
    validate_max_wait_seconds(max_wait_seconds)
    deadline = time.monotonic() + max_wait_seconds if is_given(max_wait_seconds) else None
    headers: dict[str, str] = {"X-Stainless-Poll-Helper": "true"}
    if is_given(poll_interval_ms):
        headers["X-Stainless-Custom-Poll-Interval"] = str(poll_interval_ms)

    while True:
        if deadline is not None:
            _remaining_poll_time(deadline, file_id)

        response = await resource.with_raw_response.retrieve(
            file_id,
            vector_store_id=vector_store_id,
            extra_headers=headers,
        )

        file = response.parse()
        if file.status == "in_progress":
            if not is_given(poll_interval_ms):
                poll_interval_ms = _get_poll_interval_ms(response.headers)

            sleep_seconds = poll_interval_ms / 1000
            if deadline is not None:
                sleep_seconds = min(sleep_seconds, _remaining_poll_time(deadline, file_id))
            await resource._sleep(sleep_seconds)
        elif file.status == "cancelled" or file.status == "completed" or file.status == "failed":
            return file
        else:
            if TYPE_CHECKING:  # type: ignore[unreachable]
                assert_never(file.status)
            else:
                return file


def poll_vector_store_file_batch(
    resource: FileBatches,
    batch_id: str,
    *,
    vector_store_id: str,
    poll_interval_ms: int | Omit,
) -> VectorStoreFileBatch:
    """Poll a vector-store batch using the caller's resource hooks."""
    headers: dict[str, str] = {"X-Stainless-Poll-Helper": "true"}
    if is_given(poll_interval_ms):
        headers["X-Stainless-Custom-Poll-Interval"] = str(poll_interval_ms)

    while True:
        response = resource.with_raw_response.retrieve(
            batch_id,
            vector_store_id=vector_store_id,
            extra_headers=headers,
        )

        batch = response.parse()
        if batch.file_counts.in_progress > 0:
            if not is_given(poll_interval_ms):
                poll_interval_ms = _get_poll_interval_ms(response.headers)

            resource._sleep(poll_interval_ms / 1000)
            continue

        return batch


async def async_poll_vector_store_file_batch(
    resource: AsyncFileBatches,
    batch_id: str,
    *,
    vector_store_id: str,
    poll_interval_ms: int | Omit,
) -> VectorStoreFileBatch:
    """Poll a vector-store batch using the caller's async resource hooks."""
    headers: dict[str, str] = {"X-Stainless-Poll-Helper": "true"}
    if is_given(poll_interval_ms):
        headers["X-Stainless-Custom-Poll-Interval"] = str(poll_interval_ms)

    while True:
        response = await resource.with_raw_response.retrieve(
            batch_id,
            vector_store_id=vector_store_id,
            extra_headers=headers,
        )

        batch = response.parse()
        if batch.file_counts.in_progress > 0:
            if not is_given(poll_interval_ms):
                poll_interval_ms = _get_poll_interval_ms(response.headers)

            await resource._sleep(poll_interval_ms / 1000)
            continue

        return batch
