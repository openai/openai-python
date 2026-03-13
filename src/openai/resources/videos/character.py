# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Mapping, cast

import httpx

from ... import _legacy_response
from ..._types import Body, Query, Headers, NotGiven, FileTypes, not_given
from ..._utils import extract_files, maybe_transform, deepcopy_minimal, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ..._base_client import make_request_options
from ...types.videos import character_create_params
from ...types.videos.character_get_response import CharacterGetResponse
from ...types.videos.character_create_response import CharacterCreateResponse

__all__ = ["Character", "AsyncCharacter"]


class Character(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CharacterWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return CharacterWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CharacterWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return CharacterWithStreamingResponse(self)

    def create(
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
    ) -> CharacterCreateResponse:
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
        body = deepcopy_minimal(
            {
                "name": name,
                "video": video,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["video"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/videos/characters",
            body=maybe_transform(body, character_create_params.CharacterCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CharacterCreateResponse,
        )

    def get(
        self,
        character_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CharacterGetResponse:
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
            f"/videos/characters/{character_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CharacterGetResponse,
        )


class AsyncCharacter(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCharacterWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCharacterWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCharacterWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncCharacterWithStreamingResponse(self)

    async def create(
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
    ) -> CharacterCreateResponse:
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
        body = deepcopy_minimal(
            {
                "name": name,
                "video": video,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["video"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/videos/characters",
            body=await async_maybe_transform(body, character_create_params.CharacterCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CharacterCreateResponse,
        )

    async def get(
        self,
        character_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CharacterGetResponse:
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
            f"/videos/characters/{character_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CharacterGetResponse,
        )


class CharacterWithRawResponse:
    def __init__(self, character: Character) -> None:
        self._character = character

        self.create = _legacy_response.to_raw_response_wrapper(
            character.create,
        )
        self.get = _legacy_response.to_raw_response_wrapper(
            character.get,
        )


class AsyncCharacterWithRawResponse:
    def __init__(self, character: AsyncCharacter) -> None:
        self._character = character

        self.create = _legacy_response.async_to_raw_response_wrapper(
            character.create,
        )
        self.get = _legacy_response.async_to_raw_response_wrapper(
            character.get,
        )


class CharacterWithStreamingResponse:
    def __init__(self, character: Character) -> None:
        self._character = character

        self.create = to_streamed_response_wrapper(
            character.create,
        )
        self.get = to_streamed_response_wrapper(
            character.get,
        )


class AsyncCharacterWithStreamingResponse:
    def __init__(self, character: AsyncCharacter) -> None:
        self._character = character

        self.create = async_to_streamed_response_wrapper(
            character.create,
        )
        self.get = async_to_streamed_response_wrapper(
            character.get,
        )
