# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...... import _legacy_response
from ......_types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from ......_utils import path_template, maybe_transform, async_maybe_transform
from ......_compat import cached_property
from ......_resource import SyncAPIResource, AsyncAPIResource
from ......_response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ......_base_client import make_request_options
from ......types.admin.organization.projects.service_accounts import api_key_create_params
from ......types.admin.organization.projects.service_accounts.api_key_create_response import APIKeyCreateResponse

__all__ = ["APIKeys", "AsyncAPIKeys"]


class APIKeys(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> APIKeysWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return APIKeysWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> APIKeysWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return APIKeysWithStreamingResponse(self)

    def create(
        self,
        service_account_id: str,
        *,
        project_id: str,
        name: str | Omit = omit,
        scopes: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIKeyCreateResponse:
        """
        Creates an API key for a service account in the project.

        Args:
          name: API key name.

          scopes: API key scopes.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not service_account_id:
            raise ValueError(f"Expected a non-empty value for `service_account_id` but received {service_account_id!r}")
        return self._post(
            path_template(
                "/organization/projects/{project_id}/service_accounts/{service_account_id}/api_keys",
                project_id=project_id,
                service_account_id=service_account_id,
            ),
            body=maybe_transform(
                {
                    "name": name,
                    "scopes": scopes,
                },
                api_key_create_params.APIKeyCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=APIKeyCreateResponse,
        )


class AsyncAPIKeys(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAPIKeysWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAPIKeysWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAPIKeysWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncAPIKeysWithStreamingResponse(self)

    async def create(
        self,
        service_account_id: str,
        *,
        project_id: str,
        name: str | Omit = omit,
        scopes: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> APIKeyCreateResponse:
        """
        Creates an API key for a service account in the project.

        Args:
          name: API key name.

          scopes: API key scopes.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not service_account_id:
            raise ValueError(f"Expected a non-empty value for `service_account_id` but received {service_account_id!r}")
        return await self._post(
            path_template(
                "/organization/projects/{project_id}/service_accounts/{service_account_id}/api_keys",
                project_id=project_id,
                service_account_id=service_account_id,
            ),
            body=await async_maybe_transform(
                {
                    "name": name,
                    "scopes": scopes,
                },
                api_key_create_params.APIKeyCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=APIKeyCreateResponse,
        )


class APIKeysWithRawResponse:
    def __init__(self, api_keys: APIKeys) -> None:
        self._api_keys = api_keys

        self.create = _legacy_response.to_raw_response_wrapper(
            api_keys.create,
        )


class AsyncAPIKeysWithRawResponse:
    def __init__(self, api_keys: AsyncAPIKeys) -> None:
        self._api_keys = api_keys

        self.create = _legacy_response.async_to_raw_response_wrapper(
            api_keys.create,
        )


class APIKeysWithStreamingResponse:
    def __init__(self, api_keys: APIKeys) -> None:
        self._api_keys = api_keys

        self.create = to_streamed_response_wrapper(
            api_keys.create,
        )


class AsyncAPIKeysWithStreamingResponse:
    def __init__(self, api_keys: AsyncAPIKeys) -> None:
        self._api_keys = api_keys

        self.create = async_to_streamed_response_wrapper(
            api_keys.create,
        )
