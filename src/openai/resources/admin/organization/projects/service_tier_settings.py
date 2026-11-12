# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal

import httpx2

from ..... import _legacy_response
from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ....._utils import path_template, maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ....._base_client import make_request_options
from .....types.admin.organization.projects import service_tier_setting_update_params
from .....types.admin.organization.projects.project_optional_service_tier import ProjectOptionalServiceTier
from .....types.admin.organization.projects.project_service_tier_settings import ProjectServiceTierSettings

__all__ = ["ServiceTierSettings", "AsyncServiceTierSettings"]


class ServiceTierSettings(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ServiceTierSettingsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return ServiceTierSettingsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ServiceTierSettingsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return ServiceTierSettingsWithStreamingResponse(self)

    def retrieve(
        self,
        project_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ProjectServiceTierSettings:
        """
        Retrieve the configured default and enabled service tiers for a project.

        Args:
          project_id: The ID of the project

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get(
            path_template("/organization/projects/{project_id}/service_tier_settings", project_id=project_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectServiceTierSettings,
        )

    def update(
        self,
        project_id: str,
        *,
        default: Literal["standard", "fast", "scale"] | Omit = omit,
        enabled_tiers: Union[Literal["all"], Iterable[ProjectOptionalServiceTier]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ProjectServiceTierSettings:
        """Update the default or enabled service tiers atomically.

        Supply at least one
        field. Omitted fields keep their current values.

        Args:
          project_id: The ID of the project

          default: Default tier for requests that omit service_tier or use auto.

          enabled_tiers: Additional service tiers enabled for this project. "all" includes future tiers.
              An empty array allows only Standard. Organization policy and eligibility still
              apply.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._post(
            path_template("/organization/projects/{project_id}/service_tier_settings", project_id=project_id),
            body=maybe_transform(
                {
                    "default": default,
                    "enabled_tiers": enabled_tiers,
                },
                service_tier_setting_update_params.ServiceTierSettingUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectServiceTierSettings,
        )


class AsyncServiceTierSettings(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncServiceTierSettingsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncServiceTierSettingsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncServiceTierSettingsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncServiceTierSettingsWithStreamingResponse(self)

    async def retrieve(
        self,
        project_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ProjectServiceTierSettings:
        """
        Retrieve the configured default and enabled service tiers for a project.

        Args:
          project_id: The ID of the project

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._get(
            path_template("/organization/projects/{project_id}/service_tier_settings", project_id=project_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectServiceTierSettings,
        )

    async def update(
        self,
        project_id: str,
        *,
        default: Literal["standard", "fast", "scale"] | Omit = omit,
        enabled_tiers: Union[Literal["all"], Iterable[ProjectOptionalServiceTier]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ProjectServiceTierSettings:
        """Update the default or enabled service tiers atomically.

        Supply at least one
        field. Omitted fields keep their current values.

        Args:
          project_id: The ID of the project

          default: Default tier for requests that omit service_tier or use auto.

          enabled_tiers: Additional service tiers enabled for this project. "all" includes future tiers.
              An empty array allows only Standard. Organization policy and eligibility still
              apply.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return await self._post(
            path_template("/organization/projects/{project_id}/service_tier_settings", project_id=project_id),
            body=await async_maybe_transform(
                {
                    "default": default,
                    "enabled_tiers": enabled_tiers,
                },
                service_tier_setting_update_params.ServiceTierSettingUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectServiceTierSettings,
        )


class ServiceTierSettingsWithRawResponse:
    def __init__(self, service_tier_settings: ServiceTierSettings) -> None:
        self._service_tier_settings = service_tier_settings

        self.retrieve = _legacy_response.to_raw_response_wrapper(
            service_tier_settings.retrieve,
        )
        self.update = _legacy_response.to_raw_response_wrapper(
            service_tier_settings.update,
        )


class AsyncServiceTierSettingsWithRawResponse:
    def __init__(self, service_tier_settings: AsyncServiceTierSettings) -> None:
        self._service_tier_settings = service_tier_settings

        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            service_tier_settings.retrieve,
        )
        self.update = _legacy_response.async_to_raw_response_wrapper(
            service_tier_settings.update,
        )


class ServiceTierSettingsWithStreamingResponse:
    def __init__(self, service_tier_settings: ServiceTierSettings) -> None:
        self._service_tier_settings = service_tier_settings

        self.retrieve = to_streamed_response_wrapper(
            service_tier_settings.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            service_tier_settings.update,
        )


class AsyncServiceTierSettingsWithStreamingResponse:
    def __init__(self, service_tier_settings: AsyncServiceTierSettings) -> None:
        self._service_tier_settings = service_tier_settings

        self.retrieve = async_to_streamed_response_wrapper(
            service_tier_settings.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            service_tier_settings.update,
        )
