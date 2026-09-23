# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal

import httpx2

from .... import _legacy_response
from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ...._utils import path_template, maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ....pagination import SyncCursorPage, AsyncCursorPage
from ...._base_client import AsyncPaginator, make_request_options
from ....types.admin.organization import (
    external_storage_list_params,
    external_storage_create_params,
)
from ....types.admin.organization.external_storage_deleted import ExternalStorageDeleted
from ....types.admin.organization.external_storage_configuration import ExternalStorageConfiguration

__all__ = ["ExternalStorage", "AsyncExternalStorage"]


class ExternalStorage(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ExternalStorageWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return ExternalStorageWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ExternalStorageWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return ExternalStorageWithStreamingResponse(self)

    def create(
        self,
        *,
        project_id: str,
        provider: external_storage_create_params.Provider,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ExternalStorageConfiguration:
        """
        Register one customer-managed external storage configuration.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/organization/external_storage",
            body=maybe_transform(
                {
                    "project_id": project_id,
                    "provider": provider,
                },
                external_storage_create_params.ExternalStorageCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ExternalStorageConfiguration,
        )

    def retrieve(
        self,
        external_storage_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ExternalStorageConfiguration:
        """
        Get one customer-managed external storage configuration.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not external_storage_id:
            raise ValueError(
                f"Expected a non-empty value for `external_storage_id` but received {external_storage_id!r}"
            )
        return self._get(
            path_template(
                "/organization/external_storage/{external_storage_id}", external_storage_id=external_storage_id
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ExternalStorageConfiguration,
        )

    def list(
        self,
        *,
        after: Optional[str] | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        project_id: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPage[ExternalStorageConfiguration]:
        """
        List the organization's customer-managed external storage configurations.

        Args:
          after: Return external storage configurations after this ID.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/organization/external_storage",
            page=SyncCursorPage[ExternalStorageConfiguration],
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
                        "project_id": project_id,
                    },
                    external_storage_list_params.ExternalStorageListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=ExternalStorageConfiguration,
        )

    def delete(
        self,
        external_storage_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ExternalStorageDeleted:
        """Disconnect a customer-managed external storage configuration.

        Removing the
        project's last configuration restores organization-default retention if
        customer-managed retention was active. Repeating a deletion also completes any
        interrupted retention update. Cloud storage is unchanged.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not external_storage_id:
            raise ValueError(
                f"Expected a non-empty value for `external_storage_id` but received {external_storage_id!r}"
            )
        return self._delete(
            path_template(
                "/organization/external_storage/{external_storage_id}", external_storage_id=external_storage_id
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ExternalStorageDeleted,
        )

    def validate(
        self,
        external_storage_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ExternalStorageConfiguration:
        """
        Validate one customer-managed external storage configuration.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not external_storage_id:
            raise ValueError(
                f"Expected a non-empty value for `external_storage_id` but received {external_storage_id!r}"
            )
        return self._post(
            path_template(
                "/organization/external_storage/{external_storage_id}/validate", external_storage_id=external_storage_id
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ExternalStorageConfiguration,
        )


class AsyncExternalStorage(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncExternalStorageWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncExternalStorageWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncExternalStorageWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncExternalStorageWithStreamingResponse(self)

    async def create(
        self,
        *,
        project_id: str,
        provider: external_storage_create_params.Provider,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ExternalStorageConfiguration:
        """
        Register one customer-managed external storage configuration.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/organization/external_storage",
            body=await async_maybe_transform(
                {
                    "project_id": project_id,
                    "provider": provider,
                },
                external_storage_create_params.ExternalStorageCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ExternalStorageConfiguration,
        )

    async def retrieve(
        self,
        external_storage_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ExternalStorageConfiguration:
        """
        Get one customer-managed external storage configuration.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not external_storage_id:
            raise ValueError(
                f"Expected a non-empty value for `external_storage_id` but received {external_storage_id!r}"
            )
        return await self._get(
            path_template(
                "/organization/external_storage/{external_storage_id}", external_storage_id=external_storage_id
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ExternalStorageConfiguration,
        )

    def list(
        self,
        *,
        after: Optional[str] | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        project_id: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[ExternalStorageConfiguration, AsyncCursorPage[ExternalStorageConfiguration]]:
        """
        List the organization's customer-managed external storage configurations.

        Args:
          after: Return external storage configurations after this ID.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/organization/external_storage",
            page=AsyncCursorPage[ExternalStorageConfiguration],
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
                        "project_id": project_id,
                    },
                    external_storage_list_params.ExternalStorageListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=ExternalStorageConfiguration,
        )

    async def delete(
        self,
        external_storage_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ExternalStorageDeleted:
        """Disconnect a customer-managed external storage configuration.

        Removing the
        project's last configuration restores organization-default retention if
        customer-managed retention was active. Repeating a deletion also completes any
        interrupted retention update. Cloud storage is unchanged.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not external_storage_id:
            raise ValueError(
                f"Expected a non-empty value for `external_storage_id` but received {external_storage_id!r}"
            )
        return await self._delete(
            path_template(
                "/organization/external_storage/{external_storage_id}", external_storage_id=external_storage_id
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ExternalStorageDeleted,
        )

    async def validate(
        self,
        external_storage_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ExternalStorageConfiguration:
        """
        Validate one customer-managed external storage configuration.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not external_storage_id:
            raise ValueError(
                f"Expected a non-empty value for `external_storage_id` but received {external_storage_id!r}"
            )
        return await self._post(
            path_template(
                "/organization/external_storage/{external_storage_id}/validate", external_storage_id=external_storage_id
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ExternalStorageConfiguration,
        )


class ExternalStorageWithRawResponse:
    def __init__(self, external_storage: ExternalStorage) -> None:
        self._external_storage = external_storage

        self.create = _legacy_response.to_raw_response_wrapper(
            external_storage.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            external_storage.retrieve,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            external_storage.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            external_storage.delete,
        )
        self.validate = _legacy_response.to_raw_response_wrapper(
            external_storage.validate,
        )


class AsyncExternalStorageWithRawResponse:
    def __init__(self, external_storage: AsyncExternalStorage) -> None:
        self._external_storage = external_storage

        self.create = _legacy_response.async_to_raw_response_wrapper(
            external_storage.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            external_storage.retrieve,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            external_storage.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            external_storage.delete,
        )
        self.validate = _legacy_response.async_to_raw_response_wrapper(
            external_storage.validate,
        )


class ExternalStorageWithStreamingResponse:
    def __init__(self, external_storage: ExternalStorage) -> None:
        self._external_storage = external_storage

        self.create = to_streamed_response_wrapper(
            external_storage.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            external_storage.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            external_storage.list,
        )
        self.delete = to_streamed_response_wrapper(
            external_storage.delete,
        )
        self.validate = to_streamed_response_wrapper(
            external_storage.validate,
        )


class AsyncExternalStorageWithStreamingResponse:
    def __init__(self, external_storage: AsyncExternalStorage) -> None:
        self._external_storage = external_storage

        self.create = async_to_streamed_response_wrapper(
            external_storage.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            external_storage.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            external_storage.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            external_storage.delete,
        )
        self.validate = async_to_streamed_response_wrapper(
            external_storage.validate,
        )
