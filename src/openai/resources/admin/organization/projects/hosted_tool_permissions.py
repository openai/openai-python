# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..... import _legacy_response
from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ....._utils import path_template, maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ....._base_client import make_request_options
from .....types.admin.organization.projects import hosted_tool_permission_update_params
from .....types.admin.organization.projects.project_hosted_tool_permissions import ProjectHostedToolPermissions

__all__ = ["HostedToolPermissions", "AsyncHostedToolPermissions"]


class HostedToolPermissions(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> HostedToolPermissionsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return HostedToolPermissionsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> HostedToolPermissionsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return HostedToolPermissionsWithStreamingResponse(self)

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
    ) -> ProjectHostedToolPermissions:
        """
        Returns hosted tool permissions for a project.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get(
            path_template("/organization/projects/{project_id}/hosted_tool_permissions", project_id=project_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectHostedToolPermissions,
        )

    def update(
        self,
        project_id: str,
        *,
        code_interpreter: Optional[hosted_tool_permission_update_params.CodeInterpreter] | Omit = omit,
        file_search: Optional[hosted_tool_permission_update_params.FileSearch] | Omit = omit,
        image_generation: Optional[hosted_tool_permission_update_params.ImageGeneration] | Omit = omit,
        mcp: Optional[hosted_tool_permission_update_params.Mcp] | Omit = omit,
        web_search: Optional[hosted_tool_permission_update_params.WebSearch] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProjectHostedToolPermissions:
        """
        Updates hosted tool permissions for a project.

        Args:
          code_interpreter: The code interpreter permission update.

          file_search: The file search permission update.

          image_generation: The image generation permission update.

          mcp: The MCP permission update.

          web_search: The web search permission update.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._post(
            path_template("/organization/projects/{project_id}/hosted_tool_permissions", project_id=project_id),
            body=maybe_transform(
                {
                    "code_interpreter": code_interpreter,
                    "file_search": file_search,
                    "image_generation": image_generation,
                    "mcp": mcp,
                    "web_search": web_search,
                },
                hosted_tool_permission_update_params.HostedToolPermissionUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectHostedToolPermissions,
        )


class AsyncHostedToolPermissions(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncHostedToolPermissionsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncHostedToolPermissionsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncHostedToolPermissionsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncHostedToolPermissionsWithStreamingResponse(self)

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
    ) -> ProjectHostedToolPermissions:
        """
        Returns hosted tool permissions for a project.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._get(
            path_template("/organization/projects/{project_id}/hosted_tool_permissions", project_id=project_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectHostedToolPermissions,
        )

    async def update(
        self,
        project_id: str,
        *,
        code_interpreter: Optional[hosted_tool_permission_update_params.CodeInterpreter] | Omit = omit,
        file_search: Optional[hosted_tool_permission_update_params.FileSearch] | Omit = omit,
        image_generation: Optional[hosted_tool_permission_update_params.ImageGeneration] | Omit = omit,
        mcp: Optional[hosted_tool_permission_update_params.Mcp] | Omit = omit,
        web_search: Optional[hosted_tool_permission_update_params.WebSearch] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProjectHostedToolPermissions:
        """
        Updates hosted tool permissions for a project.

        Args:
          code_interpreter: The code interpreter permission update.

          file_search: The file search permission update.

          image_generation: The image generation permission update.

          mcp: The MCP permission update.

          web_search: The web search permission update.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._post(
            path_template("/organization/projects/{project_id}/hosted_tool_permissions", project_id=project_id),
            body=await async_maybe_transform(
                {
                    "code_interpreter": code_interpreter,
                    "file_search": file_search,
                    "image_generation": image_generation,
                    "mcp": mcp,
                    "web_search": web_search,
                },
                hosted_tool_permission_update_params.HostedToolPermissionUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectHostedToolPermissions,
        )


class HostedToolPermissionsWithRawResponse:
    def __init__(self, hosted_tool_permissions: HostedToolPermissions) -> None:
        self._hosted_tool_permissions = hosted_tool_permissions

        self.retrieve = _legacy_response.to_raw_response_wrapper(
            hosted_tool_permissions.retrieve,
        )
        self.update = _legacy_response.to_raw_response_wrapper(
            hosted_tool_permissions.update,
        )


class AsyncHostedToolPermissionsWithRawResponse:
    def __init__(self, hosted_tool_permissions: AsyncHostedToolPermissions) -> None:
        self._hosted_tool_permissions = hosted_tool_permissions

        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            hosted_tool_permissions.retrieve,
        )
        self.update = _legacy_response.async_to_raw_response_wrapper(
            hosted_tool_permissions.update,
        )


class HostedToolPermissionsWithStreamingResponse:
    def __init__(self, hosted_tool_permissions: HostedToolPermissions) -> None:
        self._hosted_tool_permissions = hosted_tool_permissions

        self.retrieve = to_streamed_response_wrapper(
            hosted_tool_permissions.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            hosted_tool_permissions.update,
        )


class AsyncHostedToolPermissionsWithStreamingResponse:
    def __init__(self, hosted_tool_permissions: AsyncHostedToolPermissions) -> None:
        self._hosted_tool_permissions = hosted_tool_permissions

        self.retrieve = async_to_streamed_response_wrapper(
            hosted_tool_permissions.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            hosted_tool_permissions.update,
        )
