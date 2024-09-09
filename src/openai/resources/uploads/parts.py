# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Mapping, cast

import httpx

from ... import _legacy_response
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven, FileTypes
from ..._utils import (
    extract_files,
    maybe_transform,
    deepcopy_minimal,
    async_maybe_transform,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ..._base_client import make_request_options
from ...types.uploads import part_create_params
from ...types.uploads.upload_part import UploadPart

__all__ = ["Parts", "AsyncParts"]


class Parts(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PartsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return PartsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PartsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return PartsWithStreamingResponse(self)

    def create(
        self,
        upload_id: str,
        *,
        data: FileTypes,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UploadPart:
        """
        Adds a
        [Part](https://platform.openai.com/docs/api-reference/uploads/part-object) to an
        [Upload](https://platform.openai.com/docs/api-reference/uploads/object) object.
        A Part represents a chunk of bytes from the file you are trying to upload.

        Each Part can be at most 64 MB, and you can add Parts until you hit the Upload
        maximum of 8 GB.

        It is possible to add multiple Parts in parallel. You can decide the intended
        order of the Parts when you
        [complete the Upload](https://platform.openai.com/docs/api-reference/uploads/complete).

        Args:
          data: The chunk of bytes for this Part.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not upload_id:
            raise ValueError(f"Expected a non-empty value for `upload_id` but received {upload_id!r}")
        body = deepcopy_minimal({"data": data})
        files = extract_files(cast(Mapping[str, object], body), paths=[["data"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            f"/uploads/{upload_id}/parts",
            body=maybe_transform(body, part_create_params.PartCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UploadPart,
        )


class AsyncParts(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPartsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPartsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPartsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncPartsWithStreamingResponse(self)

    async def create(
        self,
        upload_id: str,
        *,
        data: FileTypes,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UploadPart:
        """
        Adds a
        [Part](https://platform.openai.com/docs/api-reference/uploads/part-object) to an
        [Upload](https://platform.openai.com/docs/api-reference/uploads/object) object.
        A Part represents a chunk of bytes from the file you are trying to upload.

        Each Part can be at most 64 MB, and you can add Parts until you hit the Upload
        maximum of 8 GB.

        It is possible to add multiple Parts in parallel. You can decide the intended
        order of the Parts when you
        [complete the Upload](https://platform.openai.com/docs/api-reference/uploads/complete).

        Args:
          data: The chunk of bytes for this Part.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not upload_id:
            raise ValueError(f"Expected a non-empty value for `upload_id` but received {upload_id!r}")
        body = deepcopy_minimal({"data": data})
        files = extract_files(cast(Mapping[str, object], body), paths=[["data"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            f"/uploads/{upload_id}/parts",
            body=await async_maybe_transform(body, part_create_params.PartCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UploadPart,
        )


class PartsWithRawResponse:
    def __init__(self, parts: Parts) -> None:
        self._parts = parts

        self.create = _legacy_response.to_raw_response_wrapper(
            parts.create,
        )


class AsyncPartsWithRawResponse:
    def __init__(self, parts: AsyncParts) -> None:
        self._parts = parts

        self.create = _legacy_response.async_to_raw_response_wrapper(
            parts.create,
        )


class PartsWithStreamingResponse:
    def __init__(self, parts: Parts) -> None:
        self._parts = parts

        self.create = to_streamed_response_wrapper(
            parts.create,
        )


class AsyncPartsWithStreamingResponse:
    def __init__(self, parts: AsyncParts) -> None:
        self._parts = parts

        self.create = async_to_streamed_response_wrapper(
            parts.create,
        )
