# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import TYPE_CHECKING
from typing_extensions import Literal, assert_never

import httpx

from .... import _legacy_response
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
from ....types.beta.vector_stores import file_list_params, file_create_params
from ....types.beta.file_chunking_strategy_param import FileChunkingStrategyParam
from ....types.beta.vector_stores.vector_store_file import VectorStoreFile
from ....types.beta.vector_stores.vector_store_file_deleted import VectorStoreFileDeleted

__all__ = ["Files", "AsyncFiles"]


class Files(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FilesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return FilesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FilesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return FilesWithStreamingResponse(self)

    def create(
        self,
        vector_store_id: str,
        *,
        file_id: str,
        chunking_strategy: FileChunkingStrategyParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VectorStoreFile:
        """
        Create a vector store file by attaching a
        [File](https://platform.openai.com/docs/api-reference/files) to a
        [vector store](https://platform.openai.com/docs/api-reference/vector-stores/object).

        Args:
          file_id: A [File](https://platform.openai.com/docs/api-reference/files) ID that the
              vector store should use. Useful for tools like `file_search` that can access
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
            f"/vector_stores/{vector_store_id}/files",
            body=maybe_transform(
                {
                    "file_id": file_id,
                    "chunking_strategy": chunking_strategy,
                },
                file_create_params.FileCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VectorStoreFile,
        )

    def retrieve(
        self,
        file_id: str,
        *,
        vector_store_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VectorStoreFile:
        """
        Retrieves a vector store file.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vector_store_id:
            raise ValueError(f"Expected a non-empty value for `vector_store_id` but received {vector_store_id!r}")
        if not file_id:
            raise ValueError(f"Expected a non-empty value for `file_id` but received {file_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return self._get(
            f"/vector_stores/{vector_store_id}/files/{file_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VectorStoreFile,
        )

    def list(
        self,
        vector_store_id: str,
        *,
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
        Returns a list of vector store files.

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
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return self._get_api_list(
            f"/vector_stores/{vector_store_id}/files",
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
                    file_list_params.FileListParams,
                ),
            ),
            model=VectorStoreFile,
        )

    def delete(
        self,
        file_id: str,
        *,
        vector_store_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VectorStoreFileDeleted:
        """Delete a vector store file.

        This will remove the file from the vector store but
        the file itself will not be deleted. To delete the file, use the
        [delete file](https://platform.openai.com/docs/api-reference/files/delete)
        endpoint.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vector_store_id:
            raise ValueError(f"Expected a non-empty value for `vector_store_id` but received {vector_store_id!r}")
        if not file_id:
            raise ValueError(f"Expected a non-empty value for `file_id` but received {file_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return self._delete(
            f"/vector_stores/{vector_store_id}/files/{file_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VectorStoreFileDeleted,
        )

    def create_and_poll(
        self,
        file_id: str,
        *,
        vector_store_id: str,
        poll_interval_ms: int | NotGiven = NOT_GIVEN,
        chunking_strategy: FileChunkingStrategyParam | NotGiven = NOT_GIVEN,
    ) -> VectorStoreFile:
        """Attach a file to the given vector store and wait for it to be processed."""
        self.create(vector_store_id=vector_store_id, file_id=file_id, chunking_strategy=chunking_strategy)

        return self.poll(
            file_id,
            vector_store_id=vector_store_id,
            poll_interval_ms=poll_interval_ms,
        )

    def poll(
        self,
        file_id: str,
        *,
        vector_store_id: str,
        poll_interval_ms: int | NotGiven = NOT_GIVEN,
    ) -> VectorStoreFile:
        """Wait for the vector store file to finish processing.

        Note: this will return even if the file failed to process, you need to check
        file.last_error and file.status to handle these cases
        """
        headers: dict[str, str] = {"X-Stainless-Poll-Helper": "true"}
        if is_given(poll_interval_ms):
            headers["X-Stainless-Custom-Poll-Interval"] = str(poll_interval_ms)

        while True:
            response = self.with_raw_response.retrieve(
                file_id,
                vector_store_id=vector_store_id,
                extra_headers=headers,
            )

            file = response.parse()
            if file.status == "in_progress":
                if not is_given(poll_interval_ms):
                    from_header = response.headers.get("openai-poll-after-ms")
                    if from_header is not None:
                        poll_interval_ms = int(from_header)
                    else:
                        poll_interval_ms = 1000

                self._sleep(poll_interval_ms / 1000)
            elif file.status == "cancelled" or file.status == "completed" or file.status == "failed":
                return file
            else:
                if TYPE_CHECKING:  # type: ignore[unreachable]
                    assert_never(file.status)
                else:
                    return file

    def upload(
        self,
        *,
        vector_store_id: str,
        file: FileTypes,
        chunking_strategy: FileChunkingStrategyParam | NotGiven = NOT_GIVEN,
    ) -> VectorStoreFile:
        """Upload a file to the `files` API and then attach it to the given vector store.

        Note the file will be asynchronously processed (you can use the alternative
        polling helper method to wait for processing to complete).
        """
        file_obj = self._client.files.create(file=file, purpose="assistants")
        return self.create(vector_store_id=vector_store_id, file_id=file_obj.id, chunking_strategy=chunking_strategy)

    def upload_and_poll(
        self,
        *,
        vector_store_id: str,
        file: FileTypes,
        poll_interval_ms: int | NotGiven = NOT_GIVEN,
        chunking_strategy: FileChunkingStrategyParam | NotGiven = NOT_GIVEN,
    ) -> VectorStoreFile:
        """Add a file to a vector store and poll until processing is complete."""
        file_obj = self._client.files.create(file=file, purpose="assistants")
        return self.create_and_poll(
            vector_store_id=vector_store_id,
            file_id=file_obj.id,
            chunking_strategy=chunking_strategy,
            poll_interval_ms=poll_interval_ms,
        )


class AsyncFiles(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFilesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncFilesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFilesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncFilesWithStreamingResponse(self)

    async def create(
        self,
        vector_store_id: str,
        *,
        file_id: str,
        chunking_strategy: FileChunkingStrategyParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VectorStoreFile:
        """
        Create a vector store file by attaching a
        [File](https://platform.openai.com/docs/api-reference/files) to a
        [vector store](https://platform.openai.com/docs/api-reference/vector-stores/object).

        Args:
          file_id: A [File](https://platform.openai.com/docs/api-reference/files) ID that the
              vector store should use. Useful for tools like `file_search` that can access
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
            f"/vector_stores/{vector_store_id}/files",
            body=await async_maybe_transform(
                {
                    "file_id": file_id,
                    "chunking_strategy": chunking_strategy,
                },
                file_create_params.FileCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VectorStoreFile,
        )

    async def retrieve(
        self,
        file_id: str,
        *,
        vector_store_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VectorStoreFile:
        """
        Retrieves a vector store file.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vector_store_id:
            raise ValueError(f"Expected a non-empty value for `vector_store_id` but received {vector_store_id!r}")
        if not file_id:
            raise ValueError(f"Expected a non-empty value for `file_id` but received {file_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return await self._get(
            f"/vector_stores/{vector_store_id}/files/{file_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VectorStoreFile,
        )

    def list(
        self,
        vector_store_id: str,
        *,
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
        Returns a list of vector store files.

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
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return self._get_api_list(
            f"/vector_stores/{vector_store_id}/files",
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
                    file_list_params.FileListParams,
                ),
            ),
            model=VectorStoreFile,
        )

    async def delete(
        self,
        file_id: str,
        *,
        vector_store_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VectorStoreFileDeleted:
        """Delete a vector store file.

        This will remove the file from the vector store but
        the file itself will not be deleted. To delete the file, use the
        [delete file](https://platform.openai.com/docs/api-reference/files/delete)
        endpoint.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vector_store_id:
            raise ValueError(f"Expected a non-empty value for `vector_store_id` but received {vector_store_id!r}")
        if not file_id:
            raise ValueError(f"Expected a non-empty value for `file_id` but received {file_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return await self._delete(
            f"/vector_stores/{vector_store_id}/files/{file_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VectorStoreFileDeleted,
        )

    async def create_and_poll(
        self,
        file_id: str,
        *,
        vector_store_id: str,
        poll_interval_ms: int | NotGiven = NOT_GIVEN,
        chunking_strategy: FileChunkingStrategyParam | NotGiven = NOT_GIVEN,
    ) -> VectorStoreFile:
        """Attach a file to the given vector store and wait for it to be processed."""
        await self.create(vector_store_id=vector_store_id, file_id=file_id, chunking_strategy=chunking_strategy)

        return await self.poll(
            file_id,
            vector_store_id=vector_store_id,
            poll_interval_ms=poll_interval_ms,
        )

    async def poll(
        self,
        file_id: str,
        *,
        vector_store_id: str,
        poll_interval_ms: int | NotGiven = NOT_GIVEN,
    ) -> VectorStoreFile:
        """Wait for the vector store file to finish processing.

        Note: this will return even if the file failed to process, you need to check
        file.last_error and file.status to handle these cases
        """
        headers: dict[str, str] = {"X-Stainless-Poll-Helper": "true"}
        if is_given(poll_interval_ms):
            headers["X-Stainless-Custom-Poll-Interval"] = str(poll_interval_ms)

        while True:
            response = await self.with_raw_response.retrieve(
                file_id,
                vector_store_id=vector_store_id,
                extra_headers=headers,
            )

            file = response.parse()
            if file.status == "in_progress":
                if not is_given(poll_interval_ms):
                    from_header = response.headers.get("openai-poll-after-ms")
                    if from_header is not None:
                        poll_interval_ms = int(from_header)
                    else:
                        poll_interval_ms = 1000

                await self._sleep(poll_interval_ms / 1000)
            elif file.status == "cancelled" or file.status == "completed" or file.status == "failed":
                return file
            else:
                if TYPE_CHECKING:  # type: ignore[unreachable]
                    assert_never(file.status)
                else:
                    return file

    async def upload(
        self,
        *,
        vector_store_id: str,
        file: FileTypes,
        chunking_strategy: FileChunkingStrategyParam | NotGiven = NOT_GIVEN,
    ) -> VectorStoreFile:
        """Upload a file to the `files` API and then attach it to the given vector store.

        Note the file will be asynchronously processed (you can use the alternative
        polling helper method to wait for processing to complete).
        """
        file_obj = await self._client.files.create(file=file, purpose="assistants")
        return await self.create(
            vector_store_id=vector_store_id, file_id=file_obj.id, chunking_strategy=chunking_strategy
        )

    async def upload_and_poll(
        self,
        *,
        vector_store_id: str,
        file: FileTypes,
        poll_interval_ms: int | NotGiven = NOT_GIVEN,
        chunking_strategy: FileChunkingStrategyParam | NotGiven = NOT_GIVEN,
    ) -> VectorStoreFile:
        """Add a file to a vector store and poll until processing is complete."""
        file_obj = await self._client.files.create(file=file, purpose="assistants")
        return await self.create_and_poll(
            vector_store_id=vector_store_id,
            file_id=file_obj.id,
            poll_interval_ms=poll_interval_ms,
            chunking_strategy=chunking_strategy,
        )


class FilesWithRawResponse:
    def __init__(self, files: Files) -> None:
        self._files = files

        self.create = _legacy_response.to_raw_response_wrapper(
            files.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            files.retrieve,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            files.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            files.delete,
        )


class AsyncFilesWithRawResponse:
    def __init__(self, files: AsyncFiles) -> None:
        self._files = files

        self.create = _legacy_response.async_to_raw_response_wrapper(
            files.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            files.retrieve,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            files.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            files.delete,
        )


class FilesWithStreamingResponse:
    def __init__(self, files: Files) -> None:
        self._files = files

        self.create = to_streamed_response_wrapper(
            files.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            files.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            files.list,
        )
        self.delete = to_streamed_response_wrapper(
            files.delete,
        )


class AsyncFilesWithStreamingResponse:
    def __init__(self, files: AsyncFiles) -> None:
        self._files = files

        self.create = async_to_streamed_response_wrapper(
            files.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            files.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            files.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            files.delete,
        )
