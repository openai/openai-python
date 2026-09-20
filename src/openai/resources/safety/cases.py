# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx2

from ... import _legacy_response
from ..._types import Body, Query, Headers, NotGiven, not_given
from ..._utils import path_template
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ..._base_client import make_request_options
from ...types.safety.safety_case import SafetyCase

__all__ = ["Cases", "AsyncCases"]


class Cases(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CasesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return CasesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CasesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return CasesWithStreamingResponse(self)

    def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SafetyCase:
        """
        Get a safety case by ID.

        Args:
          id: Safety case ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            path_template("/safety/cases/{id}", id=id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=SafetyCase,
        )


class AsyncCases(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCasesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCasesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCasesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncCasesWithStreamingResponse(self)

    async def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SafetyCase:
        """
        Get a safety case by ID.

        Args:
          id: Safety case ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            path_template("/safety/cases/{id}", id=id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=SafetyCase,
        )


class CasesWithRawResponse:
    def __init__(self, cases: Cases) -> None:
        self._cases = cases

        self.retrieve = _legacy_response.to_raw_response_wrapper(
            cases.retrieve,
        )


class AsyncCasesWithRawResponse:
    def __init__(self, cases: AsyncCases) -> None:
        self._cases = cases

        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            cases.retrieve,
        )


class CasesWithStreamingResponse:
    def __init__(self, cases: Cases) -> None:
        self._cases = cases

        self.retrieve = to_streamed_response_wrapper(
            cases.retrieve,
        )


class AsyncCasesWithStreamingResponse:
    def __init__(self, cases: AsyncCases) -> None:
        self._cases = cases

        self.retrieve = async_to_streamed_response_wrapper(
            cases.retrieve,
        )
