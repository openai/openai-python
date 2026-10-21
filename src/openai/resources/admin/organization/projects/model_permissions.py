# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..... import _legacy_response
from ....._types import Body, Query, Headers, NotGiven, SequenceNotStr, not_given
from ....._utils import path_template, maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ....._base_client import make_request_options
from .....types.admin.organization.projects import model_permission_update_params
from .....types.admin.organization.projects.project_model_permissions import ProjectModelPermissions
from .....types.admin.organization.projects.project_model_permissions_deleted import ProjectModelPermissionsDeleted

__all__ = ["ModelPermissions", "AsyncModelPermissions"]


class ModelPermissions(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ModelPermissionsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return ModelPermissionsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ModelPermissionsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return ModelPermissionsWithStreamingResponse(self)

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
    ) -> ProjectModelPermissions:
        """
        Returns model permissions for a project.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get(
            path_template("/organization/projects/{project_id}/model_permissions", project_id=project_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectModelPermissions,
        )

    def update(
        self,
        project_id: str,
        *,
        mode: Literal["allow_list", "deny_list"],
        model_ids: SequenceNotStr[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProjectModelPermissions:
        """
        Updates model permissions for a project.

        Args:
          mode: The model permissions mode to apply.

          model_ids: The model IDs included in this permissions policy.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._post(
            path_template("/organization/projects/{project_id}/model_permissions", project_id=project_id),
            body=maybe_transform(
                {
                    "mode": mode,
                    "model_ids": model_ids,
                },
                model_permission_update_params.ModelPermissionUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectModelPermissions,
        )

    def delete(
        self,
        project_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProjectModelPermissionsDeleted:
        """
        Deletes model permissions for a project.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._delete(
            path_template("/organization/projects/{project_id}/model_permissions", project_id=project_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectModelPermissionsDeleted,
        )


class AsyncModelPermissions(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncModelPermissionsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncModelPermissionsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncModelPermissionsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncModelPermissionsWithStreamingResponse(self)

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
    ) -> ProjectModelPermissions:
        """
        Returns model permissions for a project.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._get(
            path_template("/organization/projects/{project_id}/model_permissions", project_id=project_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectModelPermissions,
        )

    async def update(
        self,
        project_id: str,
        *,
        mode: Literal["allow_list", "deny_list"],
        model_ids: SequenceNotStr[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProjectModelPermissions:
        """
        Updates model permissions for a project.

        Args:
          mode: The model permissions mode to apply.

          model_ids: The model IDs included in this permissions policy.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._post(
            path_template("/organization/projects/{project_id}/model_permissions", project_id=project_id),
            body=await async_maybe_transform(
                {
                    "mode": mode,
                    "model_ids": model_ids,
                },
                model_permission_update_params.ModelPermissionUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectModelPermissions,
        )

    async def delete(
        self,
        project_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProjectModelPermissionsDeleted:
        """
        Deletes model permissions for a project.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._delete(
            path_template("/organization/projects/{project_id}/model_permissions", project_id=project_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectModelPermissionsDeleted,
        )


class ModelPermissionsWithRawResponse:
    def __init__(self, model_permissions: ModelPermissions) -> None:
        self._model_permissions = model_permissions

        self.retrieve = _legacy_response.to_raw_response_wrapper(
            model_permissions.retrieve,
        )
        self.update = _legacy_response.to_raw_response_wrapper(
            model_permissions.update,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            model_permissions.delete,
        )


class AsyncModelPermissionsWithRawResponse:
    def __init__(self, model_permissions: AsyncModelPermissions) -> None:
        self._model_permissions = model_permissions

        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            model_permissions.retrieve,
        )
        self.update = _legacy_response.async_to_raw_response_wrapper(
            model_permissions.update,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            model_permissions.delete,
        )


class ModelPermissionsWithStreamingResponse:
    def __init__(self, model_permissions: ModelPermissions) -> None:
        self._model_permissions = model_permissions

        self.retrieve = to_streamed_response_wrapper(
            model_permissions.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            model_permissions.update,
        )
        self.delete = to_streamed_response_wrapper(
            model_permissions.delete,
        )


class AsyncModelPermissionsWithStreamingResponse:
    def __init__(self, model_permissions: AsyncModelPermissions) -> None:
        self._model_permissions = model_permissions

        self.retrieve = async_to_streamed_response_wrapper(
            model_permissions.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            model_permissions.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            model_permissions.delete,
        )
