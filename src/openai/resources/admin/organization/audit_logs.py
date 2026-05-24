# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from .... import _legacy_response
from ...._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from ...._utils import maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ....pagination import SyncConversationCursorPage, AsyncConversationCursorPage
from ...._base_client import AsyncPaginator, make_request_options
from ....types.admin.organization import audit_log_list_params
from ....types.admin.organization.audit_log_list_response import AuditLogListResponse

__all__ = ["AuditLogs", "AsyncAuditLogs"]


class AuditLogs(SyncAPIResource):
    """List user actions and configuration changes within this organization."""

    @cached_property
    def with_raw_response(self) -> AuditLogsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AuditLogsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AuditLogsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AuditLogsWithStreamingResponse(self)

    def list(
        self,
        *,
        actor_emails: SequenceNotStr[str] | Omit = omit,
        actor_ids: SequenceNotStr[str] | Omit = omit,
        after: str | Omit = omit,
        before: str | Omit = omit,
        effective_at: audit_log_list_params.EffectiveAt | Omit = omit,
        event_types: List[
            Literal[
                "api_key.created",
                "api_key.updated",
                "api_key.deleted",
                "certificate.created",
                "certificate.updated",
                "certificate.deleted",
                "certificates.activated",
                "certificates.deactivated",
                "checkpoint.permission.created",
                "checkpoint.permission.deleted",
                "external_key.registered",
                "external_key.removed",
                "group.created",
                "group.updated",
                "group.deleted",
                "invite.sent",
                "invite.accepted",
                "invite.deleted",
                "ip_allowlist.created",
                "ip_allowlist.updated",
                "ip_allowlist.deleted",
                "ip_allowlist.config.activated",
                "ip_allowlist.config.deactivated",
                "login.succeeded",
                "login.failed",
                "logout.succeeded",
                "logout.failed",
                "organization.updated",
                "project.created",
                "project.updated",
                "project.archived",
                "project.deleted",
                "rate_limit.updated",
                "rate_limit.deleted",
                "resource.deleted",
                "tunnel.created",
                "tunnel.updated",
                "tunnel.deleted",
                "role.created",
                "role.updated",
                "role.deleted",
                "role.assignment.created",
                "role.assignment.deleted",
                "scim.enabled",
                "scim.disabled",
                "service_account.created",
                "service_account.updated",
                "service_account.deleted",
                "user.added",
                "user.updated",
                "user.deleted",
            ]
        ]
        | Omit = omit,
        limit: int | Omit = omit,
        project_ids: SequenceNotStr[str] | Omit = omit,
        resource_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncConversationCursorPage[AuditLogListResponse]:
        """
        List user actions and configuration changes within this organization.

        Args:
          actor_emails: Return only events performed by users with these emails.

          actor_ids: Return only events performed by these actors. Can be a user ID, a service
              account ID, or an api key tracking ID.

          after: A cursor for use in pagination. `after` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include after=obj_foo in order to
              fetch the next page of the list.

          before: A cursor for use in pagination. `before` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              starting with obj_foo, your subsequent call can include before=obj_foo in order
              to fetch the previous page of the list.

          effective_at: Return only events whose `effective_at` (Unix seconds) is in this range.

          event_types: Return only events with a `type` in one of these values. For example,
              `project.created`. For all options, see the documentation for the
              [audit log object](https://platform.openai.com/docs/api-reference/audit-logs/object).

          limit: A limit on the number of objects to be returned. Limit can range between 1 and
              100, and the default is 20.

          project_ids: Return only events for these projects.

          resource_ids: Return only events performed on these targets. For example, a project ID
              updated.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/organization/audit_logs",
            page=SyncConversationCursorPage[AuditLogListResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "actor_emails": actor_emails,
                        "actor_ids": actor_ids,
                        "after": after,
                        "before": before,
                        "effective_at": effective_at,
                        "event_types": event_types,
                        "limit": limit,
                        "project_ids": project_ids,
                        "resource_ids": resource_ids,
                    },
                    audit_log_list_params.AuditLogListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=AuditLogListResponse,
        )


class AsyncAuditLogs(AsyncAPIResource):
    """List user actions and configuration changes within this organization."""

    @cached_property
    def with_raw_response(self) -> AsyncAuditLogsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAuditLogsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAuditLogsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncAuditLogsWithStreamingResponse(self)

    def list(
        self,
        *,
        actor_emails: SequenceNotStr[str] | Omit = omit,
        actor_ids: SequenceNotStr[str] | Omit = omit,
        after: str | Omit = omit,
        before: str | Omit = omit,
        effective_at: audit_log_list_params.EffectiveAt | Omit = omit,
        event_types: List[
            Literal[
                "api_key.created",
                "api_key.updated",
                "api_key.deleted",
                "certificate.created",
                "certificate.updated",
                "certificate.deleted",
                "certificates.activated",
                "certificates.deactivated",
                "checkpoint.permission.created",
                "checkpoint.permission.deleted",
                "external_key.registered",
                "external_key.removed",
                "group.created",
                "group.updated",
                "group.deleted",
                "invite.sent",
                "invite.accepted",
                "invite.deleted",
                "ip_allowlist.created",
                "ip_allowlist.updated",
                "ip_allowlist.deleted",
                "ip_allowlist.config.activated",
                "ip_allowlist.config.deactivated",
                "login.succeeded",
                "login.failed",
                "logout.succeeded",
                "logout.failed",
                "organization.updated",
                "project.created",
                "project.updated",
                "project.archived",
                "project.deleted",
                "rate_limit.updated",
                "rate_limit.deleted",
                "resource.deleted",
                "tunnel.created",
                "tunnel.updated",
                "tunnel.deleted",
                "role.created",
                "role.updated",
                "role.deleted",
                "role.assignment.created",
                "role.assignment.deleted",
                "scim.enabled",
                "scim.disabled",
                "service_account.created",
                "service_account.updated",
                "service_account.deleted",
                "user.added",
                "user.updated",
                "user.deleted",
            ]
        ]
        | Omit = omit,
        limit: int | Omit = omit,
        project_ids: SequenceNotStr[str] | Omit = omit,
        resource_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[AuditLogListResponse, AsyncConversationCursorPage[AuditLogListResponse]]:
        """
        List user actions and configuration changes within this organization.

        Args:
          actor_emails: Return only events performed by users with these emails.

          actor_ids: Return only events performed by these actors. Can be a user ID, a service
              account ID, or an api key tracking ID.

          after: A cursor for use in pagination. `after` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include after=obj_foo in order to
              fetch the next page of the list.

          before: A cursor for use in pagination. `before` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              starting with obj_foo, your subsequent call can include before=obj_foo in order
              to fetch the previous page of the list.

          effective_at: Return only events whose `effective_at` (Unix seconds) is in this range.

          event_types: Return only events with a `type` in one of these values. For example,
              `project.created`. For all options, see the documentation for the
              [audit log object](https://platform.openai.com/docs/api-reference/audit-logs/object).

          limit: A limit on the number of objects to be returned. Limit can range between 1 and
              100, and the default is 20.

          project_ids: Return only events for these projects.

          resource_ids: Return only events performed on these targets. For example, a project ID
              updated.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/organization/audit_logs",
            page=AsyncConversationCursorPage[AuditLogListResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "actor_emails": actor_emails,
                        "actor_ids": actor_ids,
                        "after": after,
                        "before": before,
                        "effective_at": effective_at,
                        "event_types": event_types,
                        "limit": limit,
                        "project_ids": project_ids,
                        "resource_ids": resource_ids,
                    },
                    audit_log_list_params.AuditLogListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=AuditLogListResponse,
        )


class AuditLogsWithRawResponse:
    def __init__(self, audit_logs: AuditLogs) -> None:
        self._audit_logs = audit_logs

        self.list = _legacy_response.to_raw_response_wrapper(
            audit_logs.list,
        )


class AsyncAuditLogsWithRawResponse:
    def __init__(self, audit_logs: AsyncAuditLogs) -> None:
        self._audit_logs = audit_logs

        self.list = _legacy_response.async_to_raw_response_wrapper(
            audit_logs.list,
        )


class AuditLogsWithStreamingResponse:
    def __init__(self, audit_logs: AuditLogs) -> None:
        self._audit_logs = audit_logs

        self.list = to_streamed_response_wrapper(
            audit_logs.list,
        )


class AsyncAuditLogsWithStreamingResponse:
    def __init__(self, audit_logs: AsyncAuditLogs) -> None:
        self._audit_logs = audit_logs

        self.list = async_to_streamed_response_wrapper(
            audit_logs.list,
        )
