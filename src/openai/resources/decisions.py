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
        input: Union[str, Iterable[decision_create_params.InputUnionMember1]],
        model: str,
        questions: Iterable[decision_create_params.Question],
        prompt_cache_key: Optional[str] | Omit = omit,
        prompt_cache_options: Optional[decision_create_params.PromptCacheOptions] | Omit = omit,
        safety_identifier: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Decision:
        """
        Use this endpoint to quickly answer classification or scoring questions about
        some input. You can ask multiple questions in one request.

        Args:
          input: The input to evaluate for every question. Provide a text string or an ordered
              array of messages, function calls and outputs, or custom tool calls and outputs.
              Each tool output must identify a matching call by call ID.

          model: The model to use. Only `gpt-6-luna` is supported.

          questions: Ask 1–400 questions about the input. Each question can be a predicate, choice,
              or score. Answers come back in the same order.

          prompt_cache_key: Partition prompt cache reuse by caller-provided key.

          prompt_cache_options: Options for prompt caching. Supported for `gpt-5.6` and later models. By
              default, OpenAI automatically chooses one implicit cache breakpoint. You can add
              explicit breakpoints to content blocks with `prompt_cache_breakpoint`. Each
              request can write up to four breakpoints. For cache matching, OpenAI considers
              up to the latest 80 breakpoints in the conversation, without a content-block
              lookback limit. Set `mode` to `explicit` to disable the implicit breakpoint. The
              `ttl` defaults to `30m`, which is currently the only supported value. See the
              [prompt caching guide](https://developers.openai.com/api/docs/guides/prompt-caching)
              for current details.

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
                    "prompt_cache_key": prompt_cache_key,
                    "prompt_cache_options": prompt_cache_options,
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
        input: Union[str, Iterable[decision_create_params.InputUnionMember1]],
        model: str,
        questions: Iterable[decision_create_params.Question],
        prompt_cache_key: Optional[str] | Omit = omit,
        prompt_cache_options: Optional[decision_create_params.PromptCacheOptions] | Omit = omit,
        safety_identifier: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Decision:
        """
        Use this endpoint to quickly answer classification or scoring questions about
        some input. You can ask multiple questions in one request.

        Args:
          input: The input to evaluate for every question. Provide a text string or an ordered
              array of messages, function calls and outputs, or custom tool calls and outputs.
              Each tool output must identify a matching call by call ID.

          model: The model to use. Only `gpt-6-luna` is supported.

          questions: Ask 1–400 questions about the input. Each question can be a predicate, choice,
              or score. Answers come back in the same order.

          prompt_cache_key: Partition prompt cache reuse by caller-provided key.

          prompt_cache_options: Options for prompt caching. Supported for `gpt-5.6` and later models. By
              default, OpenAI automatically chooses one implicit cache breakpoint. You can add
              explicit breakpoints to content blocks with `prompt_cache_breakpoint`. Each
              request can write up to four breakpoints. For cache matching, OpenAI considers
              up to the latest 80 breakpoints in the conversation, without a content-block
              lookback limit. Set `mode` to `explicit` to disable the implicit breakpoint. The
              `ttl` defaults to `30m`, which is currently the only supported value. See the
              [prompt caching guide](https://developers.openai.com/api/docs/guides/prompt-caching)
              for current details.

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
                    "prompt_cache_key": prompt_cache_key,
                    "prompt_cache_options": prompt_cache_options,
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
