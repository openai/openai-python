# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..... import _legacy_response
from ....._types import Body, Query, Headers, NotGiven, not_given
from ....._utils import path_template, maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ....._base_client import make_request_options
from .....types.admin.organization.projects import data_retention_update_params
from .....types.admin.organization.projects.project_data_retention import ProjectDataRetention

__all__ = ["DataRetention", "AsyncDataRetention"]


class DataRetention(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DataRetentionWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return DataRetentionWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DataRetentionWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return DataRetentionWithStreamingResponse(self)

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
    ) -> ProjectDataRetention:
        """
        Retrieves project data retention controls.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get(
            path_template("/organization/projects/{project_id}/data_retention", project_id=project_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectDataRetention,
        )

    def update(
        self,
        project_id: str,
        *,
        retention_type: Literal[
            "organization_default",
            "none",
            "zero_data_retention",
            "modified_abuse_monitoring",
            "enhanced_zero_data_retention",
            "enhanced_modified_abuse_monitoring",
        ],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProjectDataRetention:
        """
        Updates project data retention controls.

        Args:
          retention_type: The desired project data retention type.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._post(
            path_template("/organization/projects/{project_id}/data_retention", project_id=project_id),
            body=maybe_transform(
                {"retention_type": retention_type}, data_retention_update_params.DataRetentionUpdateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectDataRetention,
        )


class AsyncDataRetention(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDataRetentionWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDataRetentionWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDataRetentionWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncDataRetentionWithStreamingResponse(self)

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
    ) -> ProjectDataRetention:
        """
        Retrieves project data retention controls.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._get(
            path_template("/organization/projects/{project_id}/data_retention", project_id=project_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectDataRetention,
        )

    async def update(
        self,
        project_id: str,
        *,
        retention_type: Literal[
            "organization_default",
            "none",
            "zero_data_retention",
            "modified_abuse_monitoring",
            "enhanced_zero_data_retention",
            "enhanced_modified_abuse_monitoring",
        ],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProjectDataRetention:
        """
        Updates project data retention controls.

        Args:
          retention_type: The desired project data retention type.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._post(
            path_template("/organization/projects/{project_id}/data_retention", project_id=project_id),
            body=await async_maybe_transform(
                {"retention_type": retention_type}, data_retention_update_params.DataRetentionUpdateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectDataRetention,
        )


class DataRetentionWithRawResponse:
    def __init__(self, data_retention: DataRetention) -> None:
        self._data_retention = data_retention

        self.retrieve = _legacy_response.to_raw_response_wrapper(
            data_retention.retrieve,
        )
        self.update = _legacy_response.to_raw_response_wrapper(
            data_retention.update,
        )


class AsyncDataRetentionWithRawResponse:
    def __init__(self, data_retention: AsyncDataRetention) -> None:
        self._data_retention = data_retention

        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            data_retention.retrieve,
        )
        self.update = _legacy_response.async_to_raw_response_wrapper(
            data_retention.update,
        )


class DataRetentionWithStreamingResponse:
    def __init__(self, data_retention: DataRetention) -> None:
        self._data_retention = data_retention

        self.retrieve = to_streamed_response_wrapper(
            data_retention.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            data_retention.update,
        )


class AsyncDataRetentionWithStreamingResponse:
    def __init__(self, data_retention: AsyncDataRetention) -> None:
        self._data_retention = data_retention

        self.retrieve = async_to_streamed_response_wrapper(
            data_retention.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            data_retention.update,
        )
