# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import TYPE_CHECKING, Mapping, Optional, cast
from typing_extensions import Literal

from ..types import (
    ImagesResponse,
    image_edit_params,
    image_generate_params,
    image_create_variation_params,
)
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven, FileTypes
from .._utils import extract_files, maybe_transform, deepcopy_minimal
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import to_raw_response_wrapper, async_to_raw_response_wrapper
from .._base_client import make_request_options

if TYPE_CHECKING:
    from .._client import OpenAI, AsyncOpenAI

__all__ = ["Images", "AsyncImages"]


class Images(SyncAPIResource):
    with_raw_response: ImagesWithRawResponse

    def __init__(self, client: OpenAI) -> None:
        super().__init__(client)
        self.with_raw_response = ImagesWithRawResponse(self)

    def create_variation(
        self,
        *,
        image: FileTypes,
        n: Optional[int] | NotGiven = NOT_GIVEN,
        response_format: Optional[Literal["url", "b64_json"]] | NotGiven = NOT_GIVEN,
        size: Optional[Literal["256x256", "512x512", "1024x1024"]] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ImagesResponse:
        """
        Creates a variation of a given image.

        Args:
          image: The image to use as the basis for the variation(s). Must be a valid PNG file,
              less than 4MB, and square.

          n: The number of images to generate. Must be between 1 and 10.

          response_format: The format in which the generated images are returned. Must be one of `url` or
              `b64_json`.

          size: The size of the generated images. Must be one of `256x256`, `512x512`, or
              `1024x1024`.

          user: A unique identifier representing your end-user, which can help OpenAI to monitor
              and detect abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices/end-user-ids).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "image": image,
                "n": n,
                "response_format": response_format,
                "size": size,
                "user": user,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["image"]])
        if files:
            # It should be noted that the actual Content-Type header that will be
            # sent to the server will contain a `boundary` parameter, e.g.
            # multipart/form-data; boundary=---abc--
            extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}

        return self._post(
            "/images/variations",
            body=maybe_transform(body, image_create_variation_params.ImageCreateVariationParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ImagesResponse,
        )

    def edit(
        self,
        *,
        image: FileTypes,
        prompt: str,
        mask: FileTypes | NotGiven = NOT_GIVEN,
        n: Optional[int] | NotGiven = NOT_GIVEN,
        response_format: Optional[Literal["url", "b64_json"]] | NotGiven = NOT_GIVEN,
        size: Optional[Literal["256x256", "512x512", "1024x1024"]] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ImagesResponse:
        """
        Creates an edited or extended image given an original image and a prompt.

        Args:
          image: The image to edit. Must be a valid PNG file, less than 4MB, and square. If mask
              is not provided, image must have transparency, which will be used as the mask.

          prompt: A text description of the desired image(s). The maximum length is 1000
              characters.

          mask: An additional image whose fully transparent areas (e.g. where alpha is zero)
              indicate where `image` should be edited. Must be a valid PNG file, less than
              4MB, and have the same dimensions as `image`.

          n: The number of images to generate. Must be between 1 and 10.

          response_format: The format in which the generated images are returned. Must be one of `url` or
              `b64_json`.

          size: The size of the generated images. Must be one of `256x256`, `512x512`, or
              `1024x1024`.

          user: A unique identifier representing your end-user, which can help OpenAI to monitor
              and detect abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices/end-user-ids).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "image": image,
                "prompt": prompt,
                "mask": mask,
                "n": n,
                "response_format": response_format,
                "size": size,
                "user": user,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["image"], ["mask"]])
        if files:
            # It should be noted that the actual Content-Type header that will be
            # sent to the server will contain a `boundary` parameter, e.g.
            # multipart/form-data; boundary=---abc--
            extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}

        return self._post(
            "/images/edits",
            body=maybe_transform(body, image_edit_params.ImageEditParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ImagesResponse,
        )

    def generate(
        self,
        *,
        prompt: str,
        n: Optional[int] | NotGiven = NOT_GIVEN,
        response_format: Optional[Literal["url", "b64_json"]] | NotGiven = NOT_GIVEN,
        size: Optional[Literal["256x256", "512x512", "1024x1024"]] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ImagesResponse:
        """
        Creates an image given a prompt.

        Args:
          prompt: A text description of the desired image(s). The maximum length is 1000
              characters.

          n: The number of images to generate. Must be between 1 and 10.

          response_format: The format in which the generated images are returned. Must be one of `url` or
              `b64_json`.

          size: The size of the generated images. Must be one of `256x256`, `512x512`, or
              `1024x1024`.

          user: A unique identifier representing your end-user, which can help OpenAI to monitor
              and detect abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices/end-user-ids).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/images/generations",
            body=maybe_transform(
                {
                    "prompt": prompt,
                    "n": n,
                    "response_format": response_format,
                    "size": size,
                    "user": user,
                },
                image_generate_params.ImageGenerateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ImagesResponse,
        )


class AsyncImages(AsyncAPIResource):
    with_raw_response: AsyncImagesWithRawResponse

    def __init__(self, client: AsyncOpenAI) -> None:
        super().__init__(client)
        self.with_raw_response = AsyncImagesWithRawResponse(self)

    async def create_variation(
        self,
        *,
        image: FileTypes,
        n: Optional[int] | NotGiven = NOT_GIVEN,
        response_format: Optional[Literal["url", "b64_json"]] | NotGiven = NOT_GIVEN,
        size: Optional[Literal["256x256", "512x512", "1024x1024"]] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ImagesResponse:
        """
        Creates a variation of a given image.

        Args:
          image: The image to use as the basis for the variation(s). Must be a valid PNG file,
              less than 4MB, and square.

          n: The number of images to generate. Must be between 1 and 10.

          response_format: The format in which the generated images are returned. Must be one of `url` or
              `b64_json`.

          size: The size of the generated images. Must be one of `256x256`, `512x512`, or
              `1024x1024`.

          user: A unique identifier representing your end-user, which can help OpenAI to monitor
              and detect abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices/end-user-ids).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "image": image,
                "n": n,
                "response_format": response_format,
                "size": size,
                "user": user,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["image"]])
        if files:
            # It should be noted that the actual Content-Type header that will be
            # sent to the server will contain a `boundary` parameter, e.g.
            # multipart/form-data; boundary=---abc--
            extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}

        return await self._post(
            "/images/variations",
            body=maybe_transform(body, image_create_variation_params.ImageCreateVariationParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ImagesResponse,
        )

    async def edit(
        self,
        *,
        image: FileTypes,
        prompt: str,
        mask: FileTypes | NotGiven = NOT_GIVEN,
        n: Optional[int] | NotGiven = NOT_GIVEN,
        response_format: Optional[Literal["url", "b64_json"]] | NotGiven = NOT_GIVEN,
        size: Optional[Literal["256x256", "512x512", "1024x1024"]] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ImagesResponse:
        """
        Creates an edited or extended image given an original image and a prompt.

        Args:
          image: The image to edit. Must be a valid PNG file, less than 4MB, and square. If mask
              is not provided, image must have transparency, which will be used as the mask.

          prompt: A text description of the desired image(s). The maximum length is 1000
              characters.

          mask: An additional image whose fully transparent areas (e.g. where alpha is zero)
              indicate where `image` should be edited. Must be a valid PNG file, less than
              4MB, and have the same dimensions as `image`.

          n: The number of images to generate. Must be between 1 and 10.

          response_format: The format in which the generated images are returned. Must be one of `url` or
              `b64_json`.

          size: The size of the generated images. Must be one of `256x256`, `512x512`, or
              `1024x1024`.

          user: A unique identifier representing your end-user, which can help OpenAI to monitor
              and detect abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices/end-user-ids).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "image": image,
                "prompt": prompt,
                "mask": mask,
                "n": n,
                "response_format": response_format,
                "size": size,
                "user": user,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["image"], ["mask"]])
        if files:
            # It should be noted that the actual Content-Type header that will be
            # sent to the server will contain a `boundary` parameter, e.g.
            # multipart/form-data; boundary=---abc--
            extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}

        return await self._post(
            "/images/edits",
            body=maybe_transform(body, image_edit_params.ImageEditParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ImagesResponse,
        )

    async def generate(
        self,
        *,
        prompt: str,
        n: Optional[int] | NotGiven = NOT_GIVEN,
        response_format: Optional[Literal["url", "b64_json"]] | NotGiven = NOT_GIVEN,
        size: Optional[Literal["256x256", "512x512", "1024x1024"]] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> ImagesResponse:
        """
        Creates an image given a prompt.

        Args:
          prompt: A text description of the desired image(s). The maximum length is 1000
              characters.

          n: The number of images to generate. Must be between 1 and 10.

          response_format: The format in which the generated images are returned. Must be one of `url` or
              `b64_json`.

          size: The size of the generated images. Must be one of `256x256`, `512x512`, or
              `1024x1024`.

          user: A unique identifier representing your end-user, which can help OpenAI to monitor
              and detect abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices/end-user-ids).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/images/generations",
            body=maybe_transform(
                {
                    "prompt": prompt,
                    "n": n,
                    "response_format": response_format,
                    "size": size,
                    "user": user,
                },
                image_generate_params.ImageGenerateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ImagesResponse,
        )


class ImagesWithRawResponse:
    def __init__(self, images: Images) -> None:
        self.create_variation = to_raw_response_wrapper(
            images.create_variation,
        )
        self.edit = to_raw_response_wrapper(
            images.edit,
        )
        self.generate = to_raw_response_wrapper(
            images.generate,
        )


class AsyncImagesWithRawResponse:
    def __init__(self, images: AsyncImages) -> None:
        self.create_variation = async_to_raw_response_wrapper(
            images.create_variation,
        )
        self.edit = async_to_raw_response_wrapper(
            images.edit,
        )
        self.generate = async_to_raw_response_wrapper(
            images.generate,
        )
