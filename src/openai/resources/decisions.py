# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional

import httpx2

from .. import _legacy_response
from ..types import decision_create_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from .._base_client import make_request_options
from ..types.decision import Decision
from ..types.decision_input_message_param import DecisionInputMessageParam

__all__ = ["Decisions", "AsyncDecisions"]


class Decisions(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DecisionsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return DecisionsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DecisionsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return DecisionsWithStreamingResponse(self)

    def create(
        self,
        *,
        input: Union[str, Iterable[DecisionInputMessageParam]],
        model: str,
        questions: Iterable[decision_create_params.Question],
        safety_identifier: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Decision:
        """Evaluate ordered classification and scoring questions against shared input.

        Answers are returned in question order.

        Supply input as a string or user messages containing text and inline images.
        Only user messages with `input_text` and `input_image` parts are supported;
        non-user roles, function calls, files, audio, and item references are not
        supported. Images require a data URL, not an external URL or file ID. At most
        128 images are allowed across the request.

        Each question can return a refusal instead of a scored answer. A refusal has
        type `refusal` and the corresponding question name, or null if unnamed.

        Args:
          input: Shared evidence, as a string or an array of user messages containing text and
              inline images. Non-user roles, function calls, function-call outputs, files,
              audio, and item references are not supported. At most 128 image parts are
              allowed across all messages in one request.

          safety_identifier: Opaque caller-provided end-user identifier, scoped by the verified org. Match
              Responses' limit; this is never the authenticated user identity.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/decisions",
            body=maybe_transform(
                {
                    "model": model,
                    "input": input,
                    "questions": questions,
                    "safety_identifier": safety_identifier,
                },
                decision_create_params.DecisionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Decision,
        )


class AsyncDecisions(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDecisionsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDecisionsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDecisionsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncDecisionsWithStreamingResponse(self)

    async def create(
        self,
        *,
        input: Union[str, Iterable[DecisionInputMessageParam]],
        model: str,
        questions: Iterable[decision_create_params.Question],
        safety_identifier: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Decision:
        """Evaluate ordered classification and scoring questions against shared input.

        Answers are returned in question order.

        Supply input as a string or user messages containing text and inline images.
        Only user messages with `input_text` and `input_image` parts are supported;
        non-user roles, function calls, files, audio, and item references are not
        supported. Images require a data URL, not an external URL or file ID. At most
        128 images are allowed across the request.

        Each question can return a refusal instead of a scored answer. A refusal has
        type `refusal` and the corresponding question name, or null if unnamed.

        Args:
          input: Shared evidence, as a string or an array of user messages containing text and
              inline images. Non-user roles, function calls, function-call outputs, files,
              audio, and item references are not supported. At most 128 image parts are
              allowed across all messages in one request.

          safety_identifier: Opaque caller-provided end-user identifier, scoped by the verified org. Match
              Responses' limit; this is never the authenticated user identity.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/decisions",
            body=await async_maybe_transform(
                {
                    "model": model,
                    "input": input,
                    "questions": questions,
                    "safety_identifier": safety_identifier,
                },
                decision_create_params.DecisionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Decision,
        )


class DecisionsWithRawResponse:
    def __init__(self, decisions: Decisions) -> None:
        self._decisions = decisions

        self.create = _legacy_response.to_raw_response_wrapper(
            decisions.create,
        )


class AsyncDecisionsWithRawResponse:
    def __init__(self, decisions: AsyncDecisions) -> None:
        self._decisions = decisions

        self.create = _legacy_response.async_to_raw_response_wrapper(
            decisions.create,
        )


class DecisionsWithStreamingResponse:
    def __init__(self, decisions: Decisions) -> None:
        self._decisions = decisions

        self.create = to_streamed_response_wrapper(
            decisions.create,
        )


class AsyncDecisionsWithStreamingResponse:
    def __init__(self, decisions: AsyncDecisions) -> None:
        self._decisions = decisions

        self.create = async_to_streamed_response_wrapper(
            decisions.create,
        )
