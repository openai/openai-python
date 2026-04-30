# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
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
from ....types.admin.organization import invite_list_params, invite_create_params
from ....types.admin.organization.invite import Invite
from ....types.admin.organization.invite_delete_response import InviteDeleteResponse

__all__ = ["Invites", "AsyncInvites"]


class Invites(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> InvitesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return InvitesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> InvitesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return InvitesWithStreamingResponse(self)

    def create(
        self,
        *,
        email: str,
        role: Literal["reader", "owner"],
        projects: Iterable[invite_create_params.Project] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Invite:
        """Create an invite for a user to the organization.

        The invite must be accepted by
        the user before they have access to the organization.

        Args:
          email: Send an email to this address

          role: `owner` or `reader`

          projects: An array of projects to which membership is granted at the same time the org
              invite is accepted. If omitted, the user will be invited to the default project
              for compatibility with legacy behavior.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/organization/invites",
            body=maybe_transform(
                {
                    "email": email,
                    "role": role,
                    "projects": projects,
                },
                invite_create_params.InviteCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=Invite,
        )

    def retrieve(
        self,
        invite_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Invite:
        """
        Retrieves an invite.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not invite_id:
            raise ValueError(f"Expected a non-empty value for `invite_id` but received {invite_id!r}")
        return self._get(
            path_template("/organization/invites/{invite_id}", invite_id=invite_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=Invite,
        )

    def list(
        self,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncConversationCursorPage[Invite]:
        """
        Returns a list of invites in the organization.

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
        return self._get_api_list(
            "/organization/invites",
            page=SyncConversationCursorPage[Invite],
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
                    invite_list_params.InviteListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=Invite,
        )

    def delete(
        self,
        invite_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> InviteDeleteResponse:
        """Delete an invite.

        If the invite has already been accepted, it cannot be deleted.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not invite_id:
            raise ValueError(f"Expected a non-empty value for `invite_id` but received {invite_id!r}")
        return self._delete(
            path_template("/organization/invites/{invite_id}", invite_id=invite_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=InviteDeleteResponse,
        )


class AsyncInvites(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncInvitesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncInvitesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncInvitesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncInvitesWithStreamingResponse(self)

    async def create(
        self,
        *,
        email: str,
        role: Literal["reader", "owner"],
        projects: Iterable[invite_create_params.Project] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Invite:
        """Create an invite for a user to the organization.

        The invite must be accepted by
        the user before they have access to the organization.

        Args:
          email: Send an email to this address

          role: `owner` or `reader`

          projects: An array of projects to which membership is granted at the same time the org
              invite is accepted. If omitted, the user will be invited to the default project
              for compatibility with legacy behavior.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/organization/invites",
            body=await async_maybe_transform(
                {
                    "email": email,
                    "role": role,
                    "projects": projects,
                },
                invite_create_params.InviteCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=Invite,
        )

    async def retrieve(
        self,
        invite_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Invite:
        """
        Retrieves an invite.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not invite_id:
            raise ValueError(f"Expected a non-empty value for `invite_id` but received {invite_id!r}")
        return await self._get(
            path_template("/organization/invites/{invite_id}", invite_id=invite_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=Invite,
        )

    def list(
        self,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[Invite, AsyncConversationCursorPage[Invite]]:
        """
        Returns a list of invites in the organization.

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
        return self._get_api_list(
            "/organization/invites",
            page=AsyncConversationCursorPage[Invite],
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
                    invite_list_params.InviteListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=Invite,
        )

    async def delete(
        self,
        invite_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> InviteDeleteResponse:
        """Delete an invite.

        If the invite has already been accepted, it cannot be deleted.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not invite_id:
            raise ValueError(f"Expected a non-empty value for `invite_id` but received {invite_id!r}")
        return await self._delete(
            path_template("/organization/invites/{invite_id}", invite_id=invite_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=InviteDeleteResponse,
        )


class InvitesWithRawResponse:
    def __init__(self, invites: Invites) -> None:
        self._invites = invites

        self.create = _legacy_response.to_raw_response_wrapper(
            invites.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            invites.retrieve,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            invites.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            invites.delete,
        )


class AsyncInvitesWithRawResponse:
    def __init__(self, invites: AsyncInvites) -> None:
        self._invites = invites

        self.create = _legacy_response.async_to_raw_response_wrapper(
            invites.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            invites.retrieve,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            invites.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            invites.delete,
        )


class InvitesWithStreamingResponse:
    def __init__(self, invites: Invites) -> None:
        self._invites = invites

        self.create = to_streamed_response_wrapper(
            invites.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            invites.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            invites.list,
        )
        self.delete = to_streamed_response_wrapper(
            invites.delete,
        )


class AsyncInvitesWithStreamingResponse:
    def __init__(self, invites: AsyncInvites) -> None:
        self._invites = invites

        self.create = async_to_streamed_response_wrapper(
            invites.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            invites.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            invites.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            invites.delete,
        )
