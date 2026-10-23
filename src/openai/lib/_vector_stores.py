from __future__ import annotations

import math
import time
import asyncio
from typing import TYPE_CHECKING, Dict, Union, Mapping, Iterable, Optional
from typing_extensions import assert_never
from concurrent.futures import Future, ThreadPoolExecutor, as_completed

import httpx2
import sniffio

from .._types import Body, Omit, Query, Headers, NotGiven, FileTypes, SequenceNotStr, omit, not_given
from .._utils import is_given
from ..types.file_object import FileObject
from ..types.vector_stores import file_batch_create_params
from ..types.file_chunking_strategy_param import FileChunkingStrategyParam
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


def create_and_poll_vector_store_file(
    resource: Files,
    file_id: str,
    *,
    vector_store_id: str,
    attributes: Optional[Dict[str, Union[str, float, bool]]] | Omit = omit,
    poll_interval_ms: int | Omit = omit,
    max_wait_seconds: float | Omit = omit,
    chunking_strategy: FileChunkingStrategyParam | Omit = omit,
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx2.Timeout | None | NotGiven = not_given,
) -> VectorStoreFile:
    """Attach a file to the given vector store and wait for it to be processed.

    `max_wait_seconds` limits polling after attachment; see `poll` for details.
    """
    validate_max_wait_seconds(max_wait_seconds)
    resource.create(
        vector_store_id=vector_store_id,
        file_id=file_id,
        chunking_strategy=chunking_strategy,
        attributes=attributes,
        extra_headers=extra_headers,
        extra_query=extra_query,
        extra_body=extra_body,
        timeout=timeout,
    )

    return resource.poll(
        file_id,
        vector_store_id=vector_store_id,
        poll_interval_ms=poll_interval_ms,
        max_wait_seconds=max_wait_seconds,
    )


def upload_vector_store_file(
    resource: Files,
    *,
    vector_store_id: str,
    file: FileTypes,
    chunking_strategy: FileChunkingStrategyParam | Omit = omit,
) -> VectorStoreFile:
    """Upload a file to the `files` API and then attach it to the given vector store.

    Note the file will be asynchronously processed (you can use the alternative
    polling helper method to wait for processing to complete).
    """
    file_obj = resource._client.files.create(file=file, purpose="assistants")
    return resource.create(vector_store_id=vector_store_id, file_id=file_obj.id, chunking_strategy=chunking_strategy)


def upload_and_poll_vector_store_file(
    resource: Files,
    *,
    vector_store_id: str,
    file: FileTypes,
    attributes: Optional[Dict[str, Union[str, float, bool]]] | Omit = omit,
    poll_interval_ms: int | Omit = omit,
    max_wait_seconds: float | Omit = omit,
    chunking_strategy: FileChunkingStrategyParam | Omit = omit,
) -> VectorStoreFile:
    """Add a file to a vector store and poll until processing is complete.

    `max_wait_seconds` limits polling after upload and attachment; see `poll` for details.
    """
    validate_max_wait_seconds(max_wait_seconds)
    file_obj = resource._client.files.create(file=file, purpose="assistants")
    return resource.create_and_poll(
        vector_store_id=vector_store_id,
        file_id=file_obj.id,
        chunking_strategy=chunking_strategy,
        poll_interval_ms=poll_interval_ms,
        max_wait_seconds=max_wait_seconds,
        attributes=attributes,
    )


async def async_create_and_poll_vector_store_file(
    resource: AsyncFiles,
    file_id: str,
    *,
    vector_store_id: str,
    attributes: Optional[Dict[str, Union[str, float, bool]]] | Omit = omit,
    poll_interval_ms: int | Omit = omit,
    max_wait_seconds: float | Omit = omit,
    chunking_strategy: FileChunkingStrategyParam | Omit = omit,
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx2.Timeout | None | NotGiven = not_given,
) -> VectorStoreFile:
    """Attach a file to the given vector store and wait for it to be processed.

    `max_wait_seconds` limits polling after attachment; see `poll` for details.
    """
    validate_max_wait_seconds(max_wait_seconds)
    await resource.create(
        vector_store_id=vector_store_id,
        file_id=file_id,
        chunking_strategy=chunking_strategy,
        attributes=attributes,
        extra_headers=extra_headers,
        extra_query=extra_query,
        extra_body=extra_body,
        timeout=timeout,
    )

    return await resource.poll(
        file_id,
        vector_store_id=vector_store_id,
        poll_interval_ms=poll_interval_ms,
        max_wait_seconds=max_wait_seconds,
    )


