# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal

import httpx

from .... import _legacy_response
from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ...._utils import path_template, maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ....pagination import SyncCursorPage, AsyncCursorPage
from ...._base_client import AsyncPaginator, make_request_options
from ....types.admin.organization import admin_api_key_list_params, admin_api_key_create_params
from ....types.admin.organization.admin_api_key import AdminAPIKey
from ....types.admin.organization.admin_api_key_create_response import AdminAPIKeyCreateResponse
from ....types.admin.organization.admin_api_key_delete_response import AdminAPIKeyDeleteResponse

__all__ = ["AdminAPIKeys", "AsyncAdminAPIKeys"]


class AdminAPIKeys(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AdminAPIKeysWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AdminAPIKeysWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AdminAPIKeysWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AdminAPIKeysWithStreamingResponse(self)

    def create(
        self,
        *,
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AdminAPIKeyCreateResponse:
        """
        Create an organization admin API key

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/organization/admin_api_keys",
            body=maybe_transform({"name": name}, admin_api_key_create_params.AdminAPIKeyCreateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=AdminAPIKeyCreateResponse,
        )

    def retrieve(
        self,
        key_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AdminAPIKey:
        """
        Retrieve a single organization API key

        Args:
          key_id: The ID of the API key.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not key_id:
            raise ValueError(f"Expected a non-empty value for `key_id` but received {key_id!r}")
        return self._get(
            path_template("/organization/admin_api_keys/{key_id}", key_id=key_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=AdminAPIKey,
        )

    def list(
        self,
        *,
        after: Optional[str] | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPage[AdminAPIKey]:
        """
        List organization API keys

        Args:
          after: Return keys with IDs that come after this ID in the pagination order.

          limit: Maximum number of keys to return.

          order: Order results by creation time, ascending or descending.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/organization/admin_api_keys",
            page=SyncCursorPage[AdminAPIKey],
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
                    admin_api_key_list_params.AdminAPIKeyListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=AdminAPIKey,
        )

    def delete(
        self,
        key_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AdminAPIKeyDeleteResponse:
        """
        Delete an organization admin API key

        Args:
          key_id: The ID of the API key to be deleted.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not key_id:
            raise ValueError(f"Expected a non-empty value for `key_id` but received {key_id!r}")
        return self._delete(
            path_template("/organization/admin_api_keys/{key_id}", key_id=key_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=AdminAPIKeyDeleteResponse,
        )


class AsyncAdminAPIKeys(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAdminAPIKeysWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAdminAPIKeysWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAdminAPIKeysWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncAdminAPIKeysWithStreamingResponse(self)

    async def create(
        self,
        *,
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AdminAPIKeyCreateResponse:
        """
        Create an organization admin API key

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/organization/admin_api_keys",
            body=await async_maybe_transform({"name": name}, admin_api_key_create_params.AdminAPIKeyCreateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=AdminAPIKeyCreateResponse,
        )

    async def retrieve(
        self,
        key_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AdminAPIKey:
        """
        Retrieve a single organization API key

        Args:
          key_id: The ID of the API key.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not key_id:
            raise ValueError(f"Expected a non-empty value for `key_id` but received {key_id!r}")
        return await self._get(
            path_template("/organization/admin_api_keys/{key_id}", key_id=key_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=AdminAPIKey,
        )

    def list(
        self,
        *,
        after: Optional[str] | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[AdminAPIKey, AsyncCursorPage[AdminAPIKey]]:
        """
        List organization API keys

        Args:
          after: Return keys with IDs that come after this ID in the pagination order.

          limit: Maximum number of keys to return.

          order: Order results by creation time, ascending or descending.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/organization/admin_api_keys",
            page=AsyncCursorPage[AdminAPIKey],
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
                    admin_api_key_list_params.AdminAPIKeyListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=AdminAPIKey,
        )

    async def delete(
        self,
        key_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AdminAPIKeyDeleteResponse:
        """
        Delete an organization admin API key

        Args:
          key_id: The ID of the API key to be deleted.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not key_id:
            raise ValueError(f"Expected a non-empty value for `key_id` but received {key_id!r}")
        return await self._delete(
            path_template("/organization/admin_api_keys/{key_id}", key_id=key_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=AdminAPIKeyDeleteResponse,
        )


class AdminAPIKeysWithRawResponse:
    def __init__(self, admin_api_keys: AdminAPIKeys) -> None:
        self._admin_api_keys = admin_api_keys

        self.create = _legacy_response.to_raw_response_wrapper(
            admin_api_keys.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            admin_api_keys.retrieve,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            admin_api_keys.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            admin_api_keys.delete,
        )


class AsyncAdminAPIKeysWithRawResponse:
    def __init__(self, admin_api_keys: AsyncAdminAPIKeys) -> None:
        self._admin_api_keys = admin_api_keys

        self.create = _legacy_response.async_to_raw_response_wrapper(
            admin_api_keys.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            admin_api_keys.retrieve,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            admin_api_keys.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            admin_api_keys.delete,
        )


class AdminAPIKeysWithStreamingResponse:
    def __init__(self, admin_api_keys: AdminAPIKeys) -> None:
        self._admin_api_keys = admin_api_keys

        self.create = to_streamed_response_wrapper(
            admin_api_keys.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            admin_api_keys.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            admin_api_keys.list,
        )
        self.delete = to_streamed_response_wrapper(
            admin_api_keys.delete,
        )


class AsyncAdminAPIKeysWithStreamingResponse:
    def __init__(self, admin_api_keys: AsyncAdminAPIKeys) -> None:
        self._admin_api_keys = admin_api_keys

        self.create = async_to_streamed_response_wrapper(
            admin_api_keys.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            admin_api_keys.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            admin_api_keys.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            admin_api_keys.delete,
        )
