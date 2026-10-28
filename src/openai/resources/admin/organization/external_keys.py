# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Literal, overload

import httpx2

from .... import _legacy_response
from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ...._utils import path_template, required_args, maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ....pagination import SyncCursorPage, AsyncCursorPage
from ...._base_client import AsyncPaginator, make_request_options
from ....types.admin.organization import external_key_list_params, external_key_create_params
from ....types.admin.organization.external_key import ExternalKey
from ....types.admin.organization.external_key_validate_response import ExternalKeyValidateResponse

__all__ = ["ExternalKeys", "AsyncExternalKeys"]


class ExternalKeys(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ExternalKeysWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return ExternalKeysWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ExternalKeysWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return ExternalKeysWithStreamingResponse(self)

    @overload
    def create(
        self,
        *,
        external_id: str,
        kms_arn: str,
        name: str,
        role_arn: str,
        type: Literal["aws"],
        purpose: Union[Literal["ekm"], Literal["psp_decryption"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ExternalKey:
        """
        Add an external key config for an organization

        Args:
          external_id: The ExternalID that OpenAI will pass in the AssumeRole call for the customer's
              AWS account. This must be the OpenAI organization ID or an API project ID that
              belongs to the organization.

          kms_arn: The Key Management System ARN for the master key you manage

          name: A friendly name to identify this config

          role_arn: The Role ARN that OpenAI will assume to call your KMS

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        *,
        audience: str,
        kms_key_location: str,
        kms_key_name: str,
        kms_key_ring_name: str,
        kms_project_id: str,
        name: str,
        type: Literal["gcp"],
        workload_identity_pool_id: str,
        workload_identity_project_number: str,
        workload_identity_provider_id: str,
        kms_key_version: str | Omit = omit,
        purpose: Union[Literal["ekm"], Literal["psp_decryption"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ExternalKey:
        """
        Add an external key config for an organization

        Args:
          audience: The aud field in the identity token OpenAI will pass in the call to the
              customer's GCP STS. This must be the OpenAI organization ID or an API project ID
              that belongs to the organization.

          kms_key_location: The region where your Key Management System master key is located

          kms_key_name: The name of the Key Management System master key you manage

          kms_key_ring_name: The Key Management System key ring for the master key you manage

          kms_project_id: The string GCP project name where your KMS resides

          name: A friendly name to identify this config

          workload_identity_pool_id: The pool containing the Workload Identity provider that you registered for
              OpenAI

          workload_identity_project_number: The numeric GCP project number where you registered OpenAI's workload identity

          workload_identity_provider_id: The Workload Identity provider that you registered for OpenAI

          kms_key_version: An exact CryptoKeyVersion number. Required for PSP decryption; not accepted for
              EKM.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        *,
        key_name: str,
        name: str,
        tenant_id: str,
        type: Literal["azure"],
        vault_uri: str,
        key_version: str | Omit = omit,
        purpose: Union[Literal["ekm"], Literal["psp_decryption"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ExternalKey:
        """
        Add an external key config for an organization

        Args:
          key_name: The name of the Azure Key Vault master key that you manage

          name: A friendly name to identify this config

          tenant_id: Your Azure tenant UUID

          vault_uri: The URI of the Azure vault containing the master key you manage

          key_version: An exact Azure Key Vault key version. Required for PSP decryption; not accepted
              for EKM.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(
        ["external_id", "kms_arn", "name", "role_arn", "type"],
        [
            "audience",
            "kms_key_location",
            "kms_key_name",
            "kms_key_ring_name",
            "kms_project_id",
            "name",
            "type",
            "workload_identity_pool_id",
            "workload_identity_project_number",
            "workload_identity_provider_id",
        ],
        ["key_name", "name", "tenant_id", "type", "vault_uri"],
    )
    def create(
        self,
        *,
        external_id: str | Omit = omit,
        kms_arn: str | Omit = omit,
        name: str,
        role_arn: str | Omit = omit,
        type: Literal["aws"] | Literal["gcp"] | Literal["azure"],
        purpose: Union[Literal["ekm"], Literal["psp_decryption"]] | Omit = omit,
        audience: str | Omit = omit,
        kms_key_location: str | Omit = omit,
        kms_key_name: str | Omit = omit,
        kms_key_ring_name: str | Omit = omit,
        kms_project_id: str | Omit = omit,
        workload_identity_pool_id: str | Omit = omit,
        workload_identity_project_number: str | Omit = omit,
        workload_identity_provider_id: str | Omit = omit,
        kms_key_version: str | Omit = omit,
        key_name: str | Omit = omit,
        tenant_id: str | Omit = omit,
        vault_uri: str | Omit = omit,
        key_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ExternalKey:
        return self._post(
            "/organization/external_keys",
            body=maybe_transform(
                {
                    "external_id": external_id,
                    "kms_arn": kms_arn,
                    "name": name,
                    "role_arn": role_arn,
                    "type": type,
                    "purpose": purpose,
                    "audience": audience,
                    "kms_key_location": kms_key_location,
                    "kms_key_name": kms_key_name,
                    "kms_key_ring_name": kms_key_ring_name,
                    "kms_project_id": kms_project_id,
                    "workload_identity_pool_id": workload_identity_pool_id,
                    "workload_identity_project_number": workload_identity_project_number,
                    "workload_identity_provider_id": workload_identity_provider_id,
                    "kms_key_version": kms_key_version,
                    "key_name": key_name,
                    "tenant_id": tenant_id,
                    "vault_uri": vault_uri,
                    "key_version": key_version,
                },
                external_key_create_params.ExternalKeyCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ExternalKey,
        )

    def retrieve(
        self,
        external_key_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ExternalKey:
        """
        Retrieve a stored external key registration for the user's organization.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not external_key_id:
            raise ValueError(f"Expected a non-empty value for `external_key_id` but received {external_key_id!r}")
        return self._get(
            path_template("/organization/external_keys/{external_key_id}", external_key_id=external_key_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ExternalKey,
        )

    def list(
        self,
        *,
        after: Optional[str] | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        purpose: Literal["ekm", "psp_decryption"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPage[ExternalKey]:
        """
        List the external key configs registered on the user's organization

        Args:
          purpose: Filter by key purpose. When omitted, returns keys of all purposes.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/organization/external_keys",
            page=SyncCursorPage[ExternalKey],
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
                        "purpose": purpose,
                    },
                    external_key_list_params.ExternalKeyListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=ExternalKey,
        )

    def delete(
        self,
        external_key_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ExternalKey:
        """
        Delete an external key config for the user's organization

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not external_key_id:
            raise ValueError(f"Expected a non-empty value for `external_key_id` but received {external_key_id!r}")
        return self._delete(
            path_template("/organization/external_keys/{external_key_id}", external_key_id=external_key_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ExternalKey,
        )

    def validate(
        self,
        external_key_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ExternalKeyValidateResponse:
        """
        Validate an external key config for the user's organization

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not external_key_id:
            raise ValueError(f"Expected a non-empty value for `external_key_id` but received {external_key_id!r}")
        return self._post(
            path_template("/organization/external_keys/{external_key_id}/validate", external_key_id=external_key_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ExternalKeyValidateResponse,
        )


class AsyncExternalKeys(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncExternalKeysWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncExternalKeysWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncExternalKeysWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncExternalKeysWithStreamingResponse(self)

    @overload
    async def create(
        self,
        *,
        external_id: str,
        kms_arn: str,
        name: str,
        role_arn: str,
        type: Literal["aws"],
        purpose: Union[Literal["ekm"], Literal["psp_decryption"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ExternalKey:
        """
        Add an external key config for an organization

        Args:
          external_id: The ExternalID that OpenAI will pass in the AssumeRole call for the customer's
              AWS account. This must be the OpenAI organization ID or an API project ID that
              belongs to the organization.

          kms_arn: The Key Management System ARN for the master key you manage

          name: A friendly name to identify this config

          role_arn: The Role ARN that OpenAI will assume to call your KMS

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        *,
        audience: str,
        kms_key_location: str,
        kms_key_name: str,
        kms_key_ring_name: str,
        kms_project_id: str,
        name: str,
        type: Literal["gcp"],
        workload_identity_pool_id: str,
        workload_identity_project_number: str,
        workload_identity_provider_id: str,
        kms_key_version: str | Omit = omit,
        purpose: Union[Literal["ekm"], Literal["psp_decryption"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ExternalKey:
        """
        Add an external key config for an organization

        Args:
          audience: The aud field in the identity token OpenAI will pass in the call to the
              customer's GCP STS. This must be the OpenAI organization ID or an API project ID
              that belongs to the organization.

          kms_key_location: The region where your Key Management System master key is located

          kms_key_name: The name of the Key Management System master key you manage

          kms_key_ring_name: The Key Management System key ring for the master key you manage

          kms_project_id: The string GCP project name where your KMS resides

          name: A friendly name to identify this config

          workload_identity_pool_id: The pool containing the Workload Identity provider that you registered for
              OpenAI

          workload_identity_project_number: The numeric GCP project number where you registered OpenAI's workload identity

          workload_identity_provider_id: The Workload Identity provider that you registered for OpenAI

          kms_key_version: An exact CryptoKeyVersion number. Required for PSP decryption; not accepted for
              EKM.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        *,
        key_name: str,
        name: str,
        tenant_id: str,
        type: Literal["azure"],
        vault_uri: str,
        key_version: str | Omit = omit,
        purpose: Union[Literal["ekm"], Literal["psp_decryption"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ExternalKey:
        """
        Add an external key config for an organization

        Args:
          key_name: The name of the Azure Key Vault master key that you manage

          name: A friendly name to identify this config

          tenant_id: Your Azure tenant UUID

          vault_uri: The URI of the Azure vault containing the master key you manage

          key_version: An exact Azure Key Vault key version. Required for PSP decryption; not accepted
              for EKM.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(
        ["external_id", "kms_arn", "name", "role_arn", "type"],
        [
            "audience",
            "kms_key_location",
            "kms_key_name",
            "kms_key_ring_name",
            "kms_project_id",
            "name",
            "type",
            "workload_identity_pool_id",
            "workload_identity_project_number",
            "workload_identity_provider_id",
        ],
        ["key_name", "name", "tenant_id", "type", "vault_uri"],
    )
    async def create(
        self,
        *,
        external_id: str | Omit = omit,
        kms_arn: str | Omit = omit,
        name: str,
        role_arn: str | Omit = omit,
        type: Literal["aws"] | Literal["gcp"] | Literal["azure"],
        purpose: Union[Literal["ekm"], Literal["psp_decryption"]] | Omit = omit,
        audience: str | Omit = omit,
        kms_key_location: str | Omit = omit,
        kms_key_name: str | Omit = omit,
        kms_key_ring_name: str | Omit = omit,
        kms_project_id: str | Omit = omit,
        workload_identity_pool_id: str | Omit = omit,
        workload_identity_project_number: str | Omit = omit,
        workload_identity_provider_id: str | Omit = omit,
        kms_key_version: str | Omit = omit,
        key_name: str | Omit = omit,
        tenant_id: str | Omit = omit,
        vault_uri: str | Omit = omit,
        key_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ExternalKey:
        return await self._post(
            "/organization/external_keys",
            body=await async_maybe_transform(
                {
                    "external_id": external_id,
                    "kms_arn": kms_arn,
                    "name": name,
                    "role_arn": role_arn,
                    "type": type,
                    "purpose": purpose,
                    "audience": audience,
                    "kms_key_location": kms_key_location,
                    "kms_key_name": kms_key_name,
                    "kms_key_ring_name": kms_key_ring_name,
                    "kms_project_id": kms_project_id,
                    "workload_identity_pool_id": workload_identity_pool_id,
                    "workload_identity_project_number": workload_identity_project_number,
                    "workload_identity_provider_id": workload_identity_provider_id,
                    "kms_key_version": kms_key_version,
                    "key_name": key_name,
                    "tenant_id": tenant_id,
                    "vault_uri": vault_uri,
                    "key_version": key_version,
                },
                external_key_create_params.ExternalKeyCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ExternalKey,
        )

    async def retrieve(
        self,
        external_key_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ExternalKey:
        """
        Retrieve a stored external key registration for the user's organization.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not external_key_id:
            raise ValueError(f"Expected a non-empty value for `external_key_id` but received {external_key_id!r}")
        return await self._get(
            path_template("/organization/external_keys/{external_key_id}", external_key_id=external_key_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ExternalKey,
        )

    def list(
        self,
        *,
        after: Optional[str] | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        purpose: Literal["ekm", "psp_decryption"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[ExternalKey, AsyncCursorPage[ExternalKey]]:
        """
        List the external key configs registered on the user's organization

        Args:
          purpose: Filter by key purpose. When omitted, returns keys of all purposes.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/organization/external_keys",
            page=AsyncCursorPage[ExternalKey],
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
                        "purpose": purpose,
                    },
                    external_key_list_params.ExternalKeyListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=ExternalKey,
        )

    async def delete(
        self,
        external_key_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ExternalKey:
        """
        Delete an external key config for the user's organization

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not external_key_id:
            raise ValueError(f"Expected a non-empty value for `external_key_id` but received {external_key_id!r}")
        return await self._delete(
            path_template("/organization/external_keys/{external_key_id}", external_key_id=external_key_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ExternalKey,
        )

    async def validate(
        self,
        external_key_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ExternalKeyValidateResponse:
        """
        Validate an external key config for the user's organization

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not external_key_id:
            raise ValueError(f"Expected a non-empty value for `external_key_id` but received {external_key_id!r}")
        return await self._post(
            path_template("/organization/external_keys/{external_key_id}/validate", external_key_id=external_key_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ExternalKeyValidateResponse,
        )


class ExternalKeysWithRawResponse:
    def __init__(self, external_keys: ExternalKeys) -> None:
        self._external_keys = external_keys

        self.create = _legacy_response.to_raw_response_wrapper(
            external_keys.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            external_keys.retrieve,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            external_keys.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            external_keys.delete,
        )
        self.validate = _legacy_response.to_raw_response_wrapper(
            external_keys.validate,
        )


class AsyncExternalKeysWithRawResponse:
    def __init__(self, external_keys: AsyncExternalKeys) -> None:
        self._external_keys = external_keys

        self.create = _legacy_response.async_to_raw_response_wrapper(
            external_keys.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            external_keys.retrieve,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            external_keys.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            external_keys.delete,
        )
        self.validate = _legacy_response.async_to_raw_response_wrapper(
            external_keys.validate,
        )


class ExternalKeysWithStreamingResponse:
    def __init__(self, external_keys: ExternalKeys) -> None:
        self._external_keys = external_keys

        self.create = to_streamed_response_wrapper(
            external_keys.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            external_keys.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            external_keys.list,
        )
        self.delete = to_streamed_response_wrapper(
            external_keys.delete,
        )
        self.validate = to_streamed_response_wrapper(
            external_keys.validate,
        )


class AsyncExternalKeysWithStreamingResponse:
    def __init__(self, external_keys: AsyncExternalKeys) -> None:
        self._external_keys = external_keys

        self.create = async_to_streamed_response_wrapper(
            external_keys.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            external_keys.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            external_keys.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            external_keys.delete,
        )
        self.validate = async_to_streamed_response_wrapper(
            external_keys.validate,
        )
