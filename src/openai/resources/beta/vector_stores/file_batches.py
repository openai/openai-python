# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import asyncio
from typing import List, Iterable
from typing_extensions import Literal
from concurrent.futures import Future, ThreadPoolExecutor, as_completed

import httpx
import sniffio

from .... import _legacy_response
from ....types import FileObject
from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven, FileTypes
from ...._utils import (
    is_given,
    maybe_transform,
    async_maybe_transform,
)
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ....pagination import SyncCursorPage, AsyncCursorPage
from ....types.beta import FileChunkingStrategyParam
from ...._base_client import AsyncPaginator, make_request_options
from ....types.beta.vector_stores import file_batch_create_params, file_batch_list_files_params
from ....types.beta.file_chunking_strategy_param import FileChunkingStrategyParam
from ....types.beta.vector_stores.vector_store_file import VectorStoreFile
from ....types.beta.vector_stores.vector_store_file_batch import VectorStoreFileBatch

__all__ = ["FileBatches", "AsyncFileBatches"]


class FileBatches(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FileBatchesWithRawResponse:
        return FileBatchesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FileBatchesWithStreamingResponse:
        return FileBatchesWithStreamingResponse(self)

    def create(
        self,
        vector_store_id: str,
        *,
        file_ids: List[str],
        chunking_strategy: FileChunkingStrategyParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VectorStoreFileBatch:
        """
        Create a vector store file batch.

        Args:
          file_ids: A list of [File](https://platform.openai.com/docs/api-reference/files) IDs that
              the vector store should use. Useful for tools like `file_search` that can access
              files.

          chunking_strategy: The chunking strategy used to chunk the file(s). If not set, will use the `auto`
              strategy. Only applicable if `file_ids` is non-empty.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vector_store_id:
            raise ValueError(f"Expected a non-empty value for `vector_store_id` but received {vector_store_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return self._post(
            f"/vector_stores/{vector_store_id}/file_batches",
            body=maybe_transform(
                {
                    "file_ids": file_ids,
                    "chunking_strategy": chunking_strategy,
                },
                file_batch_create_params.FileBatchCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VectorStoreFileBatch,
        )

    def retrieve(
        self,
        batch_id: str,
        *,
        vector_store_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VectorStoreFileBatch:
        """
        Retrieves a vector store file batch.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vector_store_id:
            raise ValueError(f"Expected a non-empty value for `vector_store_id` but received {vector_store_id!r}")
        if not batch_id:
            raise ValueError(f"Expected a non-empty value for `batch_id` but received {batch_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return self._get(
            f"/vector_stores/{vector_store_id}/file_batches/{batch_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VectorStoreFileBatch,
        )

    def cancel(
        self,
        batch_id: str,
        *,
        vector_store_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VectorStoreFileBatch:
        """Cancel a vector store file batch.

        This attempts to cancel the processing of
        files in this batch as soon as possible.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vector_store_id:
            raise ValueError(f"Expected a non-empty value for `vector_store_id` but received {vector_store_id!r}")
        if not batch_id:
            raise ValueError(f"Expected a non-empty value for `batch_id` but received {batch_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return self._post(
            f"/vector_stores/{vector_store_id}/file_batches/{batch_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VectorStoreFileBatch,
        )

    def create_and_poll(
        self,
        vector_store_id: str,
        *,
        file_ids: List[str],
        poll_interval_ms: int | NotGiven = NOT_GIVEN,
        chunking_strategy: FileChunkingStrategyParam | NotGiven = NOT_GIVEN,
    ) -> VectorStoreFileBatch:
        """Create a vector store batch and poll until all files have been processed."""
        batch = self.create(
            vector_store_id=vector_store_id,
            file_ids=file_ids,
            chunking_strategy=chunking_strategy,
        )
        # TODO: don't poll unless necessary??
        return self.poll(
            batch.id,
            vector_store_id=vector_store_id,
            poll_interval_ms=poll_interval_ms,
        )

    def list_files(
        self,
        batch_id: str,
        *,
        vector_store_id: str,
        after: str | NotGiven = NOT_GIVEN,
        before: str | NotGiven = NOT_GIVEN,
        filter: Literal["in_progress", "completed", "failed", "cancelled"] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncCursorPage[VectorStoreFile]:
        """
        Returns a list of vector store files in a batch.

        Args:
          after: A cursor for use in pagination. `after` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include after=obj_foo in order to
              fetch the next page of the list.

          before: A cursor for use in pagination. `before` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include before=obj_foo in order to
              fetch the previous page of the list.

          filter: Filter by file status. One of `in_progress`, `completed`, `failed`, `cancelled`.

          limit: A limit on the number of objects to be returned. Limit can range between 1 and
              100, and the default is 20.

          order: Sort order by the `created_at` timestamp of the objects. `asc` for ascending
              order and `desc` for descending order.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vector_store_id:
            raise ValueError(f"Expected a non-empty value for `vector_store_id` but received {vector_store_id!r}")
        if not batch_id:
            raise ValueError(f"Expected a non-empty value for `batch_id` but received {batch_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return self._get_api_list(
            f"/vector_stores/{vector_store_id}/file_batches/{batch_id}/files",
            page=SyncCursorPage[VectorStoreFile],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "before": before,
                        "filter": filter,
                        "limit": limit,
                        "order": order,
                    },
                    file_batch_list_files_params.FileBatchListFilesParams,
                ),
            ),
            model=VectorStoreFile,
        )

    def poll(
        self,
        batch_id: str,
        *,
        vector_store_id: str,
        poll_interval_ms: int | NotGiven = NOT_GIVEN,
    ) -> VectorStoreFileBatch:
        """Wait for the given file batch to be processed.

        Note: this will return even if one of the files failed to process, you need to
        check batch.file_counts.failed_count to handle this case.
        """
        headers: dict[str, str] = {"X-Stainless-Poll-Helper": "true"}
        if is_given(poll_interval_ms):
            headers["X-Stainless-Custom-Poll-Interval"] = str(poll_interval_ms)

        while True:
            response = self.with_raw_response.retrieve(
                batch_id,
                vector_store_id=vector_store_id,
                extra_headers=headers,
            )

            batch = response.parse()
            if batch.file_counts.in_progress > 0:
                if not is_given(poll_interval_ms):
                    from_header = response.headers.get("openai-poll-after-ms")
                    if from_header is not None:
                        poll_interval_ms = int(from_header)
                    else:
                        poll_interval_ms = 1000

                self._sleep(poll_interval_ms / 1000)
                continue

            return batch

    def upload_and_poll(
        self,
        vector_store_id: str,
        *,
        files: Iterable[FileTypes],
        max_concurrency: int = 5,
        file_ids: List[str] = [],
        poll_interval_ms: int | NotGiven = NOT_GIVEN,
        chunking_strategy: FileChunkingStrategyParam | NotGiven = NOT_GIVEN,
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
                    self._client.files.create,
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

        batch = self.create_and_poll(
            vector_store_id=vector_store_id,
            file_ids=[*file_ids, *(f.id for f in results)],
            poll_interval_ms=poll_interval_ms,
            chunking_strategy=chunking_strategy,
        )
        return batch


class AsyncFileBatches(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFileBatchesWithRawResponse:
        return AsyncFileBatchesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFileBatchesWithStreamingResponse:
        return AsyncFileBatchesWithStreamingResponse(self)

    async def create(
        self,
        vector_store_id: str,
        *,
        file_ids: List[str],
        chunking_strategy: FileChunkingStrategyParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VectorStoreFileBatch:
        """
        Create a vector store file batch.

        Args:
          file_ids: A list of [File](https://platform.openai.com/docs/api-reference/files) IDs that
              the vector store should use. Useful for tools like `file_search` that can access
              files.

          chunking_strategy: The chunking strategy used to chunk the file(s). If not set, will use the `auto`
              strategy. Only applicable if `file_ids` is non-empty.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vector_store_id:
            raise ValueError(f"Expected a non-empty value for `vector_store_id` but received {vector_store_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return await self._post(
            f"/vector_stores/{vector_store_id}/file_batches",
            body=await async_maybe_transform(
                {
                    "file_ids": file_ids,
                    "chunking_strategy": chunking_strategy,
                },
                file_batch_create_params.FileBatchCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VectorStoreFileBatch,
        )

    async def retrieve(
        self,
        batch_id: str,
        *,
        vector_store_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VectorStoreFileBatch:
        """
        Retrieves a vector store file batch.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vector_store_id:
            raise ValueError(f"Expected a non-empty value for `vector_store_id` but received {vector_store_id!r}")
        if not batch_id:
            raise ValueError(f"Expected a non-empty value for `batch_id` but received {batch_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return await self._get(
            f"/vector_stores/{vector_store_id}/file_batches/{batch_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VectorStoreFileBatch,
        )

    async def cancel(
        self,
        batch_id: str,
        *,
        vector_store_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VectorStoreFileBatch:
        """Cancel a vector store file batch.

        This attempts to cancel the processing of
        files in this batch as soon as possible.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vector_store_id:
            raise ValueError(f"Expected a non-empty value for `vector_store_id` but received {vector_store_id!r}")
        if not batch_id:
            raise ValueError(f"Expected a non-empty value for `batch_id` but received {batch_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return await self._post(
            f"/vector_stores/{vector_store_id}/file_batches/{batch_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VectorStoreFileBatch,
        )

    async def create_and_poll(
        self,
        vector_store_id: str,
        *,
        file_ids: List[str],
        poll_interval_ms: int | NotGiven = NOT_GIVEN,
        chunking_strategy: FileChunkingStrategyParam | NotGiven = NOT_GIVEN,
    ) -> VectorStoreFileBatch:
        """Create a vector store batch and poll until all files have been processed."""
        batch = await self.create(
            vector_store_id=vector_store_id,
            file_ids=file_ids,
            chunking_strategy=chunking_strategy,
        )
        # TODO: don't poll unless necessary??
        return await self.poll(
            batch.id,
            vector_store_id=vector_store_id,
            poll_interval_ms=poll_interval_ms,
        )

    def list_files(
        self,
        batch_id: str,
        *,
        vector_store_id: str,
        after: str | NotGiven = NOT_GIVEN,
        before: str | NotGiven = NOT_GIVEN,
        filter: Literal["in_progress", "completed", "failed", "cancelled"] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[VectorStoreFile, AsyncCursorPage[VectorStoreFile]]:
        """
        Returns a list of vector store files in a batch.

        Args:
          after: A cursor for use in pagination. `after` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include after=obj_foo in order to
              fetch the next page of the list.

          before: A cursor for use in pagination. `before` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include before=obj_foo in order to
              fetch the previous page of the list.

          filter: Filter by file status. One of `in_progress`, `completed`, `failed`, `cancelled`.

          limit: A limit on the number of objects to be returned. Limit can range between 1 and
              100, and the default is 20.

          order: Sort order by the `created_at` timestamp of the objects. `asc` for ascending
              order and `desc` for descending order.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vector_store_id:
            raise ValueError(f"Expected a non-empty value for `vector_store_id` but received {vector_store_id!r}")
        if not batch_id:
            raise ValueError(f"Expected a non-empty value for `batch_id` but received {batch_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return self._get_api_list(
            f"/vector_stores/{vector_store_id}/file_batches/{batch_id}/files",
            page=AsyncCursorPage[VectorStoreFile],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "before": before,
                        "filter": filter,
                        "limit": limit,
                        "order": order,
                    },
                    file_batch_list_files_params.FileBatchListFilesParams,
                ),
            ),
            model=VectorStoreFile,
        )

    async def poll(
        self,
        batch_id: str,
        *,
        vector_store_id: str,
        poll_interval_ms: int | NotGiven = NOT_GIVEN,
    ) -> VectorStoreFileBatch:
        """Wait for the given file batch to be processed.

        Note: this will return even if one of the files failed to process, you need to
        check batch.file_counts.failed_count to handle this case.
        """
        headers: dict[str, str] = {"X-Stainless-Poll-Helper": "true"}
        if is_given(poll_interval_ms):
            headers["X-Stainless-Custom-Poll-Interval"] = str(poll_interval_ms)

        while True:
            response = await self.with_raw_response.retrieve(
                batch_id,
                vector_store_id=vector_store_id,
                extra_headers=headers,
            )

            batch = response.parse()
            if batch.file_counts.in_progress > 0:
                if not is_given(poll_interval_ms):
                    from_header = response.headers.get("openai-poll-after-ms")
                    if from_header is not None:
                        poll_interval_ms = int(from_header)
                    else:
                        poll_interval_ms = 1000

                await self._sleep(poll_interval_ms / 1000)
                continue

            return batch

    async def upload_and_poll(
        self,
        vector_store_id: str,
        *,
        files: Iterable[FileTypes],
        max_concurrency: int = 5,
        file_ids: List[str] = [],
        poll_interval_ms: int | NotGiven = NOT_GIVEN,
        chunking_strategy: FileChunkingStrategyParam | NotGiven = NOT_GIVEN,
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
                    file_obj = await self._client.files.create(
                        file=file,
                        purpose="assistants",
                    )
                    uploaded_files.append(file_obj)

            semaphore = asyncio.Semaphore(max_concurrency)

            tasks = [asyncio_upload_file(semaphore, file) for file in files]

            await asyncio.gather(*tasks)
        elif async_library == "trio":
            # We only import if the library is being used.
            # We support Python 3.7 so are using an older version of trio that does not have type information
            import trio  # type: ignore # pyright: ignore[reportMissingTypeStubs]

            async def trio_upload_file(limiter: trio.CapacityLimiter, file: FileTypes) -> None:
                async with limiter:
                    file_obj = await self._client.files.create(
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

        batch = await self.create_and_poll(
            vector_store_id=vector_store_id,
            file_ids=[*file_ids, *(f.id for f in uploaded_files)],
            poll_interval_ms=poll_interval_ms,
            chunking_strategy=chunking_strategy,
        )
        return batch


class FileBatchesWithRawResponse:
    def __init__(self, file_batches: FileBatches) -> None:
        self._file_batches = file_batches

        self.create = _legacy_response.to_raw_response_wrapper(
            file_batches.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            file_batches.retrieve,
        )
        self.cancel = _legacy_response.to_raw_response_wrapper(
            file_batches.cancel,
        )
        self.list_files = _legacy_response.to_raw_response_wrapper(
            file_batches.list_files,
        )


class AsyncFileBatchesWithRawResponse:
    def __init__(self, file_batches: AsyncFileBatches) -> None:
        self._file_batches = file_batches

        self.create = _legacy_response.async_to_raw_response_wrapper(
            file_batches.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            file_batches.retrieve,
        )
        self.cancel = _legacy_response.async_to_raw_response_wrapper(
            file_batches.cancel,
        )
        self.list_files = _legacy_response.async_to_raw_response_wrapper(
            file_batches.list_files,
        )


class FileBatchesWithStreamingResponse:
    def __init__(self, file_batches: FileBatches) -> None:
        self._file_batches = file_batches

        self.create = to_streamed_response_wrapper(
            file_batches.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            file_batches.retrieve,
        )
        self.cancel = to_streamed_response_wrapper(
            file_batches.cancel,
        )
        self.list_files = to_streamed_response_wrapper(
            file_batches.list_files,
        )


class AsyncFileBatchesWithStreamingResponse:
    def __init__(self, file_batches: AsyncFileBatches) -> None:
        self._file_batches = file_batches

        self.create = async_to_streamed_response_wrapper(
            file_batches.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            file_batches.retrieve,
        )
        self.cancel = async_to_streamed_response_wrapper(
            file_batches.cancel,
        )
        self.list_files = async_to_streamed_response_wrapper(
            file_batches.list_files,
        )
