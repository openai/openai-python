# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import TYPE_CHECKING, Mapping, cast
from typing_extensions import Literal, assert_never

import httpx

from .. import _legacy_response
from ..types import (
    VideoSize,
    VideoSeconds,
    video_edit_params,
    video_list_params,
    video_remix_params,
    video_create_params,
    video_extend_params,
    video_create_character_params,
    video_download_content_params,
)
from .._files import deepcopy_with_paths
from .._types import Body, Omit, Query, Headers, NotGiven, FileTypes, omit, not_given
from .._utils import extract_files, path_template, maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
    to_streamed_response_wrapper,
    async_to_streamed_response_wrapper,
    to_custom_streamed_response_wrapper,
    async_to_custom_streamed_response_wrapper,
)
from ..pagination import SyncConversationCursorPage, AsyncConversationCursorPage
from ..types.video import Video
from .._base_client import AsyncPaginator, make_request_options
from .._utils._utils import is_given
from ..types.video_size import VideoSize
from ..types.video_seconds import VideoSeconds
from ..types.video_model_param import VideoModelParam
from ..types.video_delete_response import VideoDeleteResponse
from ..types.video_get_character_response import VideoGetCharacterResponse
from ..types.video_create_character_response import VideoCreateCharacterResponse

__all__ = ["Videos", "AsyncVideos"]


