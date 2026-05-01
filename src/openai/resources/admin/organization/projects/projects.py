# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..... import _legacy_response
from .roles import (
    Roles,
    AsyncRoles,
    RolesWithRawResponse,
    AsyncRolesWithRawResponse,
    RolesWithStreamingResponse,
    AsyncRolesWithStreamingResponse,
)
from .api_keys import (
    APIKeys,
    AsyncAPIKeys,
    APIKeysWithRawResponse,
    AsyncAPIKeysWithRawResponse,
    APIKeysWithStreamingResponse,
    AsyncAPIKeysWithStreamingResponse,
)
from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ....._utils import path_template, maybe_transform, async_maybe_transform
from ....._compat import cached_property
from .rate_limits import (
    RateLimits,
    AsyncRateLimits,
    RateLimitsWithRawResponse,
    AsyncRateLimitsWithRawResponse,
    RateLimitsWithStreamingResponse,
    AsyncRateLimitsWithStreamingResponse,
)
from .users.users import (
    Users,
    AsyncUsers,
    UsersWithRawResponse,
    AsyncUsersWithRawResponse,
    UsersWithStreamingResponse,
    AsyncUsersWithStreamingResponse,
)
from .certificates import (
    Certificates,
    AsyncCertificates,
    CertificatesWithRawResponse,
    AsyncCertificatesWithRawResponse,
    CertificatesWithStreamingResponse,
    AsyncCertificatesWithStreamingResponse,
)
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from .groups.groups import (
    Groups,
    AsyncGroups,
    GroupsWithRawResponse,
    AsyncGroupsWithRawResponse,
    GroupsWithStreamingResponse,
    AsyncGroupsWithStreamingResponse,
)
from .....pagination import SyncConversationCursorPage, AsyncConversationCursorPage
from ....._base_client import AsyncPaginator, make_request_options
from .service_accounts import (
    ServiceAccounts,
    AsyncServiceAccounts,
    ServiceAccountsWithRawResponse,
    AsyncServiceAccountsWithRawResponse,
    ServiceAccountsWithStreamingResponse,
    AsyncServiceAccountsWithStreamingResponse,
)
from .....types.admin.organization import project_list_params, project_create_params, project_update_params
from .....types.admin.organization.project import Project

__all__ = ["Projects", "AsyncProjects"]