async def async_upload_vector_store_file(
    resource: AsyncFiles,
    *,
    vector_store_id: str,
    file: FileTypes,
    chunking_strategy: FileChunkingStrategyParam | Omit = omit,
) -> VectorStoreFile:
    """Upload a file to the `files` API and then attach it to the given vector store.

    Note the file will be asynchronously processed (you can use the alternative
    polling helper method to wait for processing to complete).
    """
    file_obj = await resource._client.files.create(file=file, purpose="assistants")
    return await resource.create(
        vector_store_id=vector_store_id, file_id=file_obj.id, chunking_strategy=chunking_strategy
    )


async def async_upload_and_poll_vector_store_file(
    resource: AsyncFiles,
    *,
    vector_store_id: str,
    file: FileTypes,
    attributes: Optional[Dict[str, Union[str, float, bool]]] | Omit = omit,
    poll_interval_ms: int | Omit = omit,
    max_wait_seconds: float | Omit = omit,
    chunking_strategy: FileChunkingStrategyParam | Omit = omit,
) -> VectorStoreFile:
    """Add a file to a vector store and poll until processing is complete.

    `max_wait_seconds` limits polling after upload and attachment; see `poll` for details.
    """
    validate_max_wait_seconds(max_wait_seconds)
    file_obj = await resource._client.files.create(file=file, purpose="assistants")
    return await resource.create_and_poll(
        vector_store_id=vector_store_id,
        file_id=file_obj.id,
        poll_interval_ms=poll_interval_ms,
        max_wait_seconds=max_wait_seconds,
        chunking_strategy=chunking_strategy,
        attributes=attributes,
    )


def create_and_poll_vector_store_file_batch(
    resource: FileBatches,
    vector_store_id: str,
    *,
    attributes: Optional[Dict[str, Union[str, float, bool]]] | Omit = omit,
    chunking_strategy: FileChunkingStrategyParam | Omit = omit,
    file_ids: SequenceNotStr[str] | Omit = omit,
    files: Iterable[file_batch_create_params.File] | Omit = omit,
    poll_interval_ms: int | Omit = omit,
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx2.Timeout | None | NotGiven = not_given,
) -> VectorStoreFileBatch:
    """Create a vector store batch and poll until all files have been processed."""
    batch = resource.create(
        vector_store_id=vector_store_id,
        attributes=attributes,
        chunking_strategy=chunking_strategy,
        file_ids=file_ids,
        files=files,
        extra_headers=extra_headers,
        extra_query=extra_query,
        extra_body=extra_body,
        timeout=timeout,
    )
    # TODO: don't poll unless necessary??
    return resource.poll(
        batch.id,
        vector_store_id=vector_store_id,
        poll_interval_ms=poll_interval_ms,
    )


def upload_and_poll_vector_store_file_batch(
    resource: FileBatches,
    vector_store_id: str,
    *,
    files: Iterable[FileTypes],
    max_concurrency: int = 5,
    file_ids: SequenceNotStr[str] = [],
    poll_interval_ms: int | Omit = omit,
    chunking_strategy: FileChunkingStrategyParam | Omit = omit,
) -> VectorStoreFileBatch:
    """Uploads the given files concurrently and then creates a vector store file batch.

    If you've already uploaded certain files that you want to include in this batch
    then you can pass their IDs through the `file_ids` argument.

    By default, if any file upload fails then an exception will be eagerly raised.

    The number of concurrency uploads is configurable using the `max_concurrency`
    parameter.

    Note: this method only supports `asyncio` or `trio` as the backing async
    runtime.
    """
    results: list[FileObject] = []

    with ThreadPoolExecutor(max_workers=max_concurrency) as executor:
        futures: list[Future[FileObject]] = [
            executor.submit(
                resource._client.files.create,
                file=file,
                purpose="assistants",
            )
            for file in files
        ]

    for future in as_completed(futures):
        exc = future.exception()
        if exc:
            raise exc

        results.append(future.result())

    batch = resource.create_and_poll(
        vector_store_id=vector_store_id,
        file_ids=[*file_ids, *(f.id for f in results)],
        poll_interval_ms=poll_interval_ms,
        chunking_strategy=chunking_strategy,
    )
    return batch


