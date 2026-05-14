# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..... import _legacy_response
from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ....._utils import path_template, maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from .....pagination import SyncNextCursorPage, AsyncNextCursorPage
from ....._base_client import AsyncPaginator, make_request_options
from .....types.admin.organization.groups import user_list_params, user_create_params
from .....types.admin.organization.groups.user_create_response import UserCreateResponse
from .....types.admin.organization.groups.user_delete_response import UserDeleteResponse
from .....types.admin.organization.groups.organization_group_user import OrganizationGroupUser

__all__ = ["Users", "AsyncUsers"]


class Users(SyncAPIResource):
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
        group_id: str,
        *,
        user_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserCreateResponse:
        """
        Adds a user to a group.

        Args:
          user_id: Identifier of the user to add to the group.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not group_id:
            raise ValueError(f"Expected a non-empty value for `group_id` but received {group_id!r}")
        return self._post(
            path_template("/organization/groups/{group_id}/users", group_id=group_id),
            body=maybe_transform({"user_id": user_id}, user_create_params.UserCreateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=UserCreateResponse,
        )

    def list(
        self,
        group_id: str,
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
    ) -> SyncNextCursorPage[OrganizationGroupUser]:
        """
        Lists the users assigned to a group.

        Args:
          after: A cursor for use in pagination. Provide the ID of the last user from the
              previous list response to retrieve the next page.

          limit: A limit on the number of users to be returned. Limit can range between 0 and
              1000, and the default is 100.

          order: Specifies the sort order of users in the list.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not group_id:
            raise ValueError(f"Expected a non-empty value for `group_id` but received {group_id!r}")
        return self._get_api_list(
            path_template("/organization/groups/{group_id}/users", group_id=group_id),
            page=SyncNextCursorPage[OrganizationGroupUser],
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
                    user_list_params.UserListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=OrganizationGroupUser,
        )

    def delete(
        self,
        user_id: str,
        *,
        group_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserDeleteResponse:
        """
        Removes a user from a group.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not group_id:
            raise ValueError(f"Expected a non-empty value for `group_id` but received {group_id!r}")
        if not user_id:
            raise ValueError(f"Expected a non-empty value for `user_id` but received {user_id!r}")
        return self._delete(
            path_template("/organization/groups/{group_id}/users/{user_id}", group_id=group_id, user_id=user_id),
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
        group_id: str,
        *,
        user_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserCreateResponse:
        """
        Adds a user to a group.

        Args:
          user_id: Identifier of the user to add to the group.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not group_id:
            raise ValueError(f"Expected a non-empty value for `group_id` but received {group_id!r}")
        return await self._post(
            path_template("/organization/groups/{group_id}/users", group_id=group_id),
            body=await async_maybe_transform({"user_id": user_id}, user_create_params.UserCreateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=UserCreateResponse,
        )

    def list(
        self,
        group_id: str,
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
    ) -> AsyncPaginator[OrganizationGroupUser, AsyncNextCursorPage[OrganizationGroupUser]]:
        """
        Lists the users assigned to a group.

        Args:
          after: A cursor for use in pagination. Provide the ID of the last user from the
              previous list response to retrieve the next page.

          limit: A limit on the number of users to be returned. Limit can range between 0 and
              1000, and the default is 100.

          order: Specifies the sort order of users in the list.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not group_id:
            raise ValueError(f"Expected a non-empty value for `group_id` but received {group_id!r}")
        return self._get_api_list(
            path_template("/organization/groups/{group_id}/users", group_id=group_id),
            page=AsyncNextCursorPage[OrganizationGroupUser],
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
                    user_list_params.UserListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=OrganizationGroupUser,
        )

    async def delete(
        self,
        user_id: str,
        *,
        group_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserDeleteResponse:
        """
        Removes a user from a group.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not group_id:
            raise ValueError(f"Expected a non-empty value for `group_id` but received {group_id!r}")
        if not user_id:
            raise ValueError(f"Expected a non-empty value for `user_id` but received {user_id!r}")
        return await self._delete(
            path_template("/organization/groups/{group_id}/users/{user_id}", group_id=group_id, user_id=user_id),
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
        self.list = _legacy_response.to_raw_response_wrapper(
            users.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            users.delete,
        )


class AsyncUsersWithRawResponse:
    def __init__(self, users: AsyncUsers) -> None:
        self._users = users

        self.create = _legacy_response.async_to_raw_response_wrapper(
            users.create,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            users.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            users.delete,
        )


class UsersWithStreamingResponse:
    def __init__(self, users: Users) -> None:
        self._users = users

        self.create = to_streamed_response_wrapper(
            users.create,
        )
        self.list = to_streamed_response_wrapper(
            users.list,
        )
        self.delete = to_streamed_response_wrapper(
            users.delete,
        )


class AsyncUsersWithStreamingResponse:
    def __init__(self, users: AsyncUsers) -> None:
        self._users = users

        self.create = async_to_streamed_response_wrapper(
            users.create,
        )
        self.list = async_to_streamed_response_wrapper(
            users.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            users.delete,
        )
