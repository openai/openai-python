# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ...... import _legacy_response
from ......_types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ......_utils import path_template, maybe_transform, async_maybe_transform
from ......_compat import cached_property
from ......_resource import SyncAPIResource, AsyncAPIResource
from ......_response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ......pagination import SyncNextCursorPage, AsyncNextCursorPage
from ......_base_client import AsyncPaginator, make_request_options
from ......types.admin.organization.projects.users import role_list_params, role_create_params
from ......types.admin.organization.projects.users.role_list_response import RoleListResponse
from ......types.admin.organization.projects.users.role_create_response import RoleCreateResponse
from ......types.admin.organization.projects.users.role_delete_response import RoleDeleteResponse

__all__ = ["Roles", "AsyncRoles"]


class Roles(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RolesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return RolesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RolesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return RolesWithStreamingResponse(self)

    def create(
        self,
        user_id: str,
        *,
        project_id: str,
        role_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RoleCreateResponse:
        """
        Assigns a project role to a user within a project.

        Args:
          role_id: Identifier of the role to assign.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not user_id:
            raise ValueError(f"Expected a non-empty value for `user_id` but received {user_id!r}")
        return self._post(
            path_template("/projects/{project_id}/users/{user_id}/roles", project_id=project_id, user_id=user_id),
            body=maybe_transform({"role_id": role_id}, role_create_params.RoleCreateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=RoleCreateResponse,
        )

    def list(
        self,
        user_id: str,
        *,
        project_id: str,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncNextCursorPage[RoleListResponse]:
        """
        Lists the project roles assigned to a user within a project.

        Args:
          after: Cursor for pagination. Provide the value from the previous response's `next`
              field to continue listing project roles.

          limit: A limit on the number of project role assignments to return.

          order: Sort order for the returned project roles.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not user_id:
            raise ValueError(f"Expected a non-empty value for `user_id` but received {user_id!r}")
        return self._get_api_list(
            path_template("/projects/{project_id}/users/{user_id}/roles", project_id=project_id, user_id=user_id),
            page=SyncNextCursorPage[RoleListResponse],
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
                    role_list_params.RoleListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=RoleListResponse,
        )

    def delete(
        self,
        role_id: str,
        *,
        project_id: str,
        user_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RoleDeleteResponse:
        """
        Unassigns a project role from a user within a project.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not user_id:
            raise ValueError(f"Expected a non-empty value for `user_id` but received {user_id!r}")
        if not role_id:
            raise ValueError(f"Expected a non-empty value for `role_id` but received {role_id!r}")
        return self._delete(
            path_template(
                "/projects/{project_id}/users/{user_id}/roles/{role_id}",
                project_id=project_id,
                user_id=user_id,
                role_id=role_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=RoleDeleteResponse,
        )


class AsyncRoles(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRolesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRolesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRolesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncRolesWithStreamingResponse(self)

    async def create(
        self,
        user_id: str,
        *,
        project_id: str,
        role_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RoleCreateResponse:
        """
        Assigns a project role to a user within a project.

        Args:
          role_id: Identifier of the role to assign.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not user_id:
            raise ValueError(f"Expected a non-empty value for `user_id` but received {user_id!r}")
        return await self._post(
            path_template("/projects/{project_id}/users/{user_id}/roles", project_id=project_id, user_id=user_id),
            body=await async_maybe_transform({"role_id": role_id}, role_create_params.RoleCreateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=RoleCreateResponse,
        )

    def list(
        self,
        user_id: str,
        *,
        project_id: str,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[RoleListResponse, AsyncNextCursorPage[RoleListResponse]]:
        """
        Lists the project roles assigned to a user within a project.

        Args:
          after: Cursor for pagination. Provide the value from the previous response's `next`
              field to continue listing project roles.

          limit: A limit on the number of project role assignments to return.

          order: Sort order for the returned project roles.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not user_id:
            raise ValueError(f"Expected a non-empty value for `user_id` but received {user_id!r}")
        return self._get_api_list(
            path_template("/projects/{project_id}/users/{user_id}/roles", project_id=project_id, user_id=user_id),
            page=AsyncNextCursorPage[RoleListResponse],
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
                    role_list_params.RoleListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=RoleListResponse,
        )

    async def delete(
        self,
        role_id: str,
        *,
        project_id: str,
        user_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RoleDeleteResponse:
        """
        Unassigns a project role from a user within a project.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not user_id:
            raise ValueError(f"Expected a non-empty value for `user_id` but received {user_id!r}")
        if not role_id:
            raise ValueError(f"Expected a non-empty value for `role_id` but received {role_id!r}")
        return await self._delete(
            path_template(
                "/projects/{project_id}/users/{user_id}/roles/{role_id}",
                project_id=project_id,
                user_id=user_id,
                role_id=role_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=RoleDeleteResponse,
        )


class RolesWithRawResponse:
    def __init__(self, roles: Roles) -> None:
        self._roles = roles

        self.create = _legacy_response.to_raw_response_wrapper(
            roles.create,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            roles.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            roles.delete,
        )


class AsyncRolesWithRawResponse:
    def __init__(self, roles: AsyncRoles) -> None:
        self._roles = roles

        self.create = _legacy_response.async_to_raw_response_wrapper(
            roles.create,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            roles.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            roles.delete,
        )


class RolesWithStreamingResponse:
    def __init__(self, roles: Roles) -> None:
        self._roles = roles

        self.create = to_streamed_response_wrapper(
            roles.create,
        )
        self.list = to_streamed_response_wrapper(
            roles.list,
        )
        self.delete = to_streamed_response_wrapper(
            roles.delete,
        )


class AsyncRolesWithStreamingResponse:
    def __init__(self, roles: AsyncRoles) -> None:
        self._roles = roles

        self.create = async_to_streamed_response_wrapper(
            roles.create,
        )
        self.list = async_to_streamed_response_wrapper(
            roles.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            roles.delete,
        )
