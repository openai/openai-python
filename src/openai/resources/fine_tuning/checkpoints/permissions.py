# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from .... import _legacy_response
from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import (
    maybe_transform,
    async_maybe_transform,
)
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ....pagination import SyncPage, AsyncPage
from ...._base_client import AsyncPaginator, make_request_options
from ....types.fine_tuning.checkpoints import permission_create_params, permission_retrieve_params
from ....types.fine_tuning.checkpoints.permission_create_response import PermissionCreateResponse
from ....types.fine_tuning.checkpoints.permission_delete_response import PermissionDeleteResponse
from ....types.fine_tuning.checkpoints.permission_retrieve_response import PermissionRetrieveResponse

__all__ = ["Permissions", "AsyncPermissions"]


class Permissions(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PermissionsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return PermissionsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PermissionsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return PermissionsWithStreamingResponse(self)

    def create(
        self,
        fine_tuned_model_checkpoint: str,
        *,
        project_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncPage[PermissionCreateResponse]:
        """
        **NOTE:** Calling this endpoint requires an [admin API key](../admin-api-keys).

        This enables organization owners to share fine-tuned models with other projects
        in their organization.

        Args:
          project_ids: The project identifiers to grant access to.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not fine_tuned_model_checkpoint:
            raise ValueError(
                f"Expected a non-empty value for `fine_tuned_model_checkpoint` but received {fine_tuned_model_checkpoint!r}"
            )
        return self._get_api_list(
            f"/fine_tuning/checkpoints/{fine_tuned_model_checkpoint}/permissions",
            page=SyncPage[PermissionCreateResponse],
            body=maybe_transform({"project_ids": project_ids}, permission_create_params.PermissionCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            model=PermissionCreateResponse,
            method="post",
        )

    def retrieve(
        self,
        fine_tuned_model_checkpoint: str,
        *,
        after: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        order: Literal["ascending", "descending"] | NotGiven = NOT_GIVEN,
        project_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PermissionRetrieveResponse:
        """
        **NOTE:** This endpoint requires an [admin API key](../admin-api-keys).

        Organization owners can use this endpoint to view all permissions for a
        fine-tuned model checkpoint.

        Args:
          after: Identifier for the last permission ID from the previous pagination request.

          limit: Number of permissions to retrieve.

          order: The order in which to retrieve permissions.

          project_id: The ID of the project to get permissions for.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not fine_tuned_model_checkpoint:
            raise ValueError(
                f"Expected a non-empty value for `fine_tuned_model_checkpoint` but received {fine_tuned_model_checkpoint!r}"
            )
        return self._get(
            f"/fine_tuning/checkpoints/{fine_tuned_model_checkpoint}/permissions",
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
                    permission_retrieve_params.PermissionRetrieveParams,
                ),
            ),
            cast_to=PermissionRetrieveResponse,
        )

    def delete(
        self,
        fine_tuned_model_checkpoint: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PermissionDeleteResponse:
        """
        **NOTE:** This endpoint requires an [admin API key](../admin-api-keys).

        Organization owners can use this endpoint to delete a permission for a
        fine-tuned model checkpoint.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not fine_tuned_model_checkpoint:
            raise ValueError(
                f"Expected a non-empty value for `fine_tuned_model_checkpoint` but received {fine_tuned_model_checkpoint!r}"
            )
        return self._delete(
            f"/fine_tuning/checkpoints/{fine_tuned_model_checkpoint}/permissions",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PermissionDeleteResponse,
        )


class AsyncPermissions(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPermissionsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPermissionsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPermissionsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncPermissionsWithStreamingResponse(self)

    def create(
        self,
        fine_tuned_model_checkpoint: str,
        *,
        project_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[PermissionCreateResponse, AsyncPage[PermissionCreateResponse]]:
        """
        **NOTE:** Calling this endpoint requires an [admin API key](../admin-api-keys).

        This enables organization owners to share fine-tuned models with other projects
        in their organization.

        Args:
          project_ids: The project identifiers to grant access to.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not fine_tuned_model_checkpoint:
            raise ValueError(
                f"Expected a non-empty value for `fine_tuned_model_checkpoint` but received {fine_tuned_model_checkpoint!r}"
            )
        return self._get_api_list(
            f"/fine_tuning/checkpoints/{fine_tuned_model_checkpoint}/permissions",
            page=AsyncPage[PermissionCreateResponse],
            body=maybe_transform({"project_ids": project_ids}, permission_create_params.PermissionCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            model=PermissionCreateResponse,
            method="post",
        )

    async def retrieve(
        self,
        fine_tuned_model_checkpoint: str,
        *,
        after: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        order: Literal["ascending", "descending"] | NotGiven = NOT_GIVEN,
        project_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PermissionRetrieveResponse:
        """
        **NOTE:** This endpoint requires an [admin API key](../admin-api-keys).

        Organization owners can use this endpoint to view all permissions for a
        fine-tuned model checkpoint.

        Args:
          after: Identifier for the last permission ID from the previous pagination request.

          limit: Number of permissions to retrieve.

          order: The order in which to retrieve permissions.

          project_id: The ID of the project to get permissions for.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not fine_tuned_model_checkpoint:
            raise ValueError(
                f"Expected a non-empty value for `fine_tuned_model_checkpoint` but received {fine_tuned_model_checkpoint!r}"
            )
        return await self._get(
            f"/fine_tuning/checkpoints/{fine_tuned_model_checkpoint}/permissions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                        "order": order,
                        "project_id": project_id,
                    },
                    permission_retrieve_params.PermissionRetrieveParams,
                ),
            ),
            cast_to=PermissionRetrieveResponse,
        )

    async def delete(
        self,
        fine_tuned_model_checkpoint: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PermissionDeleteResponse:
        """
        **NOTE:** This endpoint requires an [admin API key](../admin-api-keys).

        Organization owners can use this endpoint to delete a permission for a
        fine-tuned model checkpoint.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not fine_tuned_model_checkpoint:
            raise ValueError(
                f"Expected a non-empty value for `fine_tuned_model_checkpoint` but received {fine_tuned_model_checkpoint!r}"
            )
        return await self._delete(
            f"/fine_tuning/checkpoints/{fine_tuned_model_checkpoint}/permissions",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PermissionDeleteResponse,
        )


class PermissionsWithRawResponse:
    def __init__(self, permissions: Permissions) -> None:
        self._permissions = permissions

        self.create = _legacy_response.to_raw_response_wrapper(
            permissions.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            permissions.retrieve,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            permissions.delete,
        )


class AsyncPermissionsWithRawResponse:
    def __init__(self, permissions: AsyncPermissions) -> None:
        self._permissions = permissions

        self.create = _legacy_response.async_to_raw_response_wrapper(
            permissions.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            permissions.retrieve,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            permissions.delete,
        )


class PermissionsWithStreamingResponse:
    def __init__(self, permissions: Permissions) -> None:
        self._permissions = permissions

        self.create = to_streamed_response_wrapper(
            permissions.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            permissions.retrieve,
        )
        self.delete = to_streamed_response_wrapper(
            permissions.delete,
        )


class AsyncPermissionsWithStreamingResponse:
    def __init__(self, permissions: AsyncPermissions) -> None:
        self._permissions = permissions

        self.create = async_to_streamed_response_wrapper(
            permissions.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            permissions.retrieve,
        )
        self.delete = async_to_streamed_response_wrapper(
            permissions.delete,
        )
