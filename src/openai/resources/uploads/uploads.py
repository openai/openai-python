# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List

import httpx

from ... import _legacy_response
from .parts import (
    Parts,
    AsyncParts,
    PartsWithRawResponse,
    AsyncPartsWithRawResponse,
    PartsWithStreamingResponse,
    AsyncPartsWithStreamingResponse,
)
from ...types import FilePurpose, upload_create_params, upload_complete_params
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import (
    maybe_transform,
    async_maybe_transform,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ..._base_client import make_request_options
from ...types.upload import Upload
from ...types.file_purpose import FilePurpose

__all__ = ["Uploads", "AsyncUploads"]


class Uploads(SyncAPIResource):
    @cached_property
    def parts(self) -> Parts:
        return Parts(self._client)

    @cached_property
    def with_raw_response(self) -> UploadsWithRawResponse:
        return UploadsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UploadsWithStreamingResponse:
        return UploadsWithStreamingResponse(self)

    def create(
        self,
        *,
        bytes: int,
        filename: str,
        mime_type: str,
        purpose: FilePurpose,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Upload:
        """
        Creates an intermediate
        [Upload](https://platform.openai.com/docs/api-reference/uploads/object) object
        that you can add
        [Parts](https://platform.openai.com/docs/api-reference/uploads/part-object) to.
        Currently, an Upload can accept at most 8 GB in total and expires after an hour
        after you create it.

        Once you complete the Upload, we will create a
        [File](https://platform.openai.com/docs/api-reference/files/object) object that
        contains all the parts you uploaded. This File is usable in the rest of our
        platform as a regular File object.

        For certain `purpose`s, the correct `mime_type` must be specified. Please refer
        to documentation for the supported MIME types for your use case:

        - [Assistants](https://platform.openai.com/docs/assistants/tools/file-search/supported-files)

        For guidance on the proper filename extensions for each purpose, please follow
        the documentation on
        [creating a File](https://platform.openai.com/docs/api-reference/files/create).

        Args:
          bytes: The number of bytes in the file you are uploading.

          filename: The name of the file to upload.

          mime_type: The MIME type of the file.

              This must fall within the supported MIME types for your file purpose. See the
              supported MIME types for assistants and vision.

          purpose: The intended purpose of the uploaded file.

              See the
              [documentation on File purposes](https://platform.openai.com/docs/api-reference/files/create#files-create-purpose).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/uploads",
            body=maybe_transform(
                {
                    "bytes": bytes,
                    "filename": filename,
                    "mime_type": mime_type,
                    "purpose": purpose,
                },
                upload_create_params.UploadCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Upload,
        )

    def cancel(
        self,
        upload_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Upload:
        """Cancels the Upload.

        No Parts may be added after an Upload is cancelled.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not upload_id:
            raise ValueError(f"Expected a non-empty value for `upload_id` but received {upload_id!r}")
        return self._post(
            f"/uploads/{upload_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Upload,
        )

    def complete(
        self,
        upload_id: str,
        *,
        part_ids: List[str],
        md5: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Upload:
        """
        Completes the
        [Upload](https://platform.openai.com/docs/api-reference/uploads/object).

        Within the returned Upload object, there is a nested
        [File](https://platform.openai.com/docs/api-reference/files/object) object that
        is ready to use in the rest of the platform.

        You can specify the order of the Parts by passing in an ordered list of the Part
        IDs.

        The number of bytes uploaded upon completion must match the number of bytes
        initially specified when creating the Upload object. No Parts may be added after
        an Upload is completed.

        Args:
          part_ids: The ordered list of Part IDs.

          md5: The optional md5 checksum for the file contents to verify if the bytes uploaded
              matches what you expect.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not upload_id:
            raise ValueError(f"Expected a non-empty value for `upload_id` but received {upload_id!r}")
        return self._post(
            f"/uploads/{upload_id}/complete",
            body=maybe_transform(
                {
                    "part_ids": part_ids,
                    "md5": md5,
                },
                upload_complete_params.UploadCompleteParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Upload,
        )


class AsyncUploads(AsyncAPIResource):
    @cached_property
    def parts(self) -> AsyncParts:
        return AsyncParts(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncUploadsWithRawResponse:
        return AsyncUploadsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUploadsWithStreamingResponse:
        return AsyncUploadsWithStreamingResponse(self)

    async def create(
        self,
        *,
        bytes: int,
        filename: str,
        mime_type: str,
        purpose: FilePurpose,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Upload:
        """
        Creates an intermediate
        [Upload](https://platform.openai.com/docs/api-reference/uploads/object) object
        that you can add
        [Parts](https://platform.openai.com/docs/api-reference/uploads/part-object) to.
        Currently, an Upload can accept at most 8 GB in total and expires after an hour
        after you create it.

        Once you complete the Upload, we will create a
        [File](https://platform.openai.com/docs/api-reference/files/object) object that
        contains all the parts you uploaded. This File is usable in the rest of our
        platform as a regular File object.

        For certain `purpose`s, the correct `mime_type` must be specified. Please refer
        to documentation for the supported MIME types for your use case:

        - [Assistants](https://platform.openai.com/docs/assistants/tools/file-search/supported-files)

        For guidance on the proper filename extensions for each purpose, please follow
        the documentation on
        [creating a File](https://platform.openai.com/docs/api-reference/files/create).

        Args:
          bytes: The number of bytes in the file you are uploading.

          filename: The name of the file to upload.

          mime_type: The MIME type of the file.

              This must fall within the supported MIME types for your file purpose. See the
              supported MIME types for assistants and vision.

          purpose: The intended purpose of the uploaded file.

              See the
              [documentation on File purposes](https://platform.openai.com/docs/api-reference/files/create#files-create-purpose).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/uploads",
            body=await async_maybe_transform(
                {
                    "bytes": bytes,
                    "filename": filename,
                    "mime_type": mime_type,
                    "purpose": purpose,
                },
                upload_create_params.UploadCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Upload,
        )

    async def cancel(
        self,
        upload_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Upload:
        """Cancels the Upload.

        No Parts may be added after an Upload is cancelled.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not upload_id:
            raise ValueError(f"Expected a non-empty value for `upload_id` but received {upload_id!r}")
        return await self._post(
            f"/uploads/{upload_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Upload,
        )

    async def complete(
        self,
        upload_id: str,
        *,
        part_ids: List[str],
        md5: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Upload:
        """
        Completes the
        [Upload](https://platform.openai.com/docs/api-reference/uploads/object).

        Within the returned Upload object, there is a nested
        [File](https://platform.openai.com/docs/api-reference/files/object) object that
        is ready to use in the rest of the platform.

        You can specify the order of the Parts by passing in an ordered list of the Part
        IDs.

        The number of bytes uploaded upon completion must match the number of bytes
        initially specified when creating the Upload object. No Parts may be added after
        an Upload is completed.

        Args:
          part_ids: The ordered list of Part IDs.

          md5: The optional md5 checksum for the file contents to verify if the bytes uploaded
              matches what you expect.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not upload_id:
            raise ValueError(f"Expected a non-empty value for `upload_id` but received {upload_id!r}")
        return await self._post(
            f"/uploads/{upload_id}/complete",
            body=await async_maybe_transform(
                {
                    "part_ids": part_ids,
                    "md5": md5,
                },
                upload_complete_params.UploadCompleteParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Upload,
        )


class UploadsWithRawResponse:
    def __init__(self, uploads: Uploads) -> None:
        self._uploads = uploads

        self.create = _legacy_response.to_raw_response_wrapper(
            uploads.create,
        )
        self.cancel = _legacy_response.to_raw_response_wrapper(
            uploads.cancel,
        )
        self.complete = _legacy_response.to_raw_response_wrapper(
            uploads.complete,
        )

    @cached_property
    def parts(self) -> PartsWithRawResponse:
        return PartsWithRawResponse(self._uploads.parts)


class AsyncUploadsWithRawResponse:
    def __init__(self, uploads: AsyncUploads) -> None:
        self._uploads = uploads

        self.create = _legacy_response.async_to_raw_response_wrapper(
            uploads.create,
        )
        self.cancel = _legacy_response.async_to_raw_response_wrapper(
            uploads.cancel,
        )
        self.complete = _legacy_response.async_to_raw_response_wrapper(
            uploads.complete,
        )

    @cached_property
    def parts(self) -> AsyncPartsWithRawResponse:
        return AsyncPartsWithRawResponse(self._uploads.parts)


class UploadsWithStreamingResponse:
    def __init__(self, uploads: Uploads) -> None:
        self._uploads = uploads

        self.create = to_streamed_response_wrapper(
            uploads.create,
        )
        self.cancel = to_streamed_response_wrapper(
            uploads.cancel,
        )
        self.complete = to_streamed_response_wrapper(
            uploads.complete,
        )

    @cached_property
    def parts(self) -> PartsWithStreamingResponse:
        return PartsWithStreamingResponse(self._uploads.parts)


class AsyncUploadsWithStreamingResponse:
    def __init__(self, uploads: AsyncUploads) -> None:
        self._uploads = uploads

        self.create = async_to_streamed_response_wrapper(
            uploads.create,
        )
        self.cancel = async_to_streamed_response_wrapper(
            uploads.cancel,
        )
        self.complete = async_to_streamed_response_wrapper(
            uploads.complete,
        )

    @cached_property
    def parts(self) -> AsyncPartsWithStreamingResponse:
        return AsyncPartsWithStreamingResponse(self._uploads.parts)
