# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..... import _legacy_response
from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ....._utils import path_template, maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from .....pagination import SyncConversationCursorPage, AsyncConversationCursorPage
from ....._base_client import AsyncPaginator, make_request_options
from .....types.admin.organization.projects import (
    rate_limit_list_rate_limits_params,
    rate_limit_update_rate_limit_params,
)
from .....types.admin.organization.projects.project_rate_limit import ProjectRateLimit

__all__ = ["RateLimits", "AsyncRateLimits"]


class RateLimits(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RateLimitsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return RateLimitsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RateLimitsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return RateLimitsWithStreamingResponse(self)

    def list_rate_limits(
        self,
        project_id: str,
        *,
        after: str | Omit = omit,
        before: str | Omit = omit,
        limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncConversationCursorPage[ProjectRateLimit]:
        """
        Returns the rate limits per model for a project.

        Args:
          after: A cursor for use in pagination. `after` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include after=obj_foo in order to
              fetch the next page of the list.

          before: A cursor for use in pagination. `before` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              beginning with obj_foo, your subsequent call can include before=obj_foo in order
              to fetch the previous page of the list.

          limit: A limit on the number of objects to be returned. The default is 100.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get_api_list(
            path_template("/organization/projects/{project_id}/rate_limits", project_id=project_id),
            page=SyncConversationCursorPage[ProjectRateLimit],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "before": before,
                        "limit": limit,
                    },
                    rate_limit_list_rate_limits_params.RateLimitListRateLimitsParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=ProjectRateLimit,
        )

    def update_rate_limit(
        self,
        rate_limit_id: str,
        *,
        project_id: str,
        batch_1_day_max_input_tokens: int | Omit = omit,
        max_audio_megabytes_per_1_minute: int | Omit = omit,
        max_images_per_1_minute: int | Omit = omit,
        max_requests_per_1_day: int | Omit = omit,
        max_requests_per_1_minute: int | Omit = omit,
        max_tokens_per_1_minute: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProjectRateLimit:
        """
        Updates a project rate limit.

        Args:
          batch_1_day_max_input_tokens: The maximum batch input tokens per day. Only relevant for certain models.

          max_audio_megabytes_per_1_minute: The maximum audio megabytes per minute. Only relevant for certain models.

          max_images_per_1_minute: The maximum images per minute. Only relevant for certain models.

          max_requests_per_1_day: The maximum requests per day. Only relevant for certain models.

          max_requests_per_1_minute: The maximum requests per minute.

          max_tokens_per_1_minute: The maximum tokens per minute.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not rate_limit_id:
            raise ValueError(f"Expected a non-empty value for `rate_limit_id` but received {rate_limit_id!r}")
        return self._post(
            path_template(
                "/organization/projects/{project_id}/rate_limits/{rate_limit_id}",
                project_id=project_id,
                rate_limit_id=rate_limit_id,
            ),
            body=maybe_transform(
                {
                    "batch_1_day_max_input_tokens": batch_1_day_max_input_tokens,
                    "max_audio_megabytes_per_1_minute": max_audio_megabytes_per_1_minute,
                    "max_images_per_1_minute": max_images_per_1_minute,
                    "max_requests_per_1_day": max_requests_per_1_day,
                    "max_requests_per_1_minute": max_requests_per_1_minute,
                    "max_tokens_per_1_minute": max_tokens_per_1_minute,
                },
                rate_limit_update_rate_limit_params.RateLimitUpdateRateLimitParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectRateLimit,
        )


class AsyncRateLimits(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRateLimitsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRateLimitsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRateLimitsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncRateLimitsWithStreamingResponse(self)

    def list_rate_limits(
        self,
        project_id: str,
        *,
        after: str | Omit = omit,
        before: str | Omit = omit,
        limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[ProjectRateLimit, AsyncConversationCursorPage[ProjectRateLimit]]:
        """
        Returns the rate limits per model for a project.

        Args:
          after: A cursor for use in pagination. `after` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include after=obj_foo in order to
              fetch the next page of the list.

          before: A cursor for use in pagination. `before` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              beginning with obj_foo, your subsequent call can include before=obj_foo in order
              to fetch the previous page of the list.

          limit: A limit on the number of objects to be returned. The default is 100.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get_api_list(
            path_template("/organization/projects/{project_id}/rate_limits", project_id=project_id),
            page=AsyncConversationCursorPage[ProjectRateLimit],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "before": before,
                        "limit": limit,
                    },
                    rate_limit_list_rate_limits_params.RateLimitListRateLimitsParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=ProjectRateLimit,
        )

    async def update_rate_limit(
        self,
        rate_limit_id: str,
        *,
        project_id: str,
        batch_1_day_max_input_tokens: int | Omit = omit,
        max_audio_megabytes_per_1_minute: int | Omit = omit,
        max_images_per_1_minute: int | Omit = omit,
        max_requests_per_1_day: int | Omit = omit,
        max_requests_per_1_minute: int | Omit = omit,
        max_tokens_per_1_minute: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProjectRateLimit:
        """
        Updates a project rate limit.

        Args:
          batch_1_day_max_input_tokens: The maximum batch input tokens per day. Only relevant for certain models.

          max_audio_megabytes_per_1_minute: The maximum audio megabytes per minute. Only relevant for certain models.

          max_images_per_1_minute: The maximum images per minute. Only relevant for certain models.

          max_requests_per_1_day: The maximum requests per day. Only relevant for certain models.

          max_requests_per_1_minute: The maximum requests per minute.

          max_tokens_per_1_minute: The maximum tokens per minute.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not rate_limit_id:
            raise ValueError(f"Expected a non-empty value for `rate_limit_id` but received {rate_limit_id!r}")
        return await self._post(
            path_template(
                "/organization/projects/{project_id}/rate_limits/{rate_limit_id}",
                project_id=project_id,
                rate_limit_id=rate_limit_id,
            ),
            body=await async_maybe_transform(
                {
                    "batch_1_day_max_input_tokens": batch_1_day_max_input_tokens,
                    "max_audio_megabytes_per_1_minute": max_audio_megabytes_per_1_minute,
                    "max_images_per_1_minute": max_images_per_1_minute,
                    "max_requests_per_1_day": max_requests_per_1_day,
                    "max_requests_per_1_minute": max_requests_per_1_minute,
                    "max_tokens_per_1_minute": max_tokens_per_1_minute,
                },
                rate_limit_update_rate_limit_params.RateLimitUpdateRateLimitParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectRateLimit,
        )


class RateLimitsWithRawResponse:
    def __init__(self, rate_limits: RateLimits) -> None:
        self._rate_limits = rate_limits

        self.list_rate_limits = _legacy_response.to_raw_response_wrapper(
            rate_limits.list_rate_limits,
        )
        self.update_rate_limit = _legacy_response.to_raw_response_wrapper(
            rate_limits.update_rate_limit,
        )


class AsyncRateLimitsWithRawResponse:
    def __init__(self, rate_limits: AsyncRateLimits) -> None:
        self._rate_limits = rate_limits

        self.list_rate_limits = _legacy_response.async_to_raw_response_wrapper(
            rate_limits.list_rate_limits,
        )
        self.update_rate_limit = _legacy_response.async_to_raw_response_wrapper(
            rate_limits.update_rate_limit,
        )


class RateLimitsWithStreamingResponse:
    def __init__(self, rate_limits: RateLimits) -> None:
        self._rate_limits = rate_limits

        self.list_rate_limits = to_streamed_response_wrapper(
            rate_limits.list_rate_limits,
        )
        self.update_rate_limit = to_streamed_response_wrapper(
            rate_limits.update_rate_limit,
        )


class AsyncRateLimitsWithStreamingResponse:
    def __init__(self, rate_limits: AsyncRateLimits) -> None:
        self._rate_limits = rate_limits

        self.list_rate_limits = async_to_streamed_response_wrapper(
            rate_limits.list_rate_limits,
        )
        self.update_rate_limit = async_to_streamed_response_wrapper(
            rate_limits.update_rate_limit,
        )
