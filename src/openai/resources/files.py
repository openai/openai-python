# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

import time
from typing import Mapping, cast

from ..types import FileObject, FileDeleted, file_create_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven, FileTypes
from .._utils import extract_files, maybe_transform, deepcopy_minimal
from .._resource import SyncAPIResource, AsyncAPIResource
from ..pagination import SyncPage, AsyncPage
from .._base_client import AsyncPaginator, make_request_options

__all__ = ["Files", "AsyncFiles"]


class Files(SyncAPIResource):
    def create(
        self,
        *,
        file: FileTypes,
        purpose: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> FileObject:
        """
        Upload a file that contains document(s) to be used across various
        endpoints/features. Currently, the size of all the files uploaded by one
        organization can be up to 1 GB. Please contact us if you need to increase the
        storage limit.

        Args:
          file: Name of the [JSON Lines](https://jsonlines.readthedocs.io/en/latest/) file to be
              uploaded.

              If the `purpose` is set to "fine-tune", the file will be used for fine-tuning.

          purpose: The intended purpose of the uploaded documents.

              Use "fine-tune" for
              [fine-tuning](https://platform.openai.com/docs/api-reference/fine-tuning). This
              allows us to validate the format of the uploaded file.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "file": file,
                "purpose": purpose,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        if files:
            # It should be noted that the actual Content-Type header that will be
            # sent to the server will contain a `boundary` parameter, e.g.
            # multipart/form-data; boundary=---abc--
            extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}

        return self._post(
            "/files",
            body=maybe_transform(body, file_create_params.FileCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileObject,
        )

    def retrieve(
        self,
        file_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> FileObject:
        """
        Returns information about a specific file.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/files/{file_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileObject,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> SyncPage[FileObject]:
        """Returns a list of files that belong to the user's organization."""
        return self._get_api_list(
            "/files",
            page=SyncPage[FileObject],
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            model=FileObject,
        )

    def delete(
        self,
        file_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> FileDeleted:
        """
        Delete a file.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._delete(
            f"/files/{file_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileDeleted,
        )

    def retrieve_content(
        self,
        file_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Returns the contents of the specified file.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json", **(extra_headers or {})}
        return self._get(
            f"/files/{file_id}/content",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=str,
        )

    def wait_for_processing(
        self,
        id: str,
        *,
        poll_interval: float = 5.0,
        max_wait_seconds: float = 30 * 60,
    ) -> FileObject:
        """Waits for the given file to be processed, default timeout is 30 mins."""
        TERMINAL_STATES = {"processed", "error", "deleted"}

        start = time.time()
        file = self.retrieve(id)
        while file.status not in TERMINAL_STATES:
            self._sleep(poll_interval)

            file = self.retrieve(id)
            if time.time() - start > max_wait_seconds:
                raise RuntimeError(
                    f"Giving up on waiting for file {id} to finish processing after {max_wait_seconds} seconds."
                )

        return file


class AsyncFiles(AsyncAPIResource):
    async def create(
        self,
        *,
        file: FileTypes,
        purpose: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> FileObject:
        """
        Upload a file that contains document(s) to be used across various
        endpoints/features. Currently, the size of all the files uploaded by one
        organization can be up to 1 GB. Please contact us if you need to increase the
        storage limit.

        Args:
          file: Name of the [JSON Lines](https://jsonlines.readthedocs.io/en/latest/) file to be
              uploaded.

              If the `purpose` is set to "fine-tune", the file will be used for fine-tuning.

          purpose: The intended purpose of the uploaded documents.

              Use "fine-tune" for
              [fine-tuning](https://platform.openai.com/docs/api-reference/fine-tuning). This
              allows us to validate the format of the uploaded file.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "file": file,
                "purpose": purpose,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        if files:
            # It should be noted that the actual Content-Type header that will be
            # sent to the server will contain a `boundary` parameter, e.g.
            # multipart/form-data; boundary=---abc--
            extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}

        return await self._post(
            "/files",
            body=maybe_transform(body, file_create_params.FileCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileObject,
        )

    async def retrieve(
        self,
        file_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> FileObject:
        """
        Returns information about a specific file.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/files/{file_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileObject,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[FileObject, AsyncPage[FileObject]]:
        """Returns a list of files that belong to the user's organization."""
        return self._get_api_list(
            "/files",
            page=AsyncPage[FileObject],
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            model=FileObject,
        )

    async def delete(
        self,
        file_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> FileDeleted:
        """
        Delete a file.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._delete(
            f"/files/{file_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileDeleted,
        )

    async def retrieve_content(
        self,
        file_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Returns the contents of the specified file.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/json", **(extra_headers or {})}
        return await self._get(
            f"/files/{file_id}/content",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=str,
        )

    async def wait_for_processing(
        self,
        id: str,
        *,
        poll_interval: float = 5.0,
        max_wait_seconds: float = 30 * 60,
    ) -> FileObject:
        """Waits for the given file to be processed, default timeout is 30 mins."""
        TERMINAL_STATES = {"processed", "error", "deleted"}

        start = time.time()
        file = await self.retrieve(id)
        while file.status not in TERMINAL_STATES:
            await self._sleep(poll_interval)

            file = await self.retrieve(id)
            if time.time() - start > max_wait_seconds:
                raise RuntimeError(
                    f"Giving up on waiting for file {id} to finish processing after {max_wait_seconds} seconds."
                )

        return file
