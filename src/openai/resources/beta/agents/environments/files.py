# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, overload

import httpx2

from ..... import _legacy_response
from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ....._utils import path_template, required_args, maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from .....pagination import SyncTokenPage, AsyncTokenPage
from ....._base_client import AsyncPaginator, make_request_options
from .....types.beta.agents.environments import file_list_params, file_create_params
from .....types.beta.agents.environments.environment_file import EnvironmentFile

__all__ = ["Files", "AsyncFiles"]


class Files(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FilesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
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

    @overload
    def create(
        self,
        environment_id: str,
        *,
        file_id: str,
        path: str,
        type: Literal["file_id"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentFile:
        """
        Copies inline bytes or a Files API file into a connected execution environment.
        See
        [environment files](https://developers.openai.com/api/docs/guides/agents-api/environments/files).

        Args:
          file_id: The ID of the uploaded file.

          path: The absolute destination path inside `/workspace`.

          type: The type of the object. Always `file_id`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        environment_id: str,
        *,
        data: str,
        path: str,
        type: Literal["inline"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentFile:
        """
        Copies inline bytes or a Files API file into a connected execution environment.
        See
        [environment files](https://developers.openai.com/api/docs/guides/agents-api/environments/files).

        Args:
          data: The standard-base64-encoded file contents.

          path: The absolute destination path inside `/workspace`.

          type: The type of the object. Always `inline`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["file_id", "path", "type"], ["data", "path", "type"])
    def create(
        self,
        environment_id: str,
        *,
        file_id: str | Omit = omit,
        path: str,
        type: Literal["file_id"] | Literal["inline"],
        data: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentFile:
        if not environment_id:
            raise ValueError(f"Expected a non-empty value for `environment_id` but received {environment_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._post(
            path_template("/agents/environments/{environment_id}/files", environment_id=environment_id),
            body=maybe_transform(
                {
                    "file_id": file_id,
                    "path": path,
                    "type": type,
                    "data": data,
                },
                file_create_params.FileCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=EnvironmentFile,
        )

    def list(
        self,
        environment_id: str,
        *,
        limit: Optional[int] | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        page: str | Omit = omit,
        path: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SyncTokenPage[EnvironmentFile]:
        """
        Lists live files on a connected execution environment with optional directory
        filtering and opaque cursor pagination. See
        [environment files](https://developers.openai.com/api/docs/guides/agents-api/environments/files).

        Args:
          limit: The maximum number of files to return, between 1 and 100.

          order: Sort by case-sensitive path components. Defaults to descending.

              - `asc` - Returns resources in ascending order.
              - `desc` - Returns resources in descending order.

          page: The opaque token from the previous page. Keep the same path, order, and limit.

          path: Restrict the listing to this absolute workspace directory.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not environment_id:
            raise ValueError(f"Expected a non-empty value for `environment_id` but received {environment_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get_api_list(
            path_template("/agents/environments/{environment_id}/files", environment_id=environment_id),
            page=SyncTokenPage[EnvironmentFile],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "order": order,
                        "page": page,
                        "path": path,
                    },
                    file_list_params.FileListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=EnvironmentFile,
        )


class AsyncFiles(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFilesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
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

    @overload
    async def create(
        self,
        environment_id: str,
        *,
        file_id: str,
        path: str,
        type: Literal["file_id"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentFile:
        """
        Copies inline bytes or a Files API file into a connected execution environment.
        See
        [environment files](https://developers.openai.com/api/docs/guides/agents-api/environments/files).

        Args:
          file_id: The ID of the uploaded file.

          path: The absolute destination path inside `/workspace`.

          type: The type of the object. Always `file_id`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        environment_id: str,
        *,
        data: str,
        path: str,
        type: Literal["inline"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentFile:
        """
        Copies inline bytes or a Files API file into a connected execution environment.
        See
        [environment files](https://developers.openai.com/api/docs/guides/agents-api/environments/files).

        Args:
          data: The standard-base64-encoded file contents.

          path: The absolute destination path inside `/workspace`.

          type: The type of the object. Always `inline`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["file_id", "path", "type"], ["data", "path", "type"])
    async def create(
        self,
        environment_id: str,
        *,
        file_id: str | Omit = omit,
        path: str,
        type: Literal["file_id"] | Literal["inline"],
        data: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentFile:
        if not environment_id:
            raise ValueError(f"Expected a non-empty value for `environment_id` but received {environment_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._post(
            path_template("/agents/environments/{environment_id}/files", environment_id=environment_id),
            body=await async_maybe_transform(
                {
                    "file_id": file_id,
                    "path": path,
                    "type": type,
                    "data": data,
                },
                file_create_params.FileCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=EnvironmentFile,
        )

    def list(
        self,
        environment_id: str,
        *,
        limit: Optional[int] | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        page: str | Omit = omit,
        path: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[EnvironmentFile, AsyncTokenPage[EnvironmentFile]]:
        """
        Lists live files on a connected execution environment with optional directory
        filtering and opaque cursor pagination. See
        [environment files](https://developers.openai.com/api/docs/guides/agents-api/environments/files).

        Args:
          limit: The maximum number of files to return, between 1 and 100.

          order: Sort by case-sensitive path components. Defaults to descending.

              - `asc` - Returns resources in ascending order.
              - `desc` - Returns resources in descending order.

          page: The opaque token from the previous page. Keep the same path, order, and limit.

          path: Restrict the listing to this absolute workspace directory.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not environment_id:
            raise ValueError(f"Expected a non-empty value for `environment_id` but received {environment_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get_api_list(
            path_template("/agents/environments/{environment_id}/files", environment_id=environment_id),
            page=AsyncTokenPage[EnvironmentFile],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "order": order,
                        "page": page,
                        "path": path,
                    },
                    file_list_params.FileListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=EnvironmentFile,
        )


class FilesWithRawResponse:
    def __init__(self, files: Files) -> None:
        self._files = files

        self.create = _legacy_response.to_raw_response_wrapper(
            files.create,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            files.list,
        )


class AsyncFilesWithRawResponse:
    def __init__(self, files: AsyncFiles) -> None:
        self._files = files

        self.create = _legacy_response.async_to_raw_response_wrapper(
            files.create,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            files.list,
        )


class FilesWithStreamingResponse:
    def __init__(self, files: Files) -> None:
        self._files = files

        self.create = to_streamed_response_wrapper(
            files.create,
        )
        self.list = to_streamed_response_wrapper(
            files.list,
        )


class AsyncFilesWithStreamingResponse:
    def __init__(self, files: AsyncFiles) -> None:
        self._files = files

        self.create = async_to_streamed_response_wrapper(
            files.create,
        )
        self.list = async_to_streamed_response_wrapper(
            files.list,
        )
