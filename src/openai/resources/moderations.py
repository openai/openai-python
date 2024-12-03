# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Iterable

import httpx

from .. import _legacy_response
from ..types import moderation_create_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import (
    maybe_transform,
    async_maybe_transform,
)
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from .._base_client import make_request_options
from ..types.moderation_model import ModerationModel
from ..types.moderation_create_response import ModerationCreateResponse
from ..types.moderation_multi_modal_input_param import ModerationMultiModalInputParam

__all__ = ["Moderations", "AsyncModerations"]


class Moderations(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ModerationsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return ModerationsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ModerationsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return ModerationsWithStreamingResponse(self)

    def create(
        self,
        *,
        input: Union[str, List[str], Iterable[ModerationMultiModalInputParam]],
        model: Union[str, ModerationModel] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ModerationCreateResponse:
        """Classifies if text and/or image inputs are potentially harmful.

        Learn more in
        the [moderation guide](https://platform.openai.com/docs/guides/moderation).

        Args:
          input: Input (or inputs) to classify. Can be a single string, an array of strings, or
              an array of multi-modal input objects similar to other models.

          model: The content moderation model you would like to use. Learn more in
              [the moderation guide](https://platform.openai.com/docs/guides/moderation), and
              learn about available models
              [here](https://platform.openai.com/docs/models#moderation).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/moderations",
            body=maybe_transform(
                {
                    "input": input,
                    "model": model,
                },
                moderation_create_params.ModerationCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModerationCreateResponse,
        )


class AsyncModerations(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncModerationsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncModerationsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncModerationsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncModerationsWithStreamingResponse(self)

    async def create(
        self,
        *,
        input: Union[str, List[str], Iterable[ModerationMultiModalInputParam]],
        model: Union[str, ModerationModel] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ModerationCreateResponse:
        """Classifies if text and/or image inputs are potentially harmful.

        Learn more in
        the [moderation guide](https://platform.openai.com/docs/guides/moderation).

        Args:
          input: Input (or inputs) to classify. Can be a single string, an array of strings, or
              an array of multi-modal input objects similar to other models.

          model: The content moderation model you would like to use. Learn more in
              [the moderation guide](https://platform.openai.com/docs/guides/moderation), and
              learn about available models
              [here](https://platform.openai.com/docs/models#moderation).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/moderations",
            body=await async_maybe_transform(
                {
                    "input": input,
                    "model": model,
                },
                moderation_create_params.ModerationCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ModerationCreateResponse,
        )


class ModerationsWithRawResponse:
    def __init__(self, moderations: Moderations) -> None:
        self._moderations = moderations

        self.create = _legacy_response.to_raw_response_wrapper(
            moderations.create,
        )


class AsyncModerationsWithRawResponse:
    def __init__(self, moderations: AsyncModerations) -> None:
        self._moderations = moderations

        self.create = _legacy_response.async_to_raw_response_wrapper(
            moderations.create,
        )


class ModerationsWithStreamingResponse:
    def __init__(self, moderations: Moderations) -> None:
        self._moderations = moderations

        self.create = to_streamed_response_wrapper(
            moderations.create,
        )


class AsyncModerationsWithStreamingResponse:
    def __init__(self, moderations: AsyncModerations) -> None:
        self._moderations = moderations

        self.create = async_to_streamed_response_wrapper(
            moderations.create,
        )
