# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import json
from typing import List, Optional, cast
from typing_extensions import Literal

import httpx2

from ... import _legacy_response
from ..._types import Body, Omit, Query, Headers, NotGiven, HeadersLike, omit, not_given
from ..._utils import path_template, maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._models import construct_type
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from .event_types import (
    EventTypes,
    AsyncEventTypes,
    EventTypesWithRawResponse,
    AsyncEventTypesWithRawResponse,
    EventTypesWithStreamingResponse,
    AsyncEventTypesWithStreamingResponse,
)
from ...pagination import SyncCursorPage, AsyncCursorPage
from ..._exceptions import InvalidWebhookSignatureError
from ..._base_client import AsyncPaginator, make_request_options
from ...lib._webhooks import webhook_signature_matches as _webhook_signature_matches
from ...types.webhooks import (
    webhook_list_params,
    webhook_test_params,
    webhook_create_params,
    webhook_update_params,
    webhook_rotate_secret_params,
)
from ...types.webhooks.webhook_endpoint import WebhookEndpoint
from ...types.webhooks.unwrap_webhook_event import UnwrapWebhookEvent
from ...types.webhooks.deleted_webhook_endpoint import DeletedWebhookEndpoint
from ...types.webhooks.webhook_endpoint_test_result import WebhookEndpointTestResult
from ...types.webhooks.webhook_endpoint_with_secret import WebhookEndpointWithSecret

__all__ = ["Webhooks", "AsyncWebhooks"]