async def async_create_and_poll_vector_store_file_batch(
    resource: AsyncFileBatches,
    vector_store_id: str,
    *,
    attributes: Optional[Dict[str, Union[str, float, bool]]] | Omit = omit,
    chunking_strategy: FileChunkingStrategyParam | Omit = omit,
    file_ids: SequenceNotStr[str] | Omit = omit,
    files: Iterable[file_batch_create_params.File] | Omit = omit,
    poll_interval_ms: int | Omit = omit,
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx2.Timeout | None | NotGiven = not_given,
) -> VectorStoreFileBatch:
    """Create a vector store batch and poll until all files have been processed."""
    batch = await resource.create(
        vector_store_id=vector_store_id,
        attributes=attributes,
        chunking_strategy=chunking_strategy,
        file_ids=file_ids,
        files=files,
        extra_headers=extra_headers,
        extra_query=extra_query,
        extra_body=extra_body,
        timeout=timeout,
    )
    # TODO: don't poll unless necessary??
    return await resource.poll(
        batch.id,
        vector_store_id=vector_store_id,
        poll_interval_ms=poll_interval_ms,
    )


async def async_upload_and_poll_vector_store_file_batch(
    resource: AsyncFileBatches,
    vector_store_id: str,
    *,
    files: Iterable[FileTypes],
    max_concurrency: int = 5,
    file_ids: SequenceNotStr[str] = [],
    poll_interval_ms: int | Omit = omit,
    chunking_strategy: FileChunkingStrategyParam | Omit = omit,
) -> VectorStoreFileBatch:
    """Uploads the given files concurrently and then creates a vector store file batch.

    If you've already uploaded certain files that you want to include in this batch
    then you can pass their IDs through the `file_ids` argument.

    By default, if any file upload fails then an exception will be eagerly raised.

    The number of concurrency uploads is configurable using the `max_concurrency`
    parameter.

    Note: this method only supports `asyncio` or `trio` as the backing async
    runtime.
    """
    uploaded_files: list[FileObject] = []

    async_library = sniffio.current_async_library()

    if async_library == "asyncio":

        async def asyncio_upload_file(semaphore: asyncio.Semaphore, file: FileTypes) -> None:
            async with semaphore:
                file_obj = await resource._client.files.create(
                    file=file,
                    purpose="assistants",
                )
                uploaded_files.append(file_obj)

        semaphore = asyncio.Semaphore(max_concurrency)

        tasks = [asyncio_upload_file(semaphore, file) for file in files]

        await asyncio.gather(*tasks)
    elif async_library == "trio":
        # We only import if the library is being used.
        import trio  # type: ignore # pyright: ignore[reportMissingTypeStubs]

        async def trio_upload_file(limiter: trio.CapacityLimiter, file: FileTypes) -> None:
            async with limiter:
                file_obj = await resource._client.files.create(
                    file=file,
                    purpose="assistants",
                )
                uploaded_files.append(file_obj)

        limiter = trio.CapacityLimiter(max_concurrency)

        async with trio.open_nursery() as nursery:
            for file in files:
                nursery.start_soon(trio_upload_file, limiter, file)  # pyright: ignore [reportUnknownMemberType]
    else:
        raise RuntimeError(
            f"Async runtime {async_library} is not supported yet. Only asyncio or trio is supported",
        )

    batch = await resource.create_and_poll(
        vector_store_id=vector_store_id,
        file_ids=[*file_ids, *(f.id for f in uploaded_files)],
        poll_interval_ms=poll_interval_ms,
        chunking_strategy=chunking_strategy,
    )
    return batch
