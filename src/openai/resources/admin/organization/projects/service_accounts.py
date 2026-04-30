# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..... import _legacy_response
from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ....._utils import path_template, maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from .....pagination import SyncConversationCursorPage, AsyncConversationCursorPage
from ....._base_client import AsyncPaginator, make_request_options
from .....types.admin.organization.projects import service_account_list_params, service_account_create_params
from .....types.admin.organization.projects.project_service_account import ProjectServiceAccount
from .....types.admin.organization.projects.service_account_create_response import ServiceAccountCreateResponse
from .....types.admin.organization.projects.service_account_delete_response import ServiceAccountDeleteResponse

__all__ = ["ServiceAccounts", "AsyncServiceAccounts"]


class ServiceAccounts(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ServiceAccountsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return ServiceAccountsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ServiceAccountsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return ServiceAccountsWithStreamingResponse(self)

    def create(
        self,
        project_id: str,
        *,
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ServiceAccountCreateResponse:
        """Creates a new service account in the project.

        This also returns an unredacted
        API key for the service account.

        Args:
          name: The name of the service account being created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._post(
            path_template("/organization/projects/{project_id}/service_accounts", project_id=project_id),
            body=maybe_transform({"name": name}, service_account_create_params.ServiceAccountCreateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ServiceAccountCreateResponse,
        )

    def retrieve(
        self,
        service_account_id: str,
        *,
        project_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProjectServiceAccount:
        """
        Retrieves a service account in the project.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not service_account_id:
            raise ValueError(f"Expected a non-empty value for `service_account_id` but received {service_account_id!r}")
        return self._get(
            path_template(
                "/organization/projects/{project_id}/service_accounts/{service_account_id}",
                project_id=project_id,
                service_account_id=service_account_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectServiceAccount,
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
    ) -> SyncConversationCursorPage[ProjectServiceAccount]:
        """
        Returns a list of service accounts in the project.

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
            path_template("/organization/projects/{project_id}/service_accounts", project_id=project_id),
            page=SyncConversationCursorPage[ProjectServiceAccount],
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
                    service_account_list_params.ServiceAccountListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=ProjectServiceAccount,
        )

    def delete(
        self,
        service_account_id: str,
        *,
        project_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ServiceAccountDeleteResponse:
        """
        Deletes a service account from the project.

        Returns confirmation of service account deletion, or an error if the project is
        archived (archived projects have no service accounts).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not service_account_id:
            raise ValueError(f"Expected a non-empty value for `service_account_id` but received {service_account_id!r}")
        return self._delete(
            path_template(
                "/organization/projects/{project_id}/service_accounts/{service_account_id}",
                project_id=project_id,
                service_account_id=service_account_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ServiceAccountDeleteResponse,
        )


class AsyncServiceAccounts(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncServiceAccountsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncServiceAccountsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncServiceAccountsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncServiceAccountsWithStreamingResponse(self)

    async def create(
        self,
        project_id: str,
        *,
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ServiceAccountCreateResponse:
        """Creates a new service account in the project.

        This also returns an unredacted
        API key for the service account.

        Args:
          name: The name of the service account being created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._post(
            path_template("/organization/projects/{project_id}/service_accounts", project_id=project_id),
            body=await async_maybe_transform({"name": name}, service_account_create_params.ServiceAccountCreateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ServiceAccountCreateResponse,
        )

    async def retrieve(
        self,
        service_account_id: str,
        *,
        project_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProjectServiceAccount:
        """
        Retrieves a service account in the project.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not service_account_id:
            raise ValueError(f"Expected a non-empty value for `service_account_id` but received {service_account_id!r}")
        return await self._get(
            path_template(
                "/organization/projects/{project_id}/service_accounts/{service_account_id}",
                project_id=project_id,
                service_account_id=service_account_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectServiceAccount,
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
    ) -> AsyncPaginator[ProjectServiceAccount, AsyncConversationCursorPage[ProjectServiceAccount]]:
        """
        Returns a list of service accounts in the project.

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
            path_template("/organization/projects/{project_id}/service_accounts", project_id=project_id),
            page=AsyncConversationCursorPage[ProjectServiceAccount],
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
                    service_account_list_params.ServiceAccountListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=ProjectServiceAccount,
        )

    async def delete(
        self,
        service_account_id: str,
        *,
        project_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ServiceAccountDeleteResponse:
        """
        Deletes a service account from the project.

        Returns confirmation of service account deletion, or an error if the project is
        archived (archived projects have no service accounts).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not service_account_id:
            raise ValueError(f"Expected a non-empty value for `service_account_id` but received {service_account_id!r}")
        return await self._delete(
            path_template(
                "/organization/projects/{project_id}/service_accounts/{service_account_id}",
                project_id=project_id,
                service_account_id=service_account_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ServiceAccountDeleteResponse,
        )


class ServiceAccountsWithRawResponse:
    def __init__(self, service_accounts: ServiceAccounts) -> None:
        self._service_accounts = service_accounts

        self.create = _legacy_response.to_raw_response_wrapper(
            service_accounts.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            service_accounts.retrieve,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            service_accounts.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            service_accounts.delete,
        )


class AsyncServiceAccountsWithRawResponse:
    def __init__(self, service_accounts: AsyncServiceAccounts) -> None:
        self._service_accounts = service_accounts

        self.create = _legacy_response.async_to_raw_response_wrapper(
            service_accounts.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            service_accounts.retrieve,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            service_accounts.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            service_accounts.delete,
        )


class ServiceAccountsWithStreamingResponse:
    def __init__(self, service_accounts: ServiceAccounts) -> None:
        self._service_accounts = service_accounts

        self.create = to_streamed_response_wrapper(
            service_accounts.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            service_accounts.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            service_accounts.list,
        )
        self.delete = to_streamed_response_wrapper(
            service_accounts.delete,
        )


class AsyncServiceAccountsWithStreamingResponse:
    def __init__(self, service_accounts: AsyncServiceAccounts) -> None:
        self._service_accounts = service_accounts

        self.create = async_to_streamed_response_wrapper(
            service_accounts.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            service_accounts.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            service_accounts.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            service_accounts.delete,
        )
