# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from .... import _legacy_response
from ...._types import Body, Query, Headers, NotGiven, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ...._base_client import make_request_options
from ....types.admin.organization import spend_limit_update_params
from ....types.admin.organization.organization_spend_limit import OrganizationSpendLimit
from ....types.admin.organization.organization_spend_limit_deleted import OrganizationSpendLimitDeleted

__all__ = ["SpendLimit", "AsyncSpendLimit"]


class SpendLimit(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SpendLimitWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return SpendLimitWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SpendLimitWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return SpendLimitWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationSpendLimit:
        """Get the organization's hard spend limit."""
        return self._get(
            "/organization/spend_limit",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=OrganizationSpendLimit,
        )

    def update(
        self,
        *,
        currency: Literal["USD"],
        interval: Literal["month"],
        threshold_amount: int,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationSpendLimit:
        """
        Create or replace the organization's hard spend limit.

        Args:
          currency: The currency for the threshold amount. Currently, only `USD` is supported.

          interval: The time interval for evaluating spend against the threshold. Currently, only
              `month` is supported.

          threshold_amount: The hard spend limit amount, in cents.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/organization/spend_limit",
            body=maybe_transform(
                {
                    "currency": currency,
                    "interval": interval,
                    "threshold_amount": threshold_amount,
                },
                spend_limit_update_params.SpendLimitUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=OrganizationSpendLimit,
        )

    def delete(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationSpendLimitDeleted:
        """Delete the organization's hard spend limit."""
        return self._delete(
            "/organization/spend_limit",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=OrganizationSpendLimitDeleted,
        )


class AsyncSpendLimit(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSpendLimitWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSpendLimitWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSpendLimitWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncSpendLimitWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationSpendLimit:
        """Get the organization's hard spend limit."""
        return await self._get(
            "/organization/spend_limit",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=OrganizationSpendLimit,
        )

    async def update(
        self,
        *,
        currency: Literal["USD"],
        interval: Literal["month"],
        threshold_amount: int,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationSpendLimit:
        """
        Create or replace the organization's hard spend limit.

        Args:
          currency: The currency for the threshold amount. Currently, only `USD` is supported.

          interval: The time interval for evaluating spend against the threshold. Currently, only
              `month` is supported.

          threshold_amount: The hard spend limit amount, in cents.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/organization/spend_limit",
            body=await async_maybe_transform(
                {
                    "currency": currency,
                    "interval": interval,
                    "threshold_amount": threshold_amount,
                },
                spend_limit_update_params.SpendLimitUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=OrganizationSpendLimit,
        )

    async def delete(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationSpendLimitDeleted:
        """Delete the organization's hard spend limit."""
        return await self._delete(
            "/organization/spend_limit",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=OrganizationSpendLimitDeleted,
        )


class SpendLimitWithRawResponse:
    def __init__(self, spend_limit: SpendLimit) -> None:
        self._spend_limit = spend_limit

        self.retrieve = _legacy_response.to_raw_response_wrapper(
            spend_limit.retrieve,
        )
        self.update = _legacy_response.to_raw_response_wrapper(
            spend_limit.update,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            spend_limit.delete,
        )


class AsyncSpendLimitWithRawResponse:
    def __init__(self, spend_limit: AsyncSpendLimit) -> None:
        self._spend_limit = spend_limit

        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            spend_limit.retrieve,
        )
        self.update = _legacy_response.async_to_raw_response_wrapper(
            spend_limit.update,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            spend_limit.delete,
        )


class SpendLimitWithStreamingResponse:
    def __init__(self, spend_limit: SpendLimit) -> None:
        self._spend_limit = spend_limit

        self.retrieve = to_streamed_response_wrapper(
            spend_limit.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            spend_limit.update,
        )
        self.delete = to_streamed_response_wrapper(
            spend_limit.delete,
        )


class AsyncSpendLimitWithStreamingResponse:
    def __init__(self, spend_limit: AsyncSpendLimit) -> None:
        self._spend_limit = spend_limit

        self.retrieve = async_to_streamed_response_wrapper(
            spend_limit.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            spend_limit.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            spend_limit.delete,
        )
