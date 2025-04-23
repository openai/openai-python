# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Mapping, Optional, cast
from typing_extensions import Literal

import httpx

from .. import _legacy_response
from ..types import image_edit_params, image_generate_params, image_create_variation_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven, FileTypes
from .._utils import extract_files, maybe_transform, deepcopy_minimal, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from .._base_client import make_request_options
from ..types.image_model import ImageModel
from ..types.images_response import ImagesResponse

__all__ = ["Images", "AsyncImages"]


class Images(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ImagesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return ImagesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ImagesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return ImagesWithStreamingResponse(self)

    def create_variation(
        self,
        *,
        image: FileTypes,
        model: Union[str, ImageModel, None] | NotGiven = NOT_GIVEN,
        n: Optional[int] | NotGiven = NOT_GIVEN,
        response_format: Optional[Literal["url", "b64_json"]] | NotGiven = NOT_GIVEN,
        size: Optional[Literal["256x256", "512x512", "1024x1024"]] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ImagesResponse:
        """Creates a variation of a given image.

        This endpoint only supports `dall-e-2`.

        Args:
          image: The image to use as the basis for the variation(s). Must be a valid PNG file,
              less than 4MB, and square.

          model: The model to use for image generation. Only `dall-e-2` is supported at this
              time.

          n: The number of images to generate. Must be between 1 and 10.

          response_format: The format in which the generated images are returned. Must be one of `url` or
              `b64_json`. URLs are only valid for 60 minutes after the image has been
              generated.

          size: The size of the generated images. Must be one of `256x256`, `512x512`, or
              `1024x1024`.

          user: A unique identifier representing your end-user, which can help OpenAI to monitor
              and detect abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#end-user-ids).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "image": image,
                "model": model,
                "n": n,
                "response_format": response_format,
                "size": size,
                "user": user,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["image"]])
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
        image: Union[FileTypes, List[FileTypes]],
        prompt: str,
        mask: FileTypes | NotGiven = NOT_GIVEN,
        model: Union[str, ImageModel, None] | NotGiven = NOT_GIVEN,
        n: Optional[int] | NotGiven = NOT_GIVEN,
        quality: Optional[Literal["standard", "low", "medium", "high", "auto"]] | NotGiven = NOT_GIVEN,
        response_format: Optional[Literal["url", "b64_json"]] | NotGiven = NOT_GIVEN,
        size: Optional[Literal["256x256", "512x512", "1024x1024"]] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ImagesResponse:
        """Creates an edited or extended image given one or more source images and a
        prompt.

        This endpoint only supports `gpt-image-1` and `dall-e-2`.

        Args:
          image: The image(s) to edit. Must be a supported image file or an array of images. For
              `gpt-image-1`, each image should be a `png`, `webp`, or `jpg` file less than
              25MB. For `dall-e-2`, you can only provide one image, and it should be a square
              `png` file less than 4MB.

          prompt: A text description of the desired image(s). The maximum length is 1000
              characters for `dall-e-2`, and 32000 characters for `gpt-image-1`.

          mask: An additional image whose fully transparent areas (e.g. where alpha is zero)
              indicate where `image` should be edited. If there are multiple images provided,
              the mask will be applied on the first image. Must be a valid PNG file, less than
              4MB, and have the same dimensions as `image`.

          model: The model to use for image generation. Only `dall-e-2` and `gpt-image-1` are
              supported. Defaults to `dall-e-2` unless a parameter specific to `gpt-image-1`
              is used.

          n: The number of images to generate. Must be between 1 and 10.

          quality: The quality of the image that will be generated. `high`, `medium` and `low` are
              only supported for `gpt-image-1`. `dall-e-2` only supports `standard` quality.
              Defaults to `auto`.

          response_format: The format in which the generated images are returned. Must be one of `url` or
              `b64_json`. URLs are only valid for 60 minutes after the image has been
              generated. This parameter is only supported for `dall-e-2`, as `gpt-image-1`
              will always return base64-encoded images.

          size: The size of the generated images. Must be one of `1024x1024`, `1536x1024`
              (landscape), `1024x1536` (portrait), or `auto` (default value) for
              `gpt-image-1`, and one of `256x256`, `512x512`, or `1024x1024` for `dall-e-2`.

          user: A unique identifier representing your end-user, which can help OpenAI to monitor
              and detect abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#end-user-ids).

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
                "model": model,
                "n": n,
                "quality": quality,
                "response_format": response_format,
                "size": size,
                "user": user,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["image"], ["image", "<array>"], ["mask"]])
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
        background: Optional[Literal["transparent", "opaque", "auto"]] | NotGiven = NOT_GIVEN,
        model: Union[str, ImageModel, None] | NotGiven = NOT_GIVEN,
        moderation: Optional[Literal["low", "auto"]] | NotGiven = NOT_GIVEN,
        n: Optional[int] | NotGiven = NOT_GIVEN,
        output_compression: Optional[int] | NotGiven = NOT_GIVEN,
        output_format: Optional[Literal["png", "jpeg", "webp"]] | NotGiven = NOT_GIVEN,
        quality: Optional[Literal["standard", "hd", "low", "medium", "high", "auto"]] | NotGiven = NOT_GIVEN,
        response_format: Optional[Literal["url", "b64_json"]] | NotGiven = NOT_GIVEN,
        size: Optional[
            Literal["auto", "1024x1024", "1536x1024", "1024x1536", "256x256", "512x512", "1792x1024", "1024x1792"]
        ]
        | NotGiven = NOT_GIVEN,
        style: Optional[Literal["vivid", "natural"]] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ImagesResponse:
        """
        Creates an image given a prompt.
        [Learn more](https://platform.openai.com/docs/guides/images).

        Args:
          prompt: A text description of the desired image(s). The maximum length is 32000
              characters for `gpt-image-1`, 1000 characters for `dall-e-2` and 4000 characters
              for `dall-e-3`.

          background: Allows to set transparency for the background of the generated image(s). This
              parameter is only supported for `gpt-image-1`. Must be one of `transparent`,
              `opaque` or `auto` (default value). When `auto` is used, the model will
              automatically determine the best background for the image.

              If `transparent`, the output format needs to support transparency, so it should
              be set to either `png` (default value) or `webp`.

          model: The model to use for image generation. One of `dall-e-2`, `dall-e-3`, or
              `gpt-image-1`. Defaults to `dall-e-2` unless a parameter specific to
              `gpt-image-1` is used.

          moderation: Control the content-moderation level for images generated by `gpt-image-1`. Must
              be either `low` for less restrictive filtering or `auto` (default value).

          n: The number of images to generate. Must be between 1 and 10. For `dall-e-3`, only
              `n=1` is supported.

          output_compression: The compression level (0-100%) for the generated images. This parameter is only
              supported for `gpt-image-1` with the `webp` or `jpeg` output formats, and
              defaults to 100.

          output_format: The format in which the generated images are returned. This parameter is only
              supported for `gpt-image-1`. Must be one of `png`, `jpeg`, or `webp`.

          quality: The quality of the image that will be generated.

              - `auto` (default value) will automatically select the best quality for the
                given model.
              - `high`, `medium` and `low` are supported for `gpt-image-1`.
              - `hd` and `standard` are supported for `dall-e-3`.
              - `standard` is the only option for `dall-e-2`.

          response_format: The format in which generated images with `dall-e-2` and `dall-e-3` are
              returned. Must be one of `url` or `b64_json`. URLs are only valid for 60 minutes
              after the image has been generated. This parameter isn't supported for
              `gpt-image-1` which will always return base64-encoded images.

          size: The size of the generated images. Must be one of `1024x1024`, `1536x1024`
              (landscape), `1024x1536` (portrait), or `auto` (default value) for
              `gpt-image-1`, one of `256x256`, `512x512`, or `1024x1024` for `dall-e-2`, and
              one of `1024x1024`, `1792x1024`, or `1024x1792` for `dall-e-3`.

          style: The style of the generated images. This parameter is only supported for
              `dall-e-3`. Must be one of `vivid` or `natural`. Vivid causes the model to lean
              towards generating hyper-real and dramatic images. Natural causes the model to
              produce more natural, less hyper-real looking images.

          user: A unique identifier representing your end-user, which can help OpenAI to monitor
              and detect abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#end-user-ids).

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
                    "background": background,
                    "model": model,
                    "moderation": moderation,
                    "n": n,
                    "output_compression": output_compression,
                    "output_format": output_format,
                    "quality": quality,
                    "response_format": response_format,
                    "size": size,
                    "style": style,
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
    @cached_property
    def with_raw_response(self) -> AsyncImagesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncImagesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncImagesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncImagesWithStreamingResponse(self)

    async def create_variation(
        self,
        *,
        image: FileTypes,
        model: Union[str, ImageModel, None] | NotGiven = NOT_GIVEN,
        n: Optional[int] | NotGiven = NOT_GIVEN,
        response_format: Optional[Literal["url", "b64_json"]] | NotGiven = NOT_GIVEN,
        size: Optional[Literal["256x256", "512x512", "1024x1024"]] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ImagesResponse:
        """Creates a variation of a given image.

        This endpoint only supports `dall-e-2`.

        Args:
          image: The image to use as the basis for the variation(s). Must be a valid PNG file,
              less than 4MB, and square.

          model: The model to use for image generation. Only `dall-e-2` is supported at this
              time.

          n: The number of images to generate. Must be between 1 and 10.

          response_format: The format in which the generated images are returned. Must be one of `url` or
              `b64_json`. URLs are only valid for 60 minutes after the image has been
              generated.

          size: The size of the generated images. Must be one of `256x256`, `512x512`, or
              `1024x1024`.

          user: A unique identifier representing your end-user, which can help OpenAI to monitor
              and detect abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#end-user-ids).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "image": image,
                "model": model,
                "n": n,
                "response_format": response_format,
                "size": size,
                "user": user,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["image"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/images/variations",
            body=await async_maybe_transform(body, image_create_variation_params.ImageCreateVariationParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ImagesResponse,
        )

    async def edit(
        self,
        *,
        image: Union[FileTypes, List[FileTypes]],
        prompt: str,
        mask: FileTypes | NotGiven = NOT_GIVEN,
        model: Union[str, ImageModel, None] | NotGiven = NOT_GIVEN,
        n: Optional[int] | NotGiven = NOT_GIVEN,
        quality: Optional[Literal["standard", "low", "medium", "high", "auto"]] | NotGiven = NOT_GIVEN,
        response_format: Optional[Literal["url", "b64_json"]] | NotGiven = NOT_GIVEN,
        size: Optional[Literal["256x256", "512x512", "1024x1024"]] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ImagesResponse:
        """Creates an edited or extended image given one or more source images and a
        prompt.

        This endpoint only supports `gpt-image-1` and `dall-e-2`.

        Args:
          image: The image(s) to edit. Must be a supported image file or an array of images. For
              `gpt-image-1`, each image should be a `png`, `webp`, or `jpg` file less than
              25MB. For `dall-e-2`, you can only provide one image, and it should be a square
              `png` file less than 4MB.

          prompt: A text description of the desired image(s). The maximum length is 1000
              characters for `dall-e-2`, and 32000 characters for `gpt-image-1`.

          mask: An additional image whose fully transparent areas (e.g. where alpha is zero)
              indicate where `image` should be edited. If there are multiple images provided,
              the mask will be applied on the first image. Must be a valid PNG file, less than
              4MB, and have the same dimensions as `image`.

          model: The model to use for image generation. Only `dall-e-2` and `gpt-image-1` are
              supported. Defaults to `dall-e-2` unless a parameter specific to `gpt-image-1`
              is used.

          n: The number of images to generate. Must be between 1 and 10.

          quality: The quality of the image that will be generated. `high`, `medium` and `low` are
              only supported for `gpt-image-1`. `dall-e-2` only supports `standard` quality.
              Defaults to `auto`.

          response_format: The format in which the generated images are returned. Must be one of `url` or
              `b64_json`. URLs are only valid for 60 minutes after the image has been
              generated. This parameter is only supported for `dall-e-2`, as `gpt-image-1`
              will always return base64-encoded images.

          size: The size of the generated images. Must be one of `1024x1024`, `1536x1024`
              (landscape), `1024x1536` (portrait), or `auto` (default value) for
              `gpt-image-1`, and one of `256x256`, `512x512`, or `1024x1024` for `dall-e-2`.

          user: A unique identifier representing your end-user, which can help OpenAI to monitor
              and detect abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#end-user-ids).

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
                "model": model,
                "n": n,
                "quality": quality,
                "response_format": response_format,
                "size": size,
                "user": user,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["image"], ["image", "<array>"], ["mask"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/images/edits",
            body=await async_maybe_transform(body, image_edit_params.ImageEditParams),
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
        background: Optional[Literal["transparent", "opaque", "auto"]] | NotGiven = NOT_GIVEN,
        model: Union[str, ImageModel, None] | NotGiven = NOT_GIVEN,
        moderation: Optional[Literal["low", "auto"]] | NotGiven = NOT_GIVEN,
        n: Optional[int] | NotGiven = NOT_GIVEN,
        output_compression: Optional[int] | NotGiven = NOT_GIVEN,
        output_format: Optional[Literal["png", "jpeg", "webp"]] | NotGiven = NOT_GIVEN,
        quality: Optional[Literal["standard", "hd", "low", "medium", "high", "auto"]] | NotGiven = NOT_GIVEN,
        response_format: Optional[Literal["url", "b64_json"]] | NotGiven = NOT_GIVEN,
        size: Optional[
            Literal["auto", "1024x1024", "1536x1024", "1024x1536", "256x256", "512x512", "1792x1024", "1024x1792"]
        ]
        | NotGiven = NOT_GIVEN,
        style: Optional[Literal["vivid", "natural"]] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ImagesResponse:
        """
        Creates an image given a prompt.
        [Learn more](https://platform.openai.com/docs/guides/images).

        Args:
          prompt: A text description of the desired image(s). The maximum length is 32000
              characters for `gpt-image-1`, 1000 characters for `dall-e-2` and 4000 characters
              for `dall-e-3`.

          background: Allows to set transparency for the background of the generated image(s). This
              parameter is only supported for `gpt-image-1`. Must be one of `transparent`,
              `opaque` or `auto` (default value). When `auto` is used, the model will
              automatically determine the best background for the image.

              If `transparent`, the output format needs to support transparency, so it should
              be set to either `png` (default value) or `webp`.

          model: The model to use for image generation. One of `dall-e-2`, `dall-e-3`, or
              `gpt-image-1`. Defaults to `dall-e-2` unless a parameter specific to
              `gpt-image-1` is used.

          moderation: Control the content-moderation level for images generated by `gpt-image-1`. Must
              be either `low` for less restrictive filtering or `auto` (default value).

          n: The number of images to generate. Must be between 1 and 10. For `dall-e-3`, only
              `n=1` is supported.

          output_compression: The compression level (0-100%) for the generated images. This parameter is only
              supported for `gpt-image-1` with the `webp` or `jpeg` output formats, and
              defaults to 100.

          output_format: The format in which the generated images are returned. This parameter is only
              supported for `gpt-image-1`. Must be one of `png`, `jpeg`, or `webp`.

          quality: The quality of the image that will be generated.

              - `auto` (default value) will automatically select the best quality for the
                given model.
              - `high`, `medium` and `low` are supported for `gpt-image-1`.
              - `hd` and `standard` are supported for `dall-e-3`.
              - `standard` is the only option for `dall-e-2`.

          response_format: The format in which generated images with `dall-e-2` and `dall-e-3` are
              returned. Must be one of `url` or `b64_json`. URLs are only valid for 60 minutes
              after the image has been generated. This parameter isn't supported for
              `gpt-image-1` which will always return base64-encoded images.

          size: The size of the generated images. Must be one of `1024x1024`, `1536x1024`
              (landscape), `1024x1536` (portrait), or `auto` (default value) for
              `gpt-image-1`, one of `256x256`, `512x512`, or `1024x1024` for `dall-e-2`, and
              one of `1024x1024`, `1792x1024`, or `1024x1792` for `dall-e-3`.

          style: The style of the generated images. This parameter is only supported for
              `dall-e-3`. Must be one of `vivid` or `natural`. Vivid causes the model to lean
              towards generating hyper-real and dramatic images. Natural causes the model to
              produce more natural, less hyper-real looking images.

          user: A unique identifier representing your end-user, which can help OpenAI to monitor
              and detect abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#end-user-ids).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/images/generations",
            body=await async_maybe_transform(
                {
                    "prompt": prompt,
                    "background": background,
                    "model": model,
                    "moderation": moderation,
                    "n": n,
                    "output_compression": output_compression,
                    "output_format": output_format,
                    "quality": quality,
                    "response_format": response_format,
                    "size": size,
                    "style": style,
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
        self._images = images

        self.create_variation = _legacy_response.to_raw_response_wrapper(
            images.create_variation,
        )
        self.edit = _legacy_response.to_raw_response_wrapper(
            images.edit,
        )
        self.generate = _legacy_response.to_raw_response_wrapper(
            images.generate,
        )


class AsyncImagesWithRawResponse:
    def __init__(self, images: AsyncImages) -> None:
        self._images = images

        self.create_variation = _legacy_response.async_to_raw_response_wrapper(
            images.create_variation,
        )
        self.edit = _legacy_response.async_to_raw_response_wrapper(
            images.edit,
        )
        self.generate = _legacy_response.async_to_raw_response_wrapper(
            images.generate,
        )


class ImagesWithStreamingResponse:
    def __init__(self, images: Images) -> None:
        self._images = images

        self.create_variation = to_streamed_response_wrapper(
            images.create_variation,
        )
        self.edit = to_streamed_response_wrapper(
            images.edit,
        )
        self.generate = to_streamed_response_wrapper(
            images.generate,
        )


class AsyncImagesWithStreamingResponse:
    def __init__(self, images: AsyncImages) -> None:
        self._images = images

        self.create_variation = async_to_streamed_response_wrapper(
            images.create_variation,
        )
        self.edit = async_to_streamed_response_wrapper(
            images.edit,
        )
        self.generate = async_to_streamed_response_wrapper(
            images.generate,
        )
