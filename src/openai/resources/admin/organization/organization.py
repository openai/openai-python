# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ...._compat import cached_property
from .audit_logs import (
    AuditLogs,
    AsyncAuditLogs,
    AuditLogsWithRawResponse,
    AsyncAuditLogsWithRawResponse,
    AuditLogsWithStreamingResponse,
    AsyncAuditLogsWithStreamingResponse,
)
from ...._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["Organization", "AsyncOrganization"]


class Organization(SyncAPIResource):
    @cached_property
    def audit_logs(self) -> AuditLogs:
        """List user actions and configuration changes within this organization."""
        return AuditLogs(self._client)

    @cached_property
    def with_raw_response(self) -> OrganizationWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return OrganizationWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OrganizationWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return OrganizationWithStreamingResponse(self)


class AsyncOrganization(AsyncAPIResource):
    @cached_property
    def audit_logs(self) -> AsyncAuditLogs:
        """List user actions and configuration changes within this organization."""
        return AsyncAuditLogs(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncOrganizationWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncOrganizationWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOrganizationWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncOrganizationWithStreamingResponse(self)


class OrganizationWithRawResponse:
    def __init__(self, organization: Organization) -> None:
        self._organization = organization

    @cached_property
    def audit_logs(self) -> AuditLogsWithRawResponse:
        """List user actions and configuration changes within this organization."""
        return AuditLogsWithRawResponse(self._organization.audit_logs)


class AsyncOrganizationWithRawResponse:
    def __init__(self, organization: AsyncOrganization) -> None:
        self._organization = organization

    @cached_property
    def audit_logs(self) -> AsyncAuditLogsWithRawResponse:
        """List user actions and configuration changes within this organization."""
        return AsyncAuditLogsWithRawResponse(self._organization.audit_logs)


class OrganizationWithStreamingResponse:
    def __init__(self, organization: Organization) -> None:
        self._organization = organization

    @cached_property
    def audit_logs(self) -> AuditLogsWithStreamingResponse:
        """List user actions and configuration changes within this organization."""
        return AuditLogsWithStreamingResponse(self._organization.audit_logs)


class AsyncOrganizationWithStreamingResponse:
    def __init__(self, organization: AsyncOrganization) -> None:
        self._organization = organization

    @cached_property
    def audit_logs(self) -> AsyncAuditLogsWithStreamingResponse:
        """List user actions and configuration changes within this organization."""
        return AsyncAuditLogsWithStreamingResponse(self._organization.audit_logs)
