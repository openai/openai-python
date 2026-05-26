# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from .organization.organization import (
    Organization,
    AsyncOrganization,
    OrganizationWithRawResponse,
    AsyncOrganizationWithRawResponse,
    OrganizationWithStreamingResponse,
    AsyncOrganizationWithStreamingResponse,
)

__all__ = ["Admin", "AsyncAdmin"]


class Admin(SyncAPIResource):
    @cached_property
    def organization(self) -> Organization:
        return Organization(self._client)

    @cached_property
    def with_raw_response(self) -> AdminWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AdminWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AdminWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AdminWithStreamingResponse(self)


class AsyncAdmin(AsyncAPIResource):
    @cached_property
    def organization(self) -> AsyncOrganization:
        return AsyncOrganization(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncAdminWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAdminWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAdminWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncAdminWithStreamingResponse(self)


class AdminWithRawResponse:
    def __init__(self, admin: Admin) -> None:
        self._admin = admin

    @cached_property
    def organization(self) -> OrganizationWithRawResponse:
        return OrganizationWithRawResponse(self._admin.organization)


class AsyncAdminWithRawResponse:
    def __init__(self, admin: AsyncAdmin) -> None:
        self._admin = admin

    @cached_property
    def organization(self) -> AsyncOrganizationWithRawResponse:
        return AsyncOrganizationWithRawResponse(self._admin.organization)


class AdminWithStreamingResponse:
    def __init__(self, admin: Admin) -> None:
        self._admin = admin

    @cached_property
    def organization(self) -> OrganizationWithStreamingResponse:
        return OrganizationWithStreamingResponse(self._admin.organization)


class AsyncAdminWithStreamingResponse:
    def __init__(self, admin: AsyncAdmin) -> None:
        self._admin = admin

    @cached_property
    def organization(self) -> AsyncOrganizationWithStreamingResponse:
        return AsyncOrganizationWithStreamingResponse(self._admin.organization)
