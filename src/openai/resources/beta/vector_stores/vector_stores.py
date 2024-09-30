# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal

import httpx

from .... import _legacy_response
from .files import (
    Files,
    AsyncFiles,
    FilesWithRawResponse,
    AsyncFilesWithRawResponse,
    FilesWithStreamingResponse,
    AsyncFilesWithStreamingResponse,
)
from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import (
    maybe_transform,
    async_maybe_transform,
)
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from .file_batches import (
    FileBatches,
    AsyncFileBatches,
    FileBatchesWithRawResponse,
    AsyncFileBatchesWithRawResponse,
    FileBatchesWithStreamingResponse,
    AsyncFileBatchesWithStreamingResponse,
)
from ....pagination import SyncCursorPage, AsyncCursorPage
from ....types.beta import (
    FileChunkingStrategyParam,
    vector_store_list_params,
    vector_store_create_params,
    vector_store_update_params,
)
from ...._base_client import AsyncPaginator, make_request_options
from ....types.beta.vector_store import VectorStore
from ....types.beta.vector_store_deleted import VectorStoreDeleted
from ....types.beta.file_chunking_strategy_param import FileChunkingStrategyParam

__all__ = ["VectorStores", "AsyncVectorStores"]


class VectorStores(SyncAPIResource):
    @cached_property
    def files(self) -> Files:
        return Files(self._client)

    @cached_property
    def file_batches(self) -> FileBatches:
        return FileBatches(self._client)

    @cached_property
    def with_raw_response(self) -> VectorStoresWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return VectorStoresWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> VectorStoresWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return VectorStoresWithStreamingResponse(self)

    def create(
        self,
        *,
        chunking_strategy: FileChunkingStrategyParam | NotGiven = NOT_GIVEN,
        expires_after: vector_store_create_params.ExpiresAfter | NotGiven = NOT_GIVEN,
        file_ids: List[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VectorStore:
        """
        Create a vector store.

        Args:
          chunking_strategy: The chunking strategy used to chunk the file(s). If not set, will use the `auto`
              strategy. Only applicable if `file_ids` is non-empty.

          expires_after: The expiration policy for a vector store.

          file_ids: A list of [File](https://platform.openai.com/docs/api-reference/files) IDs that
              the vector store should use. Useful for tools like `file_search` that can access
              files.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format. Keys
              can be a maximum of 64 characters long and values can be a maximum of 512
              characters long.

          name: The name of the vector store.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return self._post(
            "/vector_stores",
            body=maybe_transform(
                {
                    "chunking_strategy": chunking_strategy,
                    "expires_after": expires_after,
                    "file_ids": file_ids,
                    "metadata": metadata,
                    "name": name,
                },
                vector_store_create_params.VectorStoreCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VectorStore,
        )

    def retrieve(
        self,
        vector_store_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VectorStore:
        """
        Retrieves a vector store.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vector_store_id:
            raise ValueError(f"Expected a non-empty value for `vector_store_id` but received {vector_store_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return self._get(
            f"/vector_stores/{vector_store_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VectorStore,
        )

    def update(
        self,
        vector_store_id: str,
        *,
        expires_after: Optional[vector_store_update_params.ExpiresAfter] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        name: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VectorStore:
        """
        Modifies a vector store.

        Args:
          expires_after: The expiration policy for a vector store.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format. Keys
              can be a maximum of 64 characters long and values can be a maximum of 512
              characters long.

          name: The name of the vector store.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vector_store_id:
            raise ValueError(f"Expected a non-empty value for `vector_store_id` but received {vector_store_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return self._post(
            f"/vector_stores/{vector_store_id}",
            body=maybe_transform(
                {
                    "expires_after": expires_after,
                    "metadata": metadata,
                    "name": name,
                },
                vector_store_update_params.VectorStoreUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VectorStore,
        )

    def list(
        self,
        *,
        after: str | NotGiven = NOT_GIVEN,
        before: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncCursorPage[VectorStore]:
        """Returns a list of vector stores.

        Args:
          after: A cursor for use in pagination.

        `after` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include after=obj_foo in order to
              fetch the next page of the list.

          before: A cursor for use in pagination. `before` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include before=obj_foo in order to
              fetch the previous page of the list.

          limit: A limit on the number of objects to be returned. Limit can range between 1 and
              100, and the default is 20.

          order: Sort order by the `created_at` timestamp of the objects. `asc` for ascending
              order and `desc` for descending order.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return self._get_api_list(
            "/vector_stores",
            page=SyncCursorPage[VectorStore],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "before": before,
                        "limit": limit,
                        "order": order,
                    },
                    vector_store_list_params.VectorStoreListParams,
                ),
            ),
            model=VectorStore,
        )

    def delete(
        self,
        vector_store_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VectorStoreDeleted:
        """
        Delete a vector store.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vector_store_id:
            raise ValueError(f"Expected a non-empty value for `vector_store_id` but received {vector_store_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return self._delete(
            f"/vector_stores/{vector_store_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VectorStoreDeleted,
        )


class AsyncVectorStores(AsyncAPIResource):
    @cached_property
    def files(self) -> AsyncFiles:
        return AsyncFiles(self._client)

    @cached_property
    def file_batches(self) -> AsyncFileBatches:
        return AsyncFileBatches(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncVectorStoresWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncVectorStoresWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncVectorStoresWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncVectorStoresWithStreamingResponse(self)

    async def create(
        self,
        *,
        chunking_strategy: FileChunkingStrategyParam | NotGiven = NOT_GIVEN,
        expires_after: vector_store_create_params.ExpiresAfter | NotGiven = NOT_GIVEN,
        file_ids: List[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VectorStore:
        """
        Create a vector store.

        Args:
          chunking_strategy: The chunking strategy used to chunk the file(s). If not set, will use the `auto`
              strategy. Only applicable if `file_ids` is non-empty.

          expires_after: The expiration policy for a vector store.

          file_ids: A list of [File](https://platform.openai.com/docs/api-reference/files) IDs that
              the vector store should use. Useful for tools like `file_search` that can access
              files.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format. Keys
              can be a maximum of 64 characters long and values can be a maximum of 512
              characters long.

          name: The name of the vector store.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return await self._post(
            "/vector_stores",
            body=await async_maybe_transform(
                {
                    "chunking_strategy": chunking_strategy,
                    "expires_after": expires_after,
                    "file_ids": file_ids,
                    "metadata": metadata,
                    "name": name,
                },
                vector_store_create_params.VectorStoreCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VectorStore,
        )

    async def retrieve(
        self,
        vector_store_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VectorStore:
        """
        Retrieves a vector store.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vector_store_id:
            raise ValueError(f"Expected a non-empty value for `vector_store_id` but received {vector_store_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return await self._get(
            f"/vector_stores/{vector_store_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VectorStore,
        )

    async def update(
        self,
        vector_store_id: str,
        *,
        expires_after: Optional[vector_store_update_params.ExpiresAfter] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        name: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VectorStore:
        """
        Modifies a vector store.

        Args:
          expires_after: The expiration policy for a vector store.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format. Keys
              can be a maximum of 64 characters long and values can be a maximum of 512
              characters long.

          name: The name of the vector store.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vector_store_id:
            raise ValueError(f"Expected a non-empty value for `vector_store_id` but received {vector_store_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return await self._post(
            f"/vector_stores/{vector_store_id}",
            body=await async_maybe_transform(
                {
                    "expires_after": expires_after,
                    "metadata": metadata,
                    "name": name,
                },
                vector_store_update_params.VectorStoreUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VectorStore,
        )

    def list(
        self,
        *,
        after: str | NotGiven = NOT_GIVEN,
        before: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[VectorStore, AsyncCursorPage[VectorStore]]:
        """Returns a list of vector stores.

        Args:
          after: A cursor for use in pagination.

        `after` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include after=obj_foo in order to
              fetch the next page of the list.

          before: A cursor for use in pagination. `before` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include before=obj_foo in order to
              fetch the previous page of the list.

          limit: A limit on the number of objects to be returned. Limit can range between 1 and
              100, and the default is 20.

          order: Sort order by the `created_at` timestamp of the objects. `asc` for ascending
              order and `desc` for descending order.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return self._get_api_list(
            "/vector_stores",
            page=AsyncCursorPage[VectorStore],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "before": before,
                        "limit": limit,
                        "order": order,
                    },
                    vector_store_list_params.VectorStoreListParams,
                ),
            ),
            model=VectorStore,
        )

    async def delete(
        self,
        vector_store_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VectorStoreDeleted:
        """
        Delete a vector store.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vector_store_id:
            raise ValueError(f"Expected a non-empty value for `vector_store_id` but received {vector_store_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return await self._delete(
            f"/vector_stores/{vector_store_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VectorStoreDeleted,
        )


class VectorStoresWithRawResponse:
    def __init__(self, vector_stores: VectorStores) -> None:
        self._vector_stores = vector_stores

        self.create = _legacy_response.to_raw_response_wrapper(
            vector_stores.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            vector_stores.retrieve,
        )
        self.update = _legacy_response.to_raw_response_wrapper(
            vector_stores.update,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            vector_stores.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            vector_stores.delete,
        )

    @cached_property
    def files(self) -> FilesWithRawResponse:
        return FilesWithRawResponse(self._vector_stores.files)

    @cached_property
    def file_batches(self) -> FileBatchesWithRawResponse:
        return FileBatchesWithRawResponse(self._vector_stores.file_batches)


class AsyncVectorStoresWithRawResponse:
    def __init__(self, vector_stores: AsyncVectorStores) -> None:
        self._vector_stores = vector_stores

        self.create = _legacy_response.async_to_raw_response_wrapper(
            vector_stores.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            vector_stores.retrieve,
        )
        self.update = _legacy_response.async_to_raw_response_wrapper(
            vector_stores.update,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            vector_stores.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            vector_stores.delete,
        )

    @cached_property
    def files(self) -> AsyncFilesWithRawResponse:
        return AsyncFilesWithRawResponse(self._vector_stores.files)

    @cached_property
    def file_batches(self) -> AsyncFileBatchesWithRawResponse:
        return AsyncFileBatchesWithRawResponse(self._vector_stores.file_batches)


class VectorStoresWithStreamingResponse:
    def __init__(self, vector_stores: VectorStores) -> None:
        self._vector_stores = vector_stores

        self.create = to_streamed_response_wrapper(
            vector_stores.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            vector_stores.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            vector_stores.update,
        )
        self.list = to_streamed_response_wrapper(
            vector_stores.list,
        )
        self.delete = to_streamed_response_wrapper(
            vector_stores.delete,
        )

    @cached_property
    def files(self) -> FilesWithStreamingResponse:
        return FilesWithStreamingResponse(self._vector_stores.files)

    @cached_property
    def file_batches(self) -> FileBatchesWithStreamingResponse:
        return FileBatchesWithStreamingResponse(self._vector_stores.file_batches)


class AsyncVectorStoresWithStreamingResponse:
    def __init__(self, vector_stores: AsyncVectorStores) -> None:
        self._vector_stores = vector_stores

        self.create = async_to_streamed_response_wrapper(
            vector_stores.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            vector_stores.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            vector_stores.update,
        )
        self.list = async_to_streamed_response_wrapper(
            vector_stores.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            vector_stores.delete,
        )

    @cached_property
    def files(self) -> AsyncFilesWithStreamingResponse:
        return AsyncFilesWithStreamingResponse(self._vector_stores.files)

    @cached_property
    def file_batches(self) -> AsyncFileBatchesWithStreamingResponse:
        return AsyncFileBatchesWithStreamingResponse(self._vector_stores.file_batches)
