# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

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
from ......pagination import SyncConversationCursorPage, AsyncConversationCursorPage
from ......_base_client import AsyncPaginator, make_request_options
from ......types.admin.organization.projects import user_list_params, user_create_params, user_update_params
from ......types.admin.organization.projects.project_user import ProjectUser
from ......types.admin.organization.projects.user_delete_response import UserDeleteResponse

__all__ = ["Users", "AsyncUsers"]


class Users(SyncAPIResource):
    @cached_property
    def roles(self) -> Roles:
        return Roles(self._client)

    @cached_property
    def with_raw_response(self) -> UsersWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return UsersWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UsersWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return UsersWithStreamingResponse(self)

    def create(
        self,
        project_id: str,
        *,
        role: str,
        email: Optional[str] | Omit = omit,
        user_id: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProjectUser:
        """Adds a user to the project.

        Users must already be members of the organization to
        be added to a project.

        Args:
          role: `owner` or `member`

          email: Email of the user to add.

          user_id: The ID of the user.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._post(
            path_template("/organization/projects/{project_id}/users", project_id=project_id),
            body=maybe_transform(
                {
                    "role": role,
                    "email": email,
                    "user_id": user_id,
                },
                user_create_params.UserCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectUser,
        )

    def retrieve(
        self,
        user_id: str,
        *,
        project_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProjectUser:
        """
        Retrieves a user in the project.

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
        return self._get(
            path_template(
                "/organization/projects/{project_id}/users/{user_id}", project_id=project_id, user_id=user_id
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectUser,
        )

    def update(
        self,
        user_id: str,
        *,
        project_id: str,
        role: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProjectUser:
        """
        Modifies a user's role in the project.

        Args:
          role: `owner` or `member`

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
            path_template(
                "/organization/projects/{project_id}/users/{user_id}", project_id=project_id, user_id=user_id
            ),
            body=maybe_transform({"role": role}, user_update_params.UserUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectUser,
        )

    def list(
        self,
        project_id: str,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncConversationCursorPage[ProjectUser]:
        """
        Returns a list of users in the project.

        Args:
          after: A cursor for use in pagination. `after` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include after=obj_foo in order to
              fetch the next page of the list.

          limit: A limit on the number of objects to be returned. Limit can range between 1 and
              100, and the default is 20.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get_api_list(
            path_template("/organization/projects/{project_id}/users", project_id=project_id),
            page=SyncConversationCursorPage[ProjectUser],
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
                    user_list_params.UserListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=ProjectUser,
        )

    def delete(
        self,
        user_id: str,
        *,
        project_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserDeleteResponse:
        """
        Deletes a user from the project.

        Returns confirmation of project user deletion, or an error if the project is
        archived (archived projects have no users).

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
        return self._delete(
            path_template(
                "/organization/projects/{project_id}/users/{user_id}", project_id=project_id, user_id=user_id
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=UserDeleteResponse,
        )


class AsyncUsers(AsyncAPIResource):
    @cached_property
    def roles(self) -> AsyncRoles:
        return AsyncRoles(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncUsersWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncUsersWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUsersWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncUsersWithStreamingResponse(self)

    async def create(
        self,
        project_id: str,
        *,
        role: str,
        email: Optional[str] | Omit = omit,
        user_id: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProjectUser:
        """Adds a user to the project.

        Users must already be members of the organization to
        be added to a project.

        Args:
          role: `owner` or `member`

          email: Email of the user to add.

          user_id: The ID of the user.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._post(
            path_template("/organization/projects/{project_id}/users", project_id=project_id),
            body=await async_maybe_transform(
                {
                    "role": role,
                    "email": email,
                    "user_id": user_id,
                },
                user_create_params.UserCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectUser,
        )

    async def retrieve(
        self,
        user_id: str,
        *,
        project_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProjectUser:
        """
        Retrieves a user in the project.

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
        return await self._get(
            path_template(
                "/organization/projects/{project_id}/users/{user_id}", project_id=project_id, user_id=user_id
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectUser,
        )

    async def update(
        self,
        user_id: str,
        *,
        project_id: str,
        role: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProjectUser:
        """
        Modifies a user's role in the project.

        Args:
          role: `owner` or `member`

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
            path_template(
                "/organization/projects/{project_id}/users/{user_id}", project_id=project_id, user_id=user_id
            ),
            body=await async_maybe_transform({"role": role}, user_update_params.UserUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectUser,
        )

    def list(
        self,
        project_id: str,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[ProjectUser, AsyncConversationCursorPage[ProjectUser]]:
        """
        Returns a list of users in the project.

        Args:
          after: A cursor for use in pagination. `after` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include after=obj_foo in order to
              fetch the next page of the list.

          limit: A limit on the number of objects to be returned. Limit can range between 1 and
              100, and the default is 20.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get_api_list(
            path_template("/organization/projects/{project_id}/users", project_id=project_id),
            page=AsyncConversationCursorPage[ProjectUser],
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
                    user_list_params.UserListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=ProjectUser,
        )

    async def delete(
        self,
        user_id: str,
        *,
        project_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserDeleteResponse:
        """
        Deletes a user from the project.

        Returns confirmation of project user deletion, or an error if the project is
        archived (archived projects have no users).

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
        return await self._delete(
            path_template(
                "/organization/projects/{project_id}/users/{user_id}", project_id=project_id, user_id=user_id
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=UserDeleteResponse,
        )


class UsersWithRawResponse:
    def __init__(self, users: Users) -> None:
        self._users = users

        self.create = _legacy_response.to_raw_response_wrapper(
            users.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            users.retrieve,
        )
        self.update = _legacy_response.to_raw_response_wrapper(
            users.update,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            users.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            users.delete,
        )

    @cached_property
    def roles(self) -> RolesWithRawResponse:
        return RolesWithRawResponse(self._users.roles)


class AsyncUsersWithRawResponse:
    def __init__(self, users: AsyncUsers) -> None:
        self._users = users

        self.create = _legacy_response.async_to_raw_response_wrapper(
            users.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            users.retrieve,
        )
        self.update = _legacy_response.async_to_raw_response_wrapper(
            users.update,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            users.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            users.delete,
        )

    @cached_property
    def roles(self) -> AsyncRolesWithRawResponse:
        return AsyncRolesWithRawResponse(self._users.roles)


class UsersWithStreamingResponse:
    def __init__(self, users: Users) -> None:
        self._users = users

        self.create = to_streamed_response_wrapper(
            users.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            users.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            users.update,
        )
        self.list = to_streamed_response_wrapper(
            users.list,
        )
        self.delete = to_streamed_response_wrapper(
            users.delete,
        )

    @cached_property
    def roles(self) -> RolesWithStreamingResponse:
        return RolesWithStreamingResponse(self._users.roles)


class AsyncUsersWithStreamingResponse:
    def __init__(self, users: AsyncUsers) -> None:
        self._users = users

        self.create = async_to_streamed_response_wrapper(
            users.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            users.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            users.update,
        )
        self.list = async_to_streamed_response_wrapper(
            users.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            users.delete,
        )

    @cached_property
    def roles(self) -> AsyncRolesWithStreamingResponse:
        return AsyncRolesWithStreamingResponse(self._users.roles)