class Webhooks(SyncAPIResource):
    @cached_property
    def event_types(self) -> EventTypes:
        return EventTypes(self._client)

    @cached_property
    def with_raw_response(self) -> WebhooksWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return WebhooksWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> WebhooksWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return WebhooksWithStreamingResponse(self)

    def create(
        self,
        *,
        event_types: List[
            Literal[
                "batch.completed",
                "batch.failed",
                "batch.expired",
                "batch.cancelled",
                "response.completed",
                "response.failed",
                "response.cancelled",
                "response.incomplete",
                "eval.run.succeeded",
                "eval.run.failed",
                "eval.run.canceled",
                "fine_tuning.job.succeeded",
                "fine_tuning.job.failed",
                "fine_tuning.job.cancelled",
                "realtime.call.incoming",
                "video.completed",
                "video.failed",
                "safety.alert.created",
            ]
        ],
        name: str,
        url: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> WebhookEndpointWithSecret:
        """
        Creates a webhook endpoint for the authenticated project.

        Args:
          event_types: The event types that trigger deliveries to this endpoint.

          name: A human-readable name for the webhook endpoint.

          url: The HTTPS URL that receives webhook deliveries.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/webhook_endpoints",
            body=maybe_transform(
                {
                    "event_types": event_types,
                    "name": name,
                    "url": url,
                },
                webhook_create_params.WebhookCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=WebhookEndpointWithSecret,
        )

    def retrieve(
        self,
        webhook_endpoint_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> WebhookEndpoint:
        """
        Retrieves a webhook endpoint for the authenticated project.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not webhook_endpoint_id:
            raise ValueError(
                f"Expected a non-empty value for `webhook_endpoint_id` but received {webhook_endpoint_id!r}"
            )
        return self._get(
            path_template("/webhook_endpoints/{webhook_endpoint_id}", webhook_endpoint_id=webhook_endpoint_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=WebhookEndpoint,
        )

    def update(
        self,
        webhook_endpoint_id: str,
        *,
        event_types: List[
            Literal[
                "batch.completed",
                "batch.failed",
                "batch.expired",
                "batch.cancelled",
                "response.completed",
                "response.failed",
                "response.cancelled",
                "response.incomplete",
                "eval.run.succeeded",
                "eval.run.failed",
                "eval.run.canceled",
                "fine_tuning.job.succeeded",
                "fine_tuning.job.failed",
                "fine_tuning.job.cancelled",
                "realtime.call.incoming",
                "video.completed",
                "video.failed",
                "safety.alert.created",
            ]
        ]
        | Omit = omit,
        name: str | Omit = omit,
        url: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> WebhookEndpoint:
        """
        Updates a webhook endpoint for the authenticated project.

        Args:
          event_types: The complete set of event types that should trigger deliveries.

          name: A new human-readable name for the webhook endpoint.

          url: A new HTTPS URL that receives webhook deliveries.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not webhook_endpoint_id:
            raise ValueError(
                f"Expected a non-empty value for `webhook_endpoint_id` but received {webhook_endpoint_id!r}"
            )
        return self._post(
            path_template("/webhook_endpoints/{webhook_endpoint_id}", webhook_endpoint_id=webhook_endpoint_id),
            body=maybe_transform(
                {
                    "event_types": event_types,
                    "name": name,
                    "url": url,
                },
                webhook_update_params.WebhookUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=WebhookEndpoint,
        )

    def list(
        self,
        *,
        after: Optional[str] | Omit = omit,
        limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPage[WebhookEndpoint]:
        """
        Returns webhook endpoints for the authenticated project in newest-first order.

        Args:
          after: ID of the last webhook endpoint from the previous page.

          limit: Maximum number of webhook endpoints to return. Defaults to 20.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/webhook_endpoints",
            page=SyncCursorPage[WebhookEndpoint],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                    },
                    webhook_list_params.WebhookListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=WebhookEndpoint,
        )

    def delete(
        self,
        webhook_endpoint_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> DeletedWebhookEndpoint:
        """
        Deletes a webhook endpoint for the authenticated project.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not webhook_endpoint_id:
            raise ValueError(
                f"Expected a non-empty value for `webhook_endpoint_id` but received {webhook_endpoint_id!r}"
            )
        return self._delete(
            path_template("/webhook_endpoints/{webhook_endpoint_id}", webhook_endpoint_id=webhook_endpoint_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=DeletedWebhookEndpoint,
        )

    def rotate_secret(
        self,
        webhook_endpoint_id: str,
        *,
        keep_old_secret_active_for_24_hours: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> WebhookEndpointWithSecret:
        """
        Rotates the signing secret for a webhook endpoint in the authenticated project.

        Args:
          keep_old_secret_active_for_24_hours: Whether to keep the previous signing secret valid for 24 hours after rotation.
              Defaults to false, which invalidates the previous secret immediately.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not webhook_endpoint_id:
            raise ValueError(
                f"Expected a non-empty value for `webhook_endpoint_id` but received {webhook_endpoint_id!r}"
            )
        return self._post(
            path_template(
                "/webhook_endpoints/{webhook_endpoint_id}/rotate_secret", webhook_endpoint_id=webhook_endpoint_id
            ),
            body=maybe_transform(
                {"keep_old_secret_active_for_24_hours": keep_old_secret_active_for_24_hours},
                webhook_rotate_secret_params.WebhookRotateSecretParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=WebhookEndpointWithSecret,
        )

    def test(
        self,
        webhook_endpoint_id: str,
        *,
        event_type: Literal[
            "batch.completed",
            "batch.failed",
            "batch.expired",
            "batch.cancelled",
            "response.completed",
            "response.failed",
            "response.cancelled",
            "response.incomplete",
            "eval.run.succeeded",
            "eval.run.failed",
            "eval.run.canceled",
            "fine_tuning.job.succeeded",
            "fine_tuning.job.failed",
            "fine_tuning.job.cancelled",
            "realtime.call.incoming",
            "video.completed",
            "video.failed",
            "safety.alert.created",
        ],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> WebhookEndpointTestResult:
        """
        Sends a sample event to a webhook endpoint for the authenticated project.

        Args:
          event_type: The event type to send as a sample delivery.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not webhook_endpoint_id:
            raise ValueError(
                f"Expected a non-empty value for `webhook_endpoint_id` but received {webhook_endpoint_id!r}"
            )
        return self._post(
            path_template("/webhook_endpoints/{webhook_endpoint_id}/test", webhook_endpoint_id=webhook_endpoint_id),
            body=maybe_transform({"event_type": event_type}, webhook_test_params.WebhookTestParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=WebhookEndpointTestResult,
        )

    def unwrap(
        self,
        payload: str | bytes,
        headers: HeadersLike,
        *,
        secret: str | None = None,
    ) -> UnwrapWebhookEvent:
        """Validates that the given payload was sent by OpenAI and parses the payload."""
        if secret is None:
            secret = self._client.webhook_secret

        self.verify_signature(payload=payload, headers=headers, secret=secret)

        return cast(
            UnwrapWebhookEvent,
            construct_type(
                type_=UnwrapWebhookEvent,
                value=json.loads(payload),
            ),
        )

    def verify_signature(
        self,
        payload: str | bytes,
        headers: HeadersLike,
        *,
        secret: str | None = None,
        tolerance: int = 300,
    ) -> None:
        """Validates whether or not the webhook payload was sent by OpenAI.

        Args:
            payload: The webhook payload
            headers: The webhook headers
            secret: The webhook secret (optional, will use client secret if not provided)
            tolerance: Maximum age of the webhook in seconds (default: 300 = 5 minutes)
        """
        if secret is None:
            secret = self._client.webhook_secret

        if secret is None:
            raise ValueError(
                "The webhook secret must either be set using the env var, OPENAI_WEBHOOK_SECRET, "
                "on the client class, OpenAI(webhook_secret='123'), or passed to this function"
            )

        if not _webhook_signature_matches(payload, headers, secret=secret, tolerance=tolerance):
            raise InvalidWebhookSignatureError(
                "The given webhook signature does not match the expected signature"
            ) from None


class AsyncWebhooks(AsyncAPIResource):
    @cached_property
    def event_types(self) -> AsyncEventTypes:
        return AsyncEventTypes(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncWebhooksWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncWebhooksWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncWebhooksWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncWebhooksWithStreamingResponse(self)

    async def create(
        self,
        *,
        event_types: List[
            Literal[
                "batch.completed",
                "batch.failed",
                "batch.expired",
                "batch.cancelled",
                "response.completed",
                "response.failed",
                "response.cancelled",
                "response.incomplete",
                "eval.run.succeeded",
                "eval.run.failed",
                "eval.run.canceled",
                "fine_tuning.job.succeeded",
                "fine_tuning.job.failed",
                "fine_tuning.job.cancelled",
                "realtime.call.incoming",
                "video.completed",
                "video.failed",
                "safety.alert.created",
            ]
        ],
        name: str,
        url: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> WebhookEndpointWithSecret:
        """
        Creates a webhook endpoint for the authenticated project.

        Args:
          event_types: The event types that trigger deliveries to this endpoint.

          name: A human-readable name for the webhook endpoint.

          url: The HTTPS URL that receives webhook deliveries.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/webhook_endpoints",
            body=await async_maybe_transform(
                {
                    "event_types": event_types,
                    "name": name,
                    "url": url,
                },
                webhook_create_params.WebhookCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=WebhookEndpointWithSecret,
        )

    async def retrieve(
        self,
        webhook_endpoint_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> WebhookEndpoint:
        """
        Retrieves a webhook endpoint for the authenticated project.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not webhook_endpoint_id:
            raise ValueError(
                f"Expected a non-empty value for `webhook_endpoint_id` but received {webhook_endpoint_id!r}"
            )
        return await self._get(
            path_template("/webhook_endpoints/{webhook_endpoint_id}", webhook_endpoint_id=webhook_endpoint_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=WebhookEndpoint,
        )

    async def update(
        self,
        webhook_endpoint_id: str,
        *,
        event_types: List[
            Literal[
                "batch.completed",
                "batch.failed",
                "batch.expired",
                "batch.cancelled",
                "response.completed",
                "response.failed",
                "response.cancelled",
                "response.incomplete",
                "eval.run.succeeded",
                "eval.run.failed",
                "eval.run.canceled",
                "fine_tuning.job.succeeded",
                "fine_tuning.job.failed",
                "fine_tuning.job.cancelled",
                "realtime.call.incoming",
                "video.completed",
                "video.failed",
                "safety.alert.created",
            ]
        ]
        | Omit = omit,
        name: str | Omit = omit,
        url: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> WebhookEndpoint:
        """
        Updates a webhook endpoint for the authenticated project.

        Args:
          event_types: The complete set of event types that should trigger deliveries.

          name: A new human-readable name for the webhook endpoint.

          url: A new HTTPS URL that receives webhook deliveries.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not webhook_endpoint_id:
            raise ValueError(
                f"Expected a non-empty value for `webhook_endpoint_id` but received {webhook_endpoint_id!r}"
            )
        return await self._post(
            path_template("/webhook_endpoints/{webhook_endpoint_id}", webhook_endpoint_id=webhook_endpoint_id),
            body=await async_maybe_transform(
                {
                    "event_types": event_types,
                    "name": name,
                    "url": url,
                },
                webhook_update_params.WebhookUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=WebhookEndpoint,
        )

    def list(
        self,
        *,
        after: Optional[str] | Omit = omit,
        limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[WebhookEndpoint, AsyncCursorPage[WebhookEndpoint]]:
        """
        Returns webhook endpoints for the authenticated project in newest-first order.

        Args:
          after: ID of the last webhook endpoint from the previous page.

          limit: Maximum number of webhook endpoints to return. Defaults to 20.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/webhook_endpoints",
            page=AsyncCursorPage[WebhookEndpoint],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                    },
                    webhook_list_params.WebhookListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=WebhookEndpoint,
        )

    async def delete(
        self,
        webhook_endpoint_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> DeletedWebhookEndpoint:
        """
        Deletes a webhook endpoint for the authenticated project.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not webhook_endpoint_id:
            raise ValueError(
                f"Expected a non-empty value for `webhook_endpoint_id` but received {webhook_endpoint_id!r}"
            )
        return await self._delete(
            path_template("/webhook_endpoints/{webhook_endpoint_id}", webhook_endpoint_id=webhook_endpoint_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=DeletedWebhookEndpoint,
        )

    async def rotate_secret(
        self,
        webhook_endpoint_id: str,
        *,
        keep_old_secret_active_for_24_hours: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> WebhookEndpointWithSecret:
        """
        Rotates the signing secret for a webhook endpoint in the authenticated project.

        Args:
          keep_old_secret_active_for_24_hours: Whether to keep the previous signing secret valid for 24 hours after rotation.
              Defaults to false, which invalidates the previous secret immediately.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not webhook_endpoint_id:
            raise ValueError(
                f"Expected a non-empty value for `webhook_endpoint_id` but received {webhook_endpoint_id!r}"
            )
        return await self._post(
            path_template(
                "/webhook_endpoints/{webhook_endpoint_id}/rotate_secret", webhook_endpoint_id=webhook_endpoint_id
            ),
            body=await async_maybe_transform(
                {"keep_old_secret_active_for_24_hours": keep_old_secret_active_for_24_hours},
                webhook_rotate_secret_params.WebhookRotateSecretParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=WebhookEndpointWithSecret,
        )

    async def test(
        self,
        webhook_endpoint_id: str,
        *,
        event_type: Literal[
            "batch.completed",
            "batch.failed",
            "batch.expired",
            "batch.cancelled",
            "response.completed",
            "response.failed",
            "response.cancelled",
            "response.incomplete",
            "eval.run.succeeded",
            "eval.run.failed",
            "eval.run.canceled",
            "fine_tuning.job.succeeded",
            "fine_tuning.job.failed",
            "fine_tuning.job.cancelled",
            "realtime.call.incoming",
            "video.completed",
            "video.failed",
            "safety.alert.created",
        ],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> WebhookEndpointTestResult:
        """
        Sends a sample event to a webhook endpoint for the authenticated project.

        Args:
          event_type: The event type to send as a sample delivery.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not webhook_endpoint_id:
            raise ValueError(
                f"Expected a non-empty value for `webhook_endpoint_id` but received {webhook_endpoint_id!r}"
            )
        return await self._post(
            path_template("/webhook_endpoints/{webhook_endpoint_id}/test", webhook_endpoint_id=webhook_endpoint_id),
            body=await async_maybe_transform({"event_type": event_type}, webhook_test_params.WebhookTestParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=WebhookEndpointTestResult,
        )

    def unwrap(
        self,
        payload: str | bytes,
        headers: HeadersLike,
        *,
        secret: str | None = None,
    ) -> UnwrapWebhookEvent:
        """Validates that the given payload was sent by OpenAI and parses the payload."""
        if secret is None:
            secret = self._client.webhook_secret

        self.verify_signature(payload=payload, headers=headers, secret=secret)

        body = payload.decode("utf-8") if isinstance(payload, bytes) else payload
        return cast(
            UnwrapWebhookEvent,
            construct_type(
                type_=UnwrapWebhookEvent,
                value=json.loads(body),
            ),
        )

    def verify_signature(
        self,
        payload: str | bytes,
        headers: HeadersLike,
        *,
        secret: str | None = None,
        tolerance: int = 300,
    ) -> None:
        """Validates whether or not the webhook payload was sent by OpenAI.

        Args:
            payload: The webhook payload
            headers: The webhook headers
            secret: The webhook secret (optional, will use client secret if not provided)
            tolerance: Maximum age of the webhook in seconds (default: 300 = 5 minutes)
        """
        if secret is None:
            secret = self._client.webhook_secret

        if secret is None:
            raise ValueError(
                "The webhook secret must either be set using the env var, OPENAI_WEBHOOK_SECRET, "
                "on the client class, OpenAI(webhook_secret='123'), or passed to this function"
            ) from None

        if not _webhook_signature_matches(payload, headers, secret=secret, tolerance=tolerance):
            raise InvalidWebhookSignatureError("The given webhook signature does not match the expected signature")


class WebhooksWithRawResponse:
    def __init__(self, webhooks: Webhooks) -> None:
        self._webhooks = webhooks

        self.create = _legacy_response.to_raw_response_wrapper(
            webhooks.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            webhooks.retrieve,
        )
        self.update = _legacy_response.to_raw_response_wrapper(
            webhooks.update,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            webhooks.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            webhooks.delete,
        )
        self.rotate_secret = _legacy_response.to_raw_response_wrapper(
            webhooks.rotate_secret,
        )
        self.test = _legacy_response.to_raw_response_wrapper(
            webhooks.test,
        )

    @cached_property
    def event_types(self) -> EventTypesWithRawResponse:
        return EventTypesWithRawResponse(self._webhooks.event_types)


class AsyncWebhooksWithRawResponse:
    def __init__(self, webhooks: AsyncWebhooks) -> None:
        self._webhooks = webhooks

        self.create = _legacy_response.async_to_raw_response_wrapper(
            webhooks.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            webhooks.retrieve,
        )
        self.update = _legacy_response.async_to_raw_response_wrapper(
            webhooks.update,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            webhooks.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            webhooks.delete,
        )
        self.rotate_secret = _legacy_response.async_to_raw_response_wrapper(
            webhooks.rotate_secret,
        )
        self.test = _legacy_response.async_to_raw_response_wrapper(
            webhooks.test,
        )

    @cached_property
    def event_types(self) -> AsyncEventTypesWithRawResponse:
        return AsyncEventTypesWithRawResponse(self._webhooks.event_types)


class WebhooksWithStreamingResponse:
    def __init__(self, webhooks: Webhooks) -> None:
        self._webhooks = webhooks

        self.create = to_streamed_response_wrapper(
            webhooks.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            webhooks.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            webhooks.update,
        )
        self.list = to_streamed_response_wrapper(
            webhooks.list,
        )
        self.delete = to_streamed_response_wrapper(
            webhooks.delete,
        )
        self.rotate_secret = to_streamed_response_wrapper(
            webhooks.rotate_secret,
        )
        self.test = to_streamed_response_wrapper(
            webhooks.test,
        )

    @cached_property
    def event_types(self) -> EventTypesWithStreamingResponse:
        return EventTypesWithStreamingResponse(self._webhooks.event_types)


class AsyncWebhooksWithStreamingResponse:
    def __init__(self, webhooks: AsyncWebhooks) -> None:
        self._webhooks = webhooks

        self.create = async_to_streamed_response_wrapper(
            webhooks.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            webhooks.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            webhooks.update,
        )
        self.list = async_to_streamed_response_wrapper(
            webhooks.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            webhooks.delete,
        )
        self.rotate_secret = async_to_streamed_response_wrapper(
            webhooks.rotate_secret,
        )
        self.test = async_to_streamed_response_wrapper(
            webhooks.test,
        )

    @cached_property
    def event_types(self) -> AsyncEventTypesWithStreamingResponse:
        return AsyncEventTypesWithStreamingResponse(self._webhooks.event_types)