class Projects(SyncAPIResource):
    @cached_property
    def users(self) -> Users:
        return Users(self._client)

    @cached_property
    def service_accounts(self) -> ServiceAccounts:
        return ServiceAccounts(self._client)

    @cached_property
    def api_keys(self) -> APIKeys:
        return APIKeys(self._client)

    @cached_property
    def rate_limits(self) -> RateLimits:
        return RateLimits(self._client)

    @cached_property
    def groups(self) -> Groups:
        return Groups(self._client)

    @cached_property
    def roles(self) -> Roles:
        return Roles(self._client)

    @cached_property
    def certificates(self) -> Certificates:
        return Certificates(self._client)

    @cached_property
    def with_raw_response(self) -> ProjectsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return ProjectsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ProjectsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return ProjectsWithStreamingResponse(self)

    def create(
        self,
        *,
        name: str,
        external_key_id: Optional[str] | Omit = omit,
        geography: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Project:
        """Create a new project in the organization.

        Projects can be created and archived,
        but cannot be deleted.

        Args:
          name: The friendly name of the project, this name appears in reports.

          external_key_id: External key ID to associate with the project.

          geography: Create the project with the specified data residency region. Your organization
              must have access to Data residency functionality in order to use. See
              [data residency controls](https://platform.openai.com/docs/guides/your-data#data-residency-controls)
              to review the functionality and limitations of setting this field.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/organization/projects",
            body=maybe_transform(
                {
                    "name": name,
                    "external_key_id": external_key_id,
                    "geography": geography,
                },
                project_create_params.ProjectCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=Project,
        )

    def retrieve(
        self,
        project_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Project:
        """
        Retrieves a project.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get(
            path_template("/organization/projects/{project_id}", project_id=project_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=Project,
        )

    def update(
        self,
        project_id: str,
        *,
        external_key_id: Optional[str] | Omit = omit,
        geography: Optional[str] | Omit = omit,
        name: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Project:
        """
        Modifies a project in the organization.

        Args:
          external_key_id: External key ID to associate with the project.

          geography: Geography for the project.

          name: The updated name of the project, this name appears in reports.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._post(
            path_template("/organization/projects/{project_id}", project_id=project_id),
            body=maybe_transform(
                {
                    "external_key_id": external_key_id,
                    "geography": geography,
                    "name": name,
                },
                project_update_params.ProjectUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=Project,
        )

    def list(
        self,
        *,
        after: str | Omit = omit,
        include_archived: bool | Omit = omit,
        limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncConversationCursorPage[Project]:
        """Returns a list of projects.

        Args:
          after: A cursor for use in pagination.

        `after` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include after=obj_foo in order to
              fetch the next page of the list.

          include_archived: If `true` returns all projects including those that have been `archived`.
              Archived projects are not included by default.

          limit: A limit on the number of objects to be returned. Limit can range between 1 and
              100, and the default is 20.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/organization/projects",
            page=SyncConversationCursorPage[Project],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "include_archived": include_archived,
                        "limit": limit,
                    },
                    project_list_params.ProjectListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=Project,
        )

    def archive(
        self,
        project_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Project:
        """Archives a project in the organization.

        Archived projects cannot be used or
        updated.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._post(
            path_template("/organization/projects/{project_id}/archive", project_id=project_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=Project,
        )


class AsyncProjects(AsyncAPIResource):
    @cached_property
    def users(self) -> AsyncUsers:
        return AsyncUsers(self._client)

    @cached_property
    def service_accounts(self) -> AsyncServiceAccounts:
        return AsyncServiceAccounts(self._client)

    @cached_property
    def api_keys(self) -> AsyncAPIKeys:
        return AsyncAPIKeys(self._client)

    @cached_property
    def rate_limits(self) -> AsyncRateLimits:
        return AsyncRateLimits(self._client)

    @cached_property
    def groups(self) -> AsyncGroups:
        return AsyncGroups(self._client)

    @cached_property
    def roles(self) -> AsyncRoles:
        return AsyncRoles(self._client)

    @cached_property
    def certificates(self) -> AsyncCertificates:
        return AsyncCertificates(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncProjectsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncProjectsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncProjectsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncProjectsWithStreamingResponse(self)

    async def create(
        self,
        *,
        name: str,
        external_key_id: Optional[str] | Omit = omit,
        geography: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Project:
        """Create a new project in the organization.

        Projects can be created and archived,
        but cannot be deleted.

        Args:
          name: The friendly name of the project, this name appears in reports.

          external_key_id: External key ID to associate with the project.

          geography: Create the project with the specified data residency region. Your organization
              must have access to Data residency functionality in order to use. See
              [data residency controls](https://platform.openai.com/docs/guides/your-data#data-residency-controls)
              to review the functionality and limitations of setting this field.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/organization/projects",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "external_key_id": external_key_id,
                    "geography": geography,
                },
                project_create_params.ProjectCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=Project,
        )

    async def retrieve(
        self,
        project_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Project:
        """
        Retrieves a project.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._get(
            path_template("/organization/projects/{project_id}", project_id=project_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=Project,
        )

    async def update(
        self,
        project_id: str,
        *,
        external_key_id: Optional[str] | Omit = omit,
        geography: Optional[str] | Omit = omit,
        name: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Project:
        """
        Modifies a project in the organization.

        Args:
          external_key_id: External key ID to associate with the project.

          geography: Geography for the project.

          name: The updated name of the project, this name appears in reports.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._post(
            path_template("/organization/projects/{project_id}", project_id=project_id),
            body=await async_maybe_transform(
                {
                    "external_key_id": external_key_id,
                    "geography": geography,
                    "name": name,
                },
                project_update_params.ProjectUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=Project,
        )

    def list(
        self,
        *,
        after: str | Omit = omit,
        include_archived: bool | Omit = omit,
        limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[Project, AsyncConversationCursorPage[Project]]:
        """Returns a list of projects.

        Args:
          after: A cursor for use in pagination.

        `after` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include after=obj_foo in order to
              fetch the next page of the list.

          include_archived: If `true` returns all projects including those that have been `archived`.
              Archived projects are not included by default.

          limit: A limit on the number of objects to be returned. Limit can range between 1 and
              100, and the default is 20.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/organization/projects",
            page=AsyncConversationCursorPage[Project],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "include_archived": include_archived,
                        "limit": limit,
                    },
                    project_list_params.ProjectListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=Project,
        )

    async def archive(
        self,
        project_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Project:
        """Archives a project in the organization.

        Archived projects cannot be used or
        updated.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._post(
            path_template("/organization/projects/{project_id}/archive", project_id=project_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=Project,
        )


class ProjectsWithRawResponse:
    def __init__(self, projects: Projects) -> None:
        self._projects = projects

        self.create = _legacy_response.to_raw_response_wrapper(
            projects.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            projects.retrieve,
        )
        self.update = _legacy_response.to_raw_response_wrapper(
            projects.update,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            projects.list,
        )
        self.archive = _legacy_response.to_raw_response_wrapper(
            projects.archive,
        )

    @cached_property
    def users(self) -> UsersWithRawResponse:
        return UsersWithRawResponse(self._projects.users)

    @cached_property
    def service_accounts(self) -> ServiceAccountsWithRawResponse:
        return ServiceAccountsWithRawResponse(self._projects.service_accounts)

    @cached_property
    def api_keys(self) -> APIKeysWithRawResponse:
        return APIKeysWithRawResponse(self._projects.api_keys)

    @cached_property
    def rate_limits(self) -> RateLimitsWithRawResponse:
        return RateLimitsWithRawResponse(self._projects.rate_limits)

    @cached_property
    def groups(self) -> GroupsWithRawResponse:
        return GroupsWithRawResponse(self._projects.groups)

    @cached_property
    def roles(self) -> RolesWithRawResponse:
        return RolesWithRawResponse(self._projects.roles)

    @cached_property
    def certificates(self) -> CertificatesWithRawResponse:
        return CertificatesWithRawResponse(self._projects.certificates)


class AsyncProjectsWithRawResponse:
    def __init__(self, projects: AsyncProjects) -> None:
        self._projects = projects

        self.create = _legacy_response.async_to_raw_response_wrapper(
            projects.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            projects.retrieve,
        )
        self.update = _legacy_response.async_to_raw_response_wrapper(
            projects.update,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            projects.list,
        )
        self.archive = _legacy_response.async_to_raw_response_wrapper(
            projects.archive,
        )

    @cached_property
    def users(self) -> AsyncUsersWithRawResponse:
        return AsyncUsersWithRawResponse(self._projects.users)

    @cached_property
    def service_accounts(self) -> AsyncServiceAccountsWithRawResponse:
        return AsyncServiceAccountsWithRawResponse(self._projects.service_accounts)

    @cached_property
    def api_keys(self) -> AsyncAPIKeysWithRawResponse:
        return AsyncAPIKeysWithRawResponse(self._projects.api_keys)

    @cached_property
    def rate_limits(self) -> AsyncRateLimitsWithRawResponse:
        return AsyncRateLimitsWithRawResponse(self._projects.rate_limits)

    @cached_property
    def groups(self) -> AsyncGroupsWithRawResponse:
        return AsyncGroupsWithRawResponse(self._projects.groups)

    @cached_property
    def roles(self) -> AsyncRolesWithRawResponse:
        return AsyncRolesWithRawResponse(self._projects.roles)

    @cached_property
    def certificates(self) -> AsyncCertificatesWithRawResponse:
        return AsyncCertificatesWithRawResponse(self._projects.certificates)


class ProjectsWithStreamingResponse:
    def __init__(self, projects: Projects) -> None:
        self._projects = projects

        self.create = to_streamed_response_wrapper(
            projects.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            projects.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            projects.update,
        )
        self.list = to_streamed_response_wrapper(
            projects.list,
        )
        self.archive = to_streamed_response_wrapper(
            projects.archive,
        )

    @cached_property
    def users(self) -> UsersWithStreamingResponse:
        return UsersWithStreamingResponse(self._projects.users)

    @cached_property
    def service_accounts(self) -> ServiceAccountsWithStreamingResponse:
        return ServiceAccountsWithStreamingResponse(self._projects.service_accounts)

    @cached_property
    def api_keys(self) -> APIKeysWithStreamingResponse:
        return APIKeysWithStreamingResponse(self._projects.api_keys)

    @cached_property
    def rate_limits(self) -> RateLimitsWithStreamingResponse:
        return RateLimitsWithStreamingResponse(self._projects.rate_limits)

    @cached_property
    def groups(self) -> GroupsWithStreamingResponse:
        return GroupsWithStreamingResponse(self._projects.groups)

    @cached_property
    def roles(self) -> RolesWithStreamingResponse:
        return RolesWithStreamingResponse(self._projects.roles)

    @cached_property
    def certificates(self) -> CertificatesWithStreamingResponse:
        return CertificatesWithStreamingResponse(self._projects.certificates)


class AsyncProjectsWithStreamingResponse:
    def __init__(self, projects: AsyncProjects) -> None:
        self._projects = projects

        self.create = async_to_streamed_response_wrapper(
            projects.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            projects.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            projects.update,
        )
        self.list = async_to_streamed_response_wrapper(
            projects.list,
        )
        self.archive = async_to_streamed_response_wrapper(
            projects.archive,
        )

    @cached_property
    def users(self) -> AsyncUsersWithStreamingResponse:
        return AsyncUsersWithStreamingResponse(self._projects.users)

    @cached_property
    def service_accounts(self) -> AsyncServiceAccountsWithStreamingResponse:
        return AsyncServiceAccountsWithStreamingResponse(self._projects.service_accounts)

    @cached_property
    def api_keys(self) -> AsyncAPIKeysWithStreamingResponse:
        return AsyncAPIKeysWithStreamingResponse(self._projects.api_keys)

    @cached_property
    def rate_limits(self) -> AsyncRateLimitsWithStreamingResponse:
        return AsyncRateLimitsWithStreamingResponse(self._projects.rate_limits)

    @cached_property
    def groups(self) -> AsyncGroupsWithStreamingResponse:
        return AsyncGroupsWithStreamingResponse(self._projects.groups)

    @cached_property
    def roles(self) -> AsyncRolesWithStreamingResponse:
        return AsyncRolesWithStreamingResponse(self._projects.roles)

    @cached_property
    def certificates(self) -> AsyncCertificatesWithStreamingResponse:
        return AsyncCertificatesWithStreamingResponse(self._projects.certificates)
