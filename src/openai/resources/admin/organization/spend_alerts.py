# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from .... import _legacy_response
from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ...._utils import path_template, maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ....pagination import SyncConversationCursorPage, AsyncConversationCursorPage
from ...._base_client import AsyncPaginator, make_request_options
from ....types.admin.organization import spend_alert_list_params, spend_alert_create_params, spend_alert_update_params
from ....types.admin.organization.organization_spend_alert import OrganizationSpendAlert
from ....types.admin.organization.organization_spend_alert_deleted import OrganizationSpendAlertDeleted

__all__ = ["SpendAlerts", "AsyncSpendAlerts"]


class SpendAlerts(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SpendAlertsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return SpendAlertsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SpendAlertsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return SpendAlertsWithStreamingResponse(self)

    def create(
        self,
        *,
        currency: Literal["USD"],
        interval: Literal["month"],
        notification_channel: spend_alert_create_params.NotificationChannel,
        threshold_amount: int,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationSpendAlert:
        """
        Creates an organization spend alert.

        Args:
          currency: The currency for the threshold amount.

          interval: The time interval for evaluating spend against the threshold.

          notification_channel: Email notification settings for a spend alert.

          threshold_amount: The alert threshold amount, in cents.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/organization/spend_alerts",
            body=maybe_transform(
                {
                    "currency": currency,
                    "interval": interval,
                    "notification_channel": notification_channel,
                    "threshold_amount": threshold_amount,
                },
                spend_alert_create_params.SpendAlertCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=OrganizationSpendAlert,
        )

    def retrieve(
        self,
        alert_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationSpendAlert:
        """
        Retrieves an organization spend alert.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not alert_id:
            raise ValueError(f"Expected a non-empty value for `alert_id` but received {alert_id!r}")
        return self._get(
            path_template("/organization/spend_alerts/{alert_id}", alert_id=alert_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=OrganizationSpendAlert,
        )

    def update(
        self,
        alert_id: str,
        *,
        currency: Literal["USD"],
        interval: Literal["month"],
        notification_channel: spend_alert_update_params.NotificationChannel,
        threshold_amount: int,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationSpendAlert:
        """
        Updates an organization spend alert.

        Args:
          currency: The currency for the threshold amount.

          interval: The time interval for evaluating spend against the threshold.

          notification_channel: Email notification settings for a spend alert.

          threshold_amount: The alert threshold amount, in cents.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not alert_id:
            raise ValueError(f"Expected a non-empty value for `alert_id` but received {alert_id!r}")
        return self._post(
            path_template("/organization/spend_alerts/{alert_id}", alert_id=alert_id),
            body=maybe_transform(
                {
                    "currency": currency,
                    "interval": interval,
                    "notification_channel": notification_channel,
                    "threshold_amount": threshold_amount,
                },
                spend_alert_update_params.SpendAlertUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=OrganizationSpendAlert,
        )

    def list(
        self,
        *,
        after: str | Omit = omit,
        before: str | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncConversationCursorPage[OrganizationSpendAlert]:
        """Lists organization spend alerts.

        Args:
          after: Cursor for pagination.

        Provide the ID of the last spend alert from the previous
              response to fetch the next page.

          before: Cursor for pagination. Provide the ID of the first spend alert from the previous
              response to fetch the previous page.

          limit: A limit on the number of spend alerts to return. Defaults to 20.

          order: Sort order for the returned spend alerts.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/organization/spend_alerts",
            page=SyncConversationCursorPage[OrganizationSpendAlert],
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
                        "order": order,
                    },
                    spend_alert_list_params.SpendAlertListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=OrganizationSpendAlert,
        )

    def delete(
        self,
        alert_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationSpendAlertDeleted:
        """
        Deletes an organization spend alert.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not alert_id:
            raise ValueError(f"Expected a non-empty value for `alert_id` but received {alert_id!r}")
        return self._delete(
            path_template("/organization/spend_alerts/{alert_id}", alert_id=alert_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=OrganizationSpendAlertDeleted,
        )


class AsyncSpendAlerts(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSpendAlertsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSpendAlertsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSpendAlertsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncSpendAlertsWithStreamingResponse(self)

    async def create(
        self,
        *,
        currency: Literal["USD"],
        interval: Literal["month"],
        notification_channel: spend_alert_create_params.NotificationChannel,
        threshold_amount: int,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationSpendAlert:
        """
        Creates an organization spend alert.

        Args:
          currency: The currency for the threshold amount.

          interval: The time interval for evaluating spend against the threshold.

          notification_channel: Email notification settings for a spend alert.

          threshold_amount: The alert threshold amount, in cents.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/organization/spend_alerts",
            body=await async_maybe_transform(
                {
                    "currency": currency,
                    "interval": interval,
                    "notification_channel": notification_channel,
                    "threshold_amount": threshold_amount,
                },
                spend_alert_create_params.SpendAlertCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=OrganizationSpendAlert,
        )

    async def retrieve(
        self,
        alert_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationSpendAlert:
        """
        Retrieves an organization spend alert.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not alert_id:
            raise ValueError(f"Expected a non-empty value for `alert_id` but received {alert_id!r}")
        return await self._get(
            path_template("/organization/spend_alerts/{alert_id}", alert_id=alert_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=OrganizationSpendAlert,
        )

    async def update(
        self,
        alert_id: str,
        *,
        currency: Literal["USD"],
        interval: Literal["month"],
        notification_channel: spend_alert_update_params.NotificationChannel,
        threshold_amount: int,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationSpendAlert:
        """
        Updates an organization spend alert.

        Args:
          currency: The currency for the threshold amount.

          interval: The time interval for evaluating spend against the threshold.

          notification_channel: Email notification settings for a spend alert.

          threshold_amount: The alert threshold amount, in cents.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not alert_id:
            raise ValueError(f"Expected a non-empty value for `alert_id` but received {alert_id!r}")
        return await self._post(
            path_template("/organization/spend_alerts/{alert_id}", alert_id=alert_id),
            body=await async_maybe_transform(
                {
                    "currency": currency,
                    "interval": interval,
                    "notification_channel": notification_channel,
                    "threshold_amount": threshold_amount,
                },
                spend_alert_update_params.SpendAlertUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=OrganizationSpendAlert,
        )

    def list(
        self,
        *,
        after: str | Omit = omit,
        before: str | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[OrganizationSpendAlert, AsyncConversationCursorPage[OrganizationSpendAlert]]:
        """Lists organization spend alerts.

        Args:
          after: Cursor for pagination.

        Provide the ID of the last spend alert from the previous
              response to fetch the next page.

          before: Cursor for pagination. Provide the ID of the first spend alert from the previous
              response to fetch the previous page.

          limit: A limit on the number of spend alerts to return. Defaults to 20.

          order: Sort order for the returned spend alerts.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/organization/spend_alerts",
            page=AsyncConversationCursorPage[OrganizationSpendAlert],
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
                        "order": order,
                    },
                    spend_alert_list_params.SpendAlertListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=OrganizationSpendAlert,
        )

    async def delete(
        self,
        alert_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationSpendAlertDeleted:
        """
        Deletes an organization spend alert.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not alert_id:
            raise ValueError(f"Expected a non-empty value for `alert_id` but received {alert_id!r}")
        return await self._delete(
            path_template("/organization/spend_alerts/{alert_id}", alert_id=alert_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=OrganizationSpendAlertDeleted,
        )


class SpendAlertsWithRawResponse:
    def __init__(self, spend_alerts: SpendAlerts) -> None:
        self._spend_alerts = spend_alerts

        self.create = _legacy_response.to_raw_response_wrapper(
            spend_alerts.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            spend_alerts.retrieve,
        )
        self.update = _legacy_response.to_raw_response_wrapper(
            spend_alerts.update,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            spend_alerts.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            spend_alerts.delete,
        )


class AsyncSpendAlertsWithRawResponse:
    def __init__(self, spend_alerts: AsyncSpendAlerts) -> None:
        self._spend_alerts = spend_alerts

        self.create = _legacy_response.async_to_raw_response_wrapper(
            spend_alerts.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            spend_alerts.retrieve,
        )
        self.update = _legacy_response.async_to_raw_response_wrapper(
            spend_alerts.update,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            spend_alerts.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            spend_alerts.delete,
        )


class SpendAlertsWithStreamingResponse:
    def __init__(self, spend_alerts: SpendAlerts) -> None:
        self._spend_alerts = spend_alerts

        self.create = to_streamed_response_wrapper(
            spend_alerts.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            spend_alerts.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            spend_alerts.update,
        )
        self.list = to_streamed_response_wrapper(
            spend_alerts.list,
        )
        self.delete = to_streamed_response_wrapper(
            spend_alerts.delete,
        )


class AsyncSpendAlertsWithStreamingResponse:
    def __init__(self, spend_alerts: AsyncSpendAlerts) -> None:
        self._spend_alerts = spend_alerts

        self.create = async_to_streamed_response_wrapper(
            spend_alerts.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            spend_alerts.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            spend_alerts.update,
        )
        self.list = async_to_streamed_response_wrapper(
            spend_alerts.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            spend_alerts.delete,
        )