class Videos(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> VideosWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return VideosWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> VideosWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return VideosWithStreamingResponse(self)

    def create(
        self,
        *,
        prompt: str,
        input_reference: video_create_params.InputReference | Omit = omit,
        model: VideoModelParam | Omit = omit,
        seconds: VideoSeconds | Omit = omit,
        size: VideoSize | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Video:
        """
        Create a new video generation job from a prompt and optional reference assets.

        Args:
          prompt: Text prompt that describes the video to generate.

          input_reference: Optional reference asset upload or reference object that guides generation.

          model: The video generation model to use (allowed values: sora-2, sora-2-pro). Defaults
              to `sora-2`.

          seconds: Clip duration in seconds (allowed values: 4, 8, 12). Defaults to 4 seconds.

          size: Output resolution formatted as width x height (allowed values: 720x1280,
              1280x720, 1024x1792, 1792x1024). Defaults to 720x1280.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_with_paths(
            {
                "prompt": prompt,
                "input_reference": input_reference,
                "model": model,
                "seconds": seconds,
                "size": size,
            },
            [["input_reference"]],
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["input_reference"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/videos",
            body=maybe_transform(body, video_create_params.VideoCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Video,
        )

    def create_and_poll(
        self,
        *,
        prompt: str,
        input_reference: video_create_params.InputReference | Omit = omit,
        model: VideoModelParam | Omit = omit,
        seconds: VideoSeconds | Omit = omit,
        size: VideoSize | Omit = omit,
        poll_interval_ms: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Video:
        """Create a video and wait for it to be processed."""
        video = self.create(
            model=model,
            prompt=prompt,
            input_reference=input_reference,
            seconds=seconds,
            size=size,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )

        return self.poll(
            video.id,
            poll_interval_ms=poll_interval_ms,
        )

    def poll(
        self,
        video_id: str,
        *,
        poll_interval_ms: int | Omit = omit,
    ) -> Video:
        """Wait for the vector store file to finish processing.

        Note: this will return even if the file failed to process, you need to check
        file.last_error and file.status to handle these cases
        """
        headers: dict[str, str] = {"X-Stainless-Poll-Helper": "true"}
        if is_given(poll_interval_ms):
            headers["X-Stainless-Custom-Poll-Interval"] = str(poll_interval_ms)

        while True:
            response = self.with_raw_response.retrieve(
                video_id,
                extra_headers=headers,
            )

            video = response.parse()
            if video.status == "in_progress" or video.status == "queued":
                if not is_given(poll_interval_ms):
                    from_header = response.headers.get("openai-poll-after-ms")
                    if from_header is not None:
                        poll_interval_ms = int(from_header)
                    else:
                        poll_interval_ms = 1000

                self._sleep(poll_interval_ms / 1000)
            elif video.status == "completed" or video.status == "failed":
                return video
            else:
                if TYPE_CHECKING:  # type: ignore[unreachable]
                    assert_never(video.status)
                else:
                    return video

    def retrieve(
        self,
        video_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Video:
        """
        Fetch the latest metadata for a generated video.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not video_id:
            raise ValueError(f"Expected a non-empty value for `video_id` but received {video_id!r}")
        return self._get(
            path_template("/videos/{video_id}", video_id=video_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Video,
        )

    def list(
        self,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncConversationCursorPage[Video]:
        """
        List recently generated videos for the current project.

        Args:
          after: Identifier for the last item from the previous pagination request

          limit: Number of items to retrieve

          order: Sort order of results by timestamp. Use `asc` for ascending order or `desc` for
              descending order.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/videos",
            page=SyncConversationCursorPage[Video],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                        "order": order,
                    },
                    video_list_params.VideoListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=Video,
        )

    def delete(
        self,
        video_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> VideoDeleteResponse:
        """
        Permanently delete a completed or failed video and its stored assets.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not video_id:
            raise ValueError(f"Expected a non-empty value for `video_id` but received {video_id!r}")
        return self._delete(
            path_template("/videos/{video_id}", video_id=video_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=VideoDeleteResponse,
        )

    def create_character(
        self,
        *,
        name: str,
        video: FileTypes,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> VideoCreateCharacterResponse:
        """
        Create a character from an uploaded video.

        Args:
          name: Display name for this API character.

          video: Video file used to create a character.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_with_paths(
            {
                "name": name,
                "video": video,
            },
            [["video"]],
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["video"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/videos/characters",
            body=maybe_transform(body, video_create_character_params.VideoCreateCharacterParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=VideoCreateCharacterResponse,
        )

    def download_content(
        self,
        video_id: str,
        *,
        variant: Literal["video", "thumbnail", "spritesheet"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> _legacy_response.HttpxBinaryResponseContent:
        """
        Download the generated video bytes or a derived preview asset.

        Streams the rendered video content for the specified video job.

        Args:
          variant: Which downloadable asset to return. Defaults to the MP4 video.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not video_id:
            raise ValueError(f"Expected a non-empty value for `video_id` but received {video_id!r}")
        extra_headers = {"Accept": "application/binary", **(extra_headers or {})}
        return self._get(
            path_template("/videos/{video_id}/content", video_id=video_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"variant": variant}, video_download_content_params.VideoDownloadContentParams),
                security={"bearer_auth": True},
            ),
            cast_to=_legacy_response.HttpxBinaryResponseContent,
        )

    def edit(
        self,
        *,
        prompt: str,
        video: video_edit_params.Video,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Video:
        """
        Create a new video generation job by editing a source video or existing
        generated video.

        Args:
          prompt: Text prompt that describes how to edit the source video.

          video: Reference to the completed video to edit.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_with_paths(
            {
                "prompt": prompt,
                "video": video,
            },
            [["video"]],
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["video"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/videos/edits",
            body=maybe_transform(body, video_edit_params.VideoEditParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Video,
        )

    def extend(
        self,
        *,
        prompt: str,
        seconds: VideoSeconds,
        video: video_extend_params.Video,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Video:
        """
        Create an extension of a completed video.

        Args:
          prompt: Updated text prompt that directs the extension generation.

          seconds: Length of the newly generated extension segment in seconds (allowed values: 4,
              8, 12, 16, 20).

          video: Reference to the completed video to extend.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_with_paths(
            {
                "prompt": prompt,
                "seconds": seconds,
                "video": video,
            },
            [["video"]],
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["video"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/videos/extensions",
            body=maybe_transform(body, video_extend_params.VideoExtendParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Video,
        )

    def get_character(
        self,
        character_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> VideoGetCharacterResponse:
        """
        Fetch a character.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not character_id:
            raise ValueError(f"Expected a non-empty value for `character_id` but received {character_id!r}")
        return self._get(
            path_template("/videos/characters/{character_id}", character_id=character_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=VideoGetCharacterResponse,
        )

    def remix(
        self,
        video_id: str,
        *,
        prompt: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Video:
        """
        Create a remix of a completed video using a refreshed prompt.

        Args:
          prompt: Updated text prompt that directs the remix generation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not video_id:
            raise ValueError(f"Expected a non-empty value for `video_id` but received {video_id!r}")
        return self._post(
            path_template("/videos/{video_id}/remix", video_id=video_id),
            body=maybe_transform({"prompt": prompt}, video_remix_params.VideoRemixParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Video,
        )


class AsyncVideos(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncVideosWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncVideosWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncVideosWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncVideosWithStreamingResponse(self)

    async def create(
        self,
        *,
        prompt: str,
        input_reference: video_create_params.InputReference | Omit = omit,
        model: VideoModelParam | Omit = omit,
        seconds: VideoSeconds | Omit = omit,
        size: VideoSize | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Video:
        """
        Create a new video generation job from a prompt and optional reference assets.

        Args:
          prompt: Text prompt that describes the video to generate.

          input_reference: Optional reference asset upload or reference object that guides generation.

          model: The video generation model to use (allowed values: sora-2, sora-2-pro). Defaults
              to `sora-2`.

          seconds: Clip duration in seconds (allowed values: 4, 8, 12). Defaults to 4 seconds.

          size: Output resolution formatted as width x height (allowed values: 720x1280,
              1280x720, 1024x1792, 1792x1024). Defaults to 720x1280.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_with_paths(
            {
                "prompt": prompt,
                "input_reference": input_reference,
                "model": model,
                "seconds": seconds,
                "size": size,
            },
            [["input_reference"]],
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["input_reference"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/videos",
            body=await async_maybe_transform(body, video_create_params.VideoCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Video,
        )

    async def create_and_poll(
        self,
        *,
        prompt: str,
        input_reference: video_create_params.InputReference | Omit = omit,
        model: VideoModelParam | Omit = omit,
        seconds: VideoSeconds | Omit = omit,
        size: VideoSize | Omit = omit,
        poll_interval_ms: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Video:
        """Create a video and wait for it to be processed."""
        video = await self.create(
            model=model,
            prompt=prompt,
            input_reference=input_reference,
            seconds=seconds,
            size=size,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )

        return await self.poll(
            video.id,
            poll_interval_ms=poll_interval_ms,
        )

    async def poll(
        self,
        video_id: str,
        *,
        poll_interval_ms: int | Omit = omit,
    ) -> Video:
        """Wait for the vector store file to finish processing.

        Note: this will return even if the file failed to process, you need to check
        file.last_error and file.status to handle these cases
        """
        headers: dict[str, str] = {"X-Stainless-Poll-Helper": "true"}
        if is_given(poll_interval_ms):
            headers["X-Stainless-Custom-Poll-Interval"] = str(poll_interval_ms)

        while True:
            response = await self.with_raw_response.retrieve(
                video_id,
                extra_headers=headers,
            )

            video = response.parse()
            if video.status == "in_progress" or video.status == "queued":
                if not is_given(poll_interval_ms):
                    from_header = response.headers.get("openai-poll-after-ms")
                    if from_header is not None:
                        poll_interval_ms = int(from_header)
                    else:
                        poll_interval_ms = 1000

                await self._sleep(poll_interval_ms / 1000)
            elif video.status == "completed" or video.status == "failed":
                return video
            else:
                if TYPE_CHECKING:  # type: ignore[unreachable]
                    assert_never(video.status)
                else:
                    return video

    async def retrieve(
        self,
        video_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Video:
        """
        Fetch the latest metadata for a generated video.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not video_id:
            raise ValueError(f"Expected a non-empty value for `video_id` but received {video_id!r}")
        return await self._get(
            path_template("/videos/{video_id}", video_id=video_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Video,
        )

    def list(
        self,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[Video, AsyncConversationCursorPage[Video]]:
        """
        List recently generated videos for the current project.

        Args:
          after: Identifier for the last item from the previous pagination request

          limit: Number of items to retrieve

          order: Sort order of results by timestamp. Use `asc` for ascending order or `desc` for
              descending order.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/videos",
            page=AsyncConversationCursorPage[Video],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                        "order": order,
                    },
                    video_list_params.VideoListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=Video,
        )

    async def delete(
        self,
        video_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> VideoDeleteResponse:
        """
        Permanently delete a completed or failed video and its stored assets.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not video_id:
            raise ValueError(f"Expected a non-empty value for `video_id` but received {video_id!r}")
        return await self._delete(
            path_template("/videos/{video_id}", video_id=video_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=VideoDeleteResponse,
        )

    async def create_character(
        self,
        *,
        name: str,
        video: FileTypes,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> VideoCreateCharacterResponse:
        """
        Create a character from an uploaded video.

        Args:
          name: Display name for this API character.

          video: Video file used to create a character.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_with_paths(
            {
                "name": name,
                "video": video,
            },
            [["video"]],
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["video"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/videos/characters",
            body=await async_maybe_transform(body, video_create_character_params.VideoCreateCharacterParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=VideoCreateCharacterResponse,
        )

    async def download_content(
        self,
        video_id: str,
        *,
        variant: Literal["video", "thumbnail", "spritesheet"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> _legacy_response.HttpxBinaryResponseContent:
        """
        Download the generated video bytes or a derived preview asset.

        Streams the rendered video content for the specified video job.

        Args:
          variant: Which downloadable asset to return. Defaults to the MP4 video.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not video_id:
            raise ValueError(f"Expected a non-empty value for `video_id` but received {video_id!r}")
        extra_headers = {"Accept": "application/binary", **(extra_headers or {})}
        return await self._get(
            path_template("/videos/{video_id}/content", video_id=video_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"variant": variant}, video_download_content_params.VideoDownloadContentParams
                ),
                security={"bearer_auth": True},
            ),
            cast_to=_legacy_response.HttpxBinaryResponseContent,
        )

    async def edit(
        self,
        *,
        prompt: str,
        video: video_edit_params.Video,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Video:
        """
        Create a new video generation job by editing a source video or existing
        generated video.

        Args:
          prompt: Text prompt that describes how to edit the source video.

          video: Reference to the completed video to edit.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_with_paths(
            {
                "prompt": prompt,
                "video": video,
            },
            [["video"]],
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["video"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/videos/edits",
            body=await async_maybe_transform(body, video_edit_params.VideoEditParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Video,
        )

    async def extend(
        self,
        *,
        prompt: str,
        seconds: VideoSeconds,
        video: video_extend_params.Video,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Video:
        """
        Create an extension of a completed video.

        Args:
          prompt: Updated text prompt that directs the extension generation.

          seconds: Length of the newly generated extension segment in seconds (allowed values: 4,
              8, 12, 16, 20).

          video: Reference to the completed video to extend.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_with_paths(
            {
                "prompt": prompt,
                "seconds": seconds,
                "video": video,
            },
            [["video"]],
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["video"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/videos/extensions",
            body=await async_maybe_transform(body, video_extend_params.VideoExtendParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Video,
        )

    async def get_character(
        self,
        character_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> VideoGetCharacterResponse:
        """
        Fetch a character.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not character_id:
            raise ValueError(f"Expected a non-empty value for `character_id` but received {character_id!r}")
        return await self._get(
            path_template("/videos/characters/{character_id}", character_id=character_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=VideoGetCharacterResponse,
        )

    async def remix(
        self,
        video_id: str,
        *,
        prompt: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Video:
        """
        Create a remix of a completed video using a refreshed prompt.

        Args:
          prompt: Updated text prompt that directs the remix generation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not video_id:
            raise ValueError(f"Expected a non-empty value for `video_id` but received {video_id!r}")
        return await self._post(
            path_template("/videos/{video_id}/remix", video_id=video_id),
            body=await async_maybe_transform({"prompt": prompt}, video_remix_params.VideoRemixParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Video,
        )


class VideosWithRawResponse:
    def __init__(self, videos: Videos) -> None:
        self._videos = videos

        self.create = _legacy_response.to_raw_response_wrapper(
            videos.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            videos.retrieve,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            videos.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            videos.delete,
        )
        self.create_character = _legacy_response.to_raw_response_wrapper(
            videos.create_character,
        )
        self.download_content = _legacy_response.to_raw_response_wrapper(
            videos.download_content,
        )
        self.edit = _legacy_response.to_raw_response_wrapper(
            videos.edit,
        )
        self.extend = _legacy_response.to_raw_response_wrapper(
            videos.extend,
        )
        self.get_character = _legacy_response.to_raw_response_wrapper(
            videos.get_character,
        )
        self.remix = _legacy_response.to_raw_response_wrapper(
            videos.remix,
        )


class AsyncVideosWithRawResponse:
    def __init__(self, videos: AsyncVideos) -> None:
        self._videos = videos

        self.create = _legacy_response.async_to_raw_response_wrapper(
            videos.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            videos.retrieve,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            videos.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            videos.delete,
        )
        self.create_character = _legacy_response.async_to_raw_response_wrapper(
            videos.create_character,
        )
        self.download_content = _legacy_response.async_to_raw_response_wrapper(
            videos.download_content,
        )
        self.edit = _legacy_response.async_to_raw_response_wrapper(
            videos.edit,
        )
        self.extend = _legacy_response.async_to_raw_response_wrapper(
            videos.extend,
        )
        self.get_character = _legacy_response.async_to_raw_response_wrapper(
            videos.get_character,
        )
        self.remix = _legacy_response.async_to_raw_response_wrapper(
            videos.remix,
        )


class VideosWithStreamingResponse:
    def __init__(self, videos: Videos) -> None:
        self._videos = videos

        self.create = to_streamed_response_wrapper(
            videos.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            videos.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            videos.list,
        )
        self.delete = to_streamed_response_wrapper(
            videos.delete,
        )
        self.create_character = to_streamed_response_wrapper(
            videos.create_character,
        )
        self.download_content = to_custom_streamed_response_wrapper(
            videos.download_content,
            StreamedBinaryAPIResponse,
        )
        self.edit = to_streamed_response_wrapper(
            videos.edit,
        )
        self.extend = to_streamed_response_wrapper(
            videos.extend,
        )
        self.get_character = to_streamed_response_wrapper(
            videos.get_character,
        )
        self.remix = to_streamed_response_wrapper(
            videos.remix,
        )


class AsyncVideosWithStreamingResponse:
    def __init__(self, videos: AsyncVideos) -> None:
        self._videos = videos

        self.create = async_to_streamed_response_wrapper(
            videos.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            videos.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            videos.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            videos.delete,
        )
        self.create_character = async_to_streamed_response_wrapper(
            videos.create_character,
        )
        self.download_content = async_to_custom_streamed_response_wrapper(
            videos.download_content,
            AsyncStreamedBinaryAPIResponse,
        )
        self.edit = async_to_streamed_response_wrapper(
            videos.edit,
        )
        self.extend = async_to_streamed_response_wrapper(
            videos.extend,
        )
        self.get_character = async_to_streamed_response_wrapper(
            videos.get_character,
        )
        self.remix = async_to_streamed_response_wrapper(
            videos.remix,
        )
