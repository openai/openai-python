from __future__ import annotations

from typing import TYPE_CHECKING, Mapping
from typing_extensions import assert_never

from .._types import Omit
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


def poll_vector_store_file(
    resource: Files,
    file_id: str,
    *,
    vector_store_id: str,
    poll_interval_ms: int | Omit,
) -> VectorStoreFile:
    """Poll a vector-store file using the caller's resource hooks."""
    headers: dict[str, str] = {"X-Stainless-Poll-Helper": "true"}
    if is_given(poll_interval_ms):
        headers["X-Stainless-Custom-Poll-Interval"] = str(poll_interval_ms)

    while True:
        response = resource.with_raw_response.retrieve(
            file_id,
            vector_store_id=vector_store_id,
            extra_headers=headers,
        )

        file = response.parse()
        if file.status == "in_progress":
            if not is_given(poll_interval_ms):
                poll_interval_ms = _get_poll_interval_ms(response.headers)

            resource._sleep(poll_interval_ms / 1000)
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
) -> VectorStoreFile:
    """Poll a vector-store file using the caller's async resource hooks."""
    headers: dict[str, str] = {"X-Stainless-Poll-Helper": "true"}
    if is_given(poll_interval_ms):
        headers["X-Stainless-Custom-Poll-Interval"] = str(poll_interval_ms)

    while True:
        response = await resource.with_raw_response.retrieve(
            file_id,
            vector_store_id=vector_store_id,
            extra_headers=headers,
        )

        file = response.parse()
        if file.status == "in_progress":
            if not is_given(poll_interval_ms):
                poll_interval_ms = _get_poll_interval_ms(response.headers)

            await resource._sleep(poll_interval_ms / 1000)
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
