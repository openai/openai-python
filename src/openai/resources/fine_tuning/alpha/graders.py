# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable

import httpx

from .... import _legacy_response
from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ...._base_client import make_request_options
from ....types.fine_tuning.alpha import grader_run_params, grader_validate_params
from ....types.fine_tuning.alpha.grader_run_response import GraderRunResponse
from ....types.fine_tuning.alpha.grader_validate_response import GraderValidateResponse

__all__ = ["Graders", "AsyncGraders"]


class Graders(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> GradersWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return GradersWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> GradersWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return GradersWithStreamingResponse(self)

    def run(
        self,
        *,
        grader: grader_run_params.Grader,
        model_sample: str,
        reference_answer: Union[str, Iterable[object], float, object],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraderRunResponse:
        """
        Run a grader.

        Args:
          grader: The grader used for the fine-tuning job.

          model_sample: The model sample to be evaluated.

          reference_answer: The reference answer for the evaluation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/fine_tuning/alpha/graders/run",
            body=maybe_transform(
                {
                    "grader": grader,
                    "model_sample": model_sample,
                    "reference_answer": reference_answer,
                },
                grader_run_params.GraderRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GraderRunResponse,
        )

    def validate(
        self,
        *,
        grader: grader_validate_params.Grader,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraderValidateResponse:
        """
        Validate a grader.

        Args:
          grader: The grader used for the fine-tuning job.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/fine_tuning/alpha/graders/validate",
            body=maybe_transform({"grader": grader}, grader_validate_params.GraderValidateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GraderValidateResponse,
        )


class AsyncGraders(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncGradersWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncGradersWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncGradersWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncGradersWithStreamingResponse(self)

    async def run(
        self,
        *,
        grader: grader_run_params.Grader,
        model_sample: str,
        reference_answer: Union[str, Iterable[object], float, object],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraderRunResponse:
        """
        Run a grader.

        Args:
          grader: The grader used for the fine-tuning job.

          model_sample: The model sample to be evaluated.

          reference_answer: The reference answer for the evaluation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/fine_tuning/alpha/graders/run",
            body=await async_maybe_transform(
                {
                    "grader": grader,
                    "model_sample": model_sample,
                    "reference_answer": reference_answer,
                },
                grader_run_params.GraderRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GraderRunResponse,
        )

    async def validate(
        self,
        *,
        grader: grader_validate_params.Grader,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraderValidateResponse:
        """
        Validate a grader.

        Args:
          grader: The grader used for the fine-tuning job.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/fine_tuning/alpha/graders/validate",
            body=await async_maybe_transform({"grader": grader}, grader_validate_params.GraderValidateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GraderValidateResponse,
        )


class GradersWithRawResponse:
    def __init__(self, graders: Graders) -> None:
        self._graders = graders

        self.run = _legacy_response.to_raw_response_wrapper(
            graders.run,
        )
        self.validate = _legacy_response.to_raw_response_wrapper(
            graders.validate,
        )


class AsyncGradersWithRawResponse:
    def __init__(self, graders: AsyncGraders) -> None:
        self._graders = graders

        self.run = _legacy_response.async_to_raw_response_wrapper(
            graders.run,
        )
        self.validate = _legacy_response.async_to_raw_response_wrapper(
            graders.validate,
        )


class GradersWithStreamingResponse:
    def __init__(self, graders: Graders) -> None:
        self._graders = graders

        self.run = to_streamed_response_wrapper(
            graders.run,
        )
        self.validate = to_streamed_response_wrapper(
            graders.validate,
        )


class AsyncGradersWithStreamingResponse:
    def __init__(self, graders: AsyncGraders) -> None:
        self._graders = graders

        self.run = async_to_streamed_response_wrapper(
            graders.run,
        )
        self.validate = async_to_streamed_response_wrapper(
            graders.validate,
        )
