# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Literal

import httpx2

from ..... import _legacy_response
from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ....._utils import path_template, maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from .....pagination import SyncCursorPage, AsyncCursorPage
from ....._base_client import AsyncPaginator, make_request_options
from .federation_rules import (
    FederationRules,
    AsyncFederationRules,
    FederationRulesWithRawResponse,
    AsyncFederationRulesWithRawResponse,
    FederationRulesWithStreamingResponse,
    AsyncFederationRulesWithStreamingResponse,
)
from .....types.admin.organization import (
    workload_identity_provider_list_params,
    workload_identity_provider_create_params,
    workload_identity_provider_update_params,
)
from .....types.admin.organization.workload_identity_provider import WorkloadIdentityProvider
from .....types.admin.organization.workload_identity_provider_deleted import WorkloadIdentityProviderDeleted

__all__ = ["WorkloadIdentityProviders", "AsyncWorkloadIdentityProviders"]


class WorkloadIdentityProviders(SyncAPIResource):
    @cached_property
    def federation_rules(self) -> FederationRules:
        return FederationRules(self._client)

    @cached_property
    def with_raw_response(self) -> WorkloadIdentityProvidersWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return WorkloadIdentityProvidersWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> WorkloadIdentityProvidersWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return WorkloadIdentityProvidersWithStreamingResponse(self)

    def create(
        self,
        *,
        audience: str,
        issuer: str,
        name: str,
        type: Literal["oidc"],
        attribute_transformations: Iterable[workload_identity_provider_create_params.AttributeTransformation]
        | Omit = omit,
        description: str | Omit = omit,
        enabled: bool | Omit = omit,
        verification: workload_identity_provider_create_params.Verification | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> WorkloadIdentityProvider:
        """
        Register an OIDC provider for keyless project service-account authentication.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/organization/workload_identity_providers",
            body=maybe_transform(
                {
                    "audience": audience,
                    "issuer": issuer,
                    "name": name,
                    "type": type,
                    "attribute_transformations": attribute_transformations,
                    "description": description,
                    "enabled": enabled,
                    "verification": verification,
                },
                workload_identity_provider_create_params.WorkloadIdentityProviderCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=WorkloadIdentityProvider,
        )

    def retrieve(
        self,
        workload_identity_provider_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> WorkloadIdentityProvider:
        """
        Retrieve an OIDC provider in the authenticated organization.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not workload_identity_provider_id:
            raise ValueError(
                f"Expected a non-empty value for `workload_identity_provider_id` but received {workload_identity_provider_id!r}"
            )
        return self._get(
            path_template(
                "/organization/workload_identity_providers/{workload_identity_provider_id}",
                workload_identity_provider_id=workload_identity_provider_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=WorkloadIdentityProvider,
        )

    def update(
        self,
        workload_identity_provider_id: str,
        *,
        attribute_transformations: Iterable[workload_identity_provider_update_params.AttributeTransformation]
        | Omit = omit,
        audience: str | Omit = omit,
        description: Optional[str] | Omit = omit,
        enabled: bool | Omit = omit,
        issuer: str | Omit = omit,
        name: str | Omit = omit,
        verification: workload_identity_provider_update_params.Verification | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> WorkloadIdentityProvider:
        """
        Update supplied provider fields, preserving omitted fields.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not workload_identity_provider_id:
            raise ValueError(
                f"Expected a non-empty value for `workload_identity_provider_id` but received {workload_identity_provider_id!r}"
            )
        return self._post(
            path_template(
                "/organization/workload_identity_providers/{workload_identity_provider_id}",
                workload_identity_provider_id=workload_identity_provider_id,
            ),
            body=maybe_transform(
                {
                    "attribute_transformations": attribute_transformations,
                    "audience": audience,
                    "description": description,
                    "enabled": enabled,
                    "issuer": issuer,
                    "name": name,
                    "verification": verification,
                },
                workload_identity_provider_update_params.WorkloadIdentityProviderUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=WorkloadIdentityProvider,
        )

    def list(
        self,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPage[WorkloadIdentityProvider]:
        """
        List OIDC providers in the authenticated Admin API key's organization.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/organization/workload_identity_providers",
            page=SyncCursorPage[WorkloadIdentityProvider],
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
                    workload_identity_provider_list_params.WorkloadIdentityProviderListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=WorkloadIdentityProvider,
        )

    def delete(
        self,
        workload_identity_provider_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> WorkloadIdentityProviderDeleted:
        """
        Delete a provider after deleting all its federation rules.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not workload_identity_provider_id:
            raise ValueError(
                f"Expected a non-empty value for `workload_identity_provider_id` but received {workload_identity_provider_id!r}"
            )
        return self._delete(
            path_template(
                "/organization/workload_identity_providers/{workload_identity_provider_id}",
                workload_identity_provider_id=workload_identity_provider_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=WorkloadIdentityProviderDeleted,
        )


class AsyncWorkloadIdentityProviders(AsyncAPIResource):
    @cached_property
    def federation_rules(self) -> AsyncFederationRules:
        return AsyncFederationRules(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncWorkloadIdentityProvidersWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncWorkloadIdentityProvidersWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncWorkloadIdentityProvidersWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncWorkloadIdentityProvidersWithStreamingResponse(self)

    async def create(
        self,
        *,
        audience: str,
        issuer: str,
        name: str,
        type: Literal["oidc"],
        attribute_transformations: Iterable[workload_identity_provider_create_params.AttributeTransformation]
        | Omit = omit,
        description: str | Omit = omit,
        enabled: bool | Omit = omit,
        verification: workload_identity_provider_create_params.Verification | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> WorkloadIdentityProvider:
        """
        Register an OIDC provider for keyless project service-account authentication.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/organization/workload_identity_providers",
            body=await async_maybe_transform(
                {
                    "audience": audience,
                    "issuer": issuer,
                    "name": name,
                    "type": type,
                    "attribute_transformations": attribute_transformations,
                    "description": description,
                    "enabled": enabled,
                    "verification": verification,
                },
                workload_identity_provider_create_params.WorkloadIdentityProviderCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=WorkloadIdentityProvider,
        )

    async def retrieve(
        self,
        workload_identity_provider_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> WorkloadIdentityProvider:
        """
        Retrieve an OIDC provider in the authenticated organization.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not workload_identity_provider_id:
            raise ValueError(
                f"Expected a non-empty value for `workload_identity_provider_id` but received {workload_identity_provider_id!r}"
            )
        return await self._get(
            path_template(
                "/organization/workload_identity_providers/{workload_identity_provider_id}",
                workload_identity_provider_id=workload_identity_provider_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=WorkloadIdentityProvider,
        )

    async def update(
        self,
        workload_identity_provider_id: str,
        *,
        attribute_transformations: Iterable[workload_identity_provider_update_params.AttributeTransformation]
        | Omit = omit,
        audience: str | Omit = omit,
        description: Optional[str] | Omit = omit,
        enabled: bool | Omit = omit,
        issuer: str | Omit = omit,
        name: str | Omit = omit,
        verification: workload_identity_provider_update_params.Verification | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> WorkloadIdentityProvider:
        """
        Update supplied provider fields, preserving omitted fields.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not workload_identity_provider_id:
            raise ValueError(
                f"Expected a non-empty value for `workload_identity_provider_id` but received {workload_identity_provider_id!r}"
            )
        return await self._post(
            path_template(
                "/organization/workload_identity_providers/{workload_identity_provider_id}",
                workload_identity_provider_id=workload_identity_provider_id,
            ),
            body=await async_maybe_transform(
                {
                    "attribute_transformations": attribute_transformations,
                    "audience": audience,
                    "description": description,
                    "enabled": enabled,
                    "issuer": issuer,
                    "name": name,
                    "verification": verification,
                },
                workload_identity_provider_update_params.WorkloadIdentityProviderUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=WorkloadIdentityProvider,
        )

    def list(
        self,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[WorkloadIdentityProvider, AsyncCursorPage[WorkloadIdentityProvider]]:
        """
        List OIDC providers in the authenticated Admin API key's organization.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/organization/workload_identity_providers",
            page=AsyncCursorPage[WorkloadIdentityProvider],
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
                    workload_identity_provider_list_params.WorkloadIdentityProviderListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=WorkloadIdentityProvider,
        )

    async def delete(
        self,
        workload_identity_provider_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> WorkloadIdentityProviderDeleted:
        """
        Delete a provider after deleting all its federation rules.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not workload_identity_provider_id:
            raise ValueError(
                f"Expected a non-empty value for `workload_identity_provider_id` but received {workload_identity_provider_id!r}"
            )
        return await self._delete(
            path_template(
                "/organization/workload_identity_providers/{workload_identity_provider_id}",
                workload_identity_provider_id=workload_identity_provider_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=WorkloadIdentityProviderDeleted,
        )


class WorkloadIdentityProvidersWithRawResponse:
    def __init__(self, workload_identity_providers: WorkloadIdentityProviders) -> None:
        self._workload_identity_providers = workload_identity_providers

        self.create = _legacy_response.to_raw_response_wrapper(
            workload_identity_providers.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            workload_identity_providers.retrieve,
        )
        self.update = _legacy_response.to_raw_response_wrapper(
            workload_identity_providers.update,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            workload_identity_providers.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            workload_identity_providers.delete,
        )

    @cached_property
    def federation_rules(self) -> FederationRulesWithRawResponse:
        return FederationRulesWithRawResponse(self._workload_identity_providers.federation_rules)


class AsyncWorkloadIdentityProvidersWithRawResponse:
    def __init__(self, workload_identity_providers: AsyncWorkloadIdentityProviders) -> None:
        self._workload_identity_providers = workload_identity_providers

        self.create = _legacy_response.async_to_raw_response_wrapper(
            workload_identity_providers.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            workload_identity_providers.retrieve,
        )
        self.update = _legacy_response.async_to_raw_response_wrapper(
            workload_identity_providers.update,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            workload_identity_providers.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            workload_identity_providers.delete,
        )

    @cached_property
    def federation_rules(self) -> AsyncFederationRulesWithRawResponse:
        return AsyncFederationRulesWithRawResponse(self._workload_identity_providers.federation_rules)


class WorkloadIdentityProvidersWithStreamingResponse:
    def __init__(self, workload_identity_providers: WorkloadIdentityProviders) -> None:
        self._workload_identity_providers = workload_identity_providers

        self.create = to_streamed_response_wrapper(
            workload_identity_providers.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            workload_identity_providers.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            workload_identity_providers.update,
        )
        self.list = to_streamed_response_wrapper(
            workload_identity_providers.list,
        )
        self.delete = to_streamed_response_wrapper(
            workload_identity_providers.delete,
        )

    @cached_property
    def federation_rules(self) -> FederationRulesWithStreamingResponse:
        return FederationRulesWithStreamingResponse(self._workload_identity_providers.federation_rules)


class AsyncWorkloadIdentityProvidersWithStreamingResponse:
    def __init__(self, workload_identity_providers: AsyncWorkloadIdentityProviders) -> None:
        self._workload_identity_providers = workload_identity_providers

        self.create = async_to_streamed_response_wrapper(
            workload_identity_providers.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            workload_identity_providers.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            workload_identity_providers.update,
        )
        self.list = async_to_streamed_response_wrapper(
            workload_identity_providers.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            workload_identity_providers.delete,
        )

    @cached_property
    def federation_rules(self) -> AsyncFederationRulesWithStreamingResponse:
        return AsyncFederationRulesWithStreamingResponse(self._workload_identity_providers.federation_rules)
