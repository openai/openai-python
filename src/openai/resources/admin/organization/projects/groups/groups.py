# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ...... import _legacy_response
from .roles import (
    Roles,
    AsyncRoles,
    RolesWithRawResponse,
    AsyncRolesWithRawResponse,
    RolesWithStreamingResponse,
    AsyncRolesWithStreamingResponse,
)
from ......_types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ......_utils import path_template, maybe_transform, async_maybe_transform
from ......_compat import cached_property
from ......_resource import SyncAPIResource, AsyncAPIResource
from ......_response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ......pagination import SyncNextCursorPage, AsyncNextCursorPage
from ......_base_client import AsyncPaginator, make_request_options
from ......types.admin.organization.projects import group_list_params, group_create_params
from ......types.admin.organization.projects.project_group import ProjectGroup
from ......types.admin.organization.projects.group_delete_response import GroupDeleteResponse

__all__ = ["Groups", "AsyncGroups"]


class Groups(SyncAPIResource):
    @cached_property
    def roles(self) -> Roles:
        return Roles(self._client)

    @cached_property
    def with_raw_response(self) -> GroupsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return GroupsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> GroupsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return GroupsWithStreamingResponse(self)

    def create(
        self,
        project_id: str,
        *,
        group_id: str,
        role: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProjectGroup:
        """
        Grants a group access to a project.

        Args:
          group_id: Identifier of the group to add to the project.

          role: Identifier of the project role to grant to the group.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._post(
            path_template("/organization/projects/{project_id}/groups", project_id=project_id),
            body=maybe_transform(
                {
                    "group_id": group_id,
                    "role": role,
                },
                group_create_params.GroupCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectGroup,
        )

    def list(
        self,
        project_id: str,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncNextCursorPage[ProjectGroup]:
        """
        Lists the groups that have access to a project.

        Args:
          after: Cursor for pagination. Provide the ID of the last group from the previous
              response to fetch the next page.

          limit: A limit on the number of project groups to return. Defaults to 20.

          order: Sort order for the returned groups.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get_api_list(
            path_template("/organization/projects/{project_id}/groups", project_id=project_id),
            page=SyncNextCursorPage[ProjectGroup],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                        "order": order,
                    },
                    group_list_params.GroupListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=ProjectGroup,
        )

    def delete(
        self,
        group_id: str,
        *,
        project_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GroupDeleteResponse:
        """
        Revokes a group's access to a project.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not group_id:
            raise ValueError(f"Expected a non-empty value for `group_id` but received {group_id!r}")
        return self._delete(
            path_template(
                "/organization/projects/{project_id}/groups/{group_id}", project_id=project_id, group_id=group_id
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=GroupDeleteResponse,
        )


class AsyncGroups(AsyncAPIResource):
    @cached_property
    def roles(self) -> AsyncRoles:
        return AsyncRoles(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncGroupsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncGroupsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncGroupsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncGroupsWithStreamingResponse(self)

    async def create(
        self,
        project_id: str,
        *,
        group_id: str,
        role: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProjectGroup:
        """
        Grants a group access to a project.

        Args:
          group_id: Identifier of the group to add to the project.

          role: Identifier of the project role to grant to the group.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._post(
            path_template("/organization/projects/{project_id}/groups", project_id=project_id),
            body=await async_maybe_transform(
                {
                    "group_id": group_id,
                    "role": role,
                },
                group_create_params.GroupCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectGroup,
        )

    def list(
        self,
        project_id: str,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[ProjectGroup, AsyncNextCursorPage[ProjectGroup]]:
        """
        Lists the groups that have access to a project.

        Args:
          after: Cursor for pagination. Provide the ID of the last group from the previous
              response to fetch the next page.

          limit: A limit on the number of project groups to return. Defaults to 20.

          order: Sort order for the returned groups.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get_api_list(
            path_template("/organization/projects/{project_id}/groups", project_id=project_id),
            page=AsyncNextCursorPage[ProjectGroup],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                        "order": order,
                    },
                    group_list_params.GroupListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=ProjectGroup,
        )

    async def delete(
        self,
        group_id: str,
        *,
        project_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GroupDeleteResponse:
        """
        Revokes a group's access to a project.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not group_id:
            raise ValueError(f"Expected a non-empty value for `group_id` but received {group_id!r}")
        return await self._delete(
            path_template(
                "/organization/projects/{project_id}/groups/{group_id}", project_id=project_id, group_id=group_id
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=GroupDeleteResponse,
        )


class GroupsWithRawResponse:
    def __init__(self, groups: Groups) -> None:
        self._groups = groups

        self.create = _legacy_response.to_raw_response_wrapper(
            groups.create,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            groups.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            groups.delete,
        )

    @cached_property
    def roles(self) -> RolesWithRawResponse:
        return RolesWithRawResponse(self._groups.roles)


class AsyncGroupsWithRawResponse:
    def __init__(self, groups: AsyncGroups) -> None:
        self._groups = groups

        self.create = _legacy_response.async_to_raw_response_wrapper(
            groups.create,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            groups.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            groups.delete,
        )

    @cached_property
    def roles(self) -> AsyncRolesWithRawResponse:
        return AsyncRolesWithRawResponse(self._groups.roles)


class GroupsWithStreamingResponse:
    def __init__(self, groups: Groups) -> None:
        self._groups = groups

        self.create = to_streamed_response_wrapper(
            groups.create,
        )
        self.list = to_streamed_response_wrapper(
            groups.list,
        )
        self.delete = to_streamed_response_wrapper(
            groups.delete,
        )

    @cached_property
    def roles(self) -> RolesWithStreamingResponse:
        return RolesWithStreamingResponse(self._groups.roles)


class AsyncGroupsWithStreamingResponse:
    def __init__(self, groups: AsyncGroups) -> None:
        self._groups = groups

        self.create = async_to_streamed_response_wrapper(
            groups.create,
        )
        self.list = async_to_streamed_response_wrapper(
            groups.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            groups.delete,
        )

    @cached_property
    def roles(self) -> AsyncRolesWithStreamingResponse:
        return AsyncRolesWithStreamingResponse(self._groups.roles)
