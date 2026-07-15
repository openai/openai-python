# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from .... import _legacy_response
from ...._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from ...._utils import path_template, maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ....pagination import SyncPage, AsyncPage, SyncConversationCursorPage, AsyncConversationCursorPage
from ...._base_client import AsyncPaginator, make_request_options
from ....types.admin.organization import (
    certificate_list_params,
    certificate_create_params,
    certificate_update_params,
    certificate_activate_params,
    certificate_retrieve_params,
    certificate_deactivate_params,
)
from ....types.admin.organization.certificate import Certificate
from ....types.admin.organization.certificate_list_response import CertificateListResponse
from ....types.admin.organization.certificate_delete_response import CertificateDeleteResponse
from ....types.admin.organization.certificate_activate_response import CertificateActivateResponse
from ....types.admin.organization.certificate_deactivate_response import CertificateDeactivateResponse

__all__ = ["Certificates", "AsyncCertificates"]


class Certificates(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CertificatesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return CertificatesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CertificatesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return CertificatesWithStreamingResponse(self)

    def create(
        self,
        *,
        certificate: str,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Certificate:
        """Upload a certificate to the organization.

        This does **not** automatically
        activate the certificate.

        Organizations can upload up to 50 certificates.

        Args:
          certificate: The certificate content in PEM format

          name: An optional name for the certificate

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/organization/certificates",
            body=maybe_transform(
                {
                    "certificate": certificate,
                    "name": name,
                },
                certificate_create_params.CertificateCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=Certificate,
        )

    def retrieve(
        self,
        certificate_id: str,
        *,
        include: List[Literal["content"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Certificate:
        """
        Get a certificate that has been uploaded to the organization.

        You can get a certificate regardless of whether it is active or not.

        Args:
          include: A list of additional fields to include in the response. Currently the only
              supported value is `content` to fetch the PEM content of the certificate.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not certificate_id:
            raise ValueError(f"Expected a non-empty value for `certificate_id` but received {certificate_id!r}")
        return self._get(
            path_template("/organization/certificates/{certificate_id}", certificate_id=certificate_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"include": include}, certificate_retrieve_params.CertificateRetrieveParams),
                security={"admin_api_key_auth": True},
            ),
            cast_to=Certificate,
        )

    def update(
        self,
        certificate_id: str,
        *,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Certificate:
        """Modify a certificate.

        Note that only the name can be modified.

        Args:
          name: The updated name for the certificate

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not certificate_id:
            raise ValueError(f"Expected a non-empty value for `certificate_id` but received {certificate_id!r}")
        return self._post(
            path_template("/organization/certificates/{certificate_id}", certificate_id=certificate_id),
            body=maybe_transform({"name": name}, certificate_update_params.CertificateUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=Certificate,
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
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncConversationCursorPage[CertificateListResponse]:
        """
        List uploaded certificates for this organization.

        Args:
          after: A cursor for use in pagination. `after` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include after=obj_foo in order to
              fetch the next page of the list.

          limit: A limit on the number of objects to be returned. Limit can range between 1 and
              100, and the default is 20.

          order: Sort order by the `created_at` timestamp of the objects. `asc` for ascending
              order and `desc` for descending order.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/organization/certificates",
            page=SyncConversationCursorPage[CertificateListResponse],
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
                    certificate_list_params.CertificateListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=CertificateListResponse,
        )

    def delete(
        self,
        certificate_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CertificateDeleteResponse:
        """
        Delete a certificate from the organization.

        The certificate must be inactive for the organization and all projects.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not certificate_id:
            raise ValueError(f"Expected a non-empty value for `certificate_id` but received {certificate_id!r}")
        return self._delete(
            path_template("/organization/certificates/{certificate_id}", certificate_id=certificate_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=CertificateDeleteResponse,
        )

    def activate(
        self,
        *,
        certificate_ids: SequenceNotStr[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncPage[CertificateActivateResponse]:
        """
        Activate certificates at the organization level.

        You can atomically and idempotently activate up to 10 certificates at a time.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/organization/certificates/activate",
            page=SyncPage[CertificateActivateResponse],
            body=maybe_transform(
                {"certificate_ids": certificate_ids}, certificate_activate_params.CertificateActivateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            model=CertificateActivateResponse,
            method="post",
        )

    def deactivate(
        self,
        *,
        certificate_ids: SequenceNotStr[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncPage[CertificateDeactivateResponse]:
        """
        Deactivate certificates at the organization level.

        You can atomically and idempotently deactivate up to 10 certificates at a time.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/organization/certificates/deactivate",
            page=SyncPage[CertificateDeactivateResponse],
            body=maybe_transform(
                {"certificate_ids": certificate_ids}, certificate_deactivate_params.CertificateDeactivateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            model=CertificateDeactivateResponse,
            method="post",
        )


class AsyncCertificates(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCertificatesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCertificatesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCertificatesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncCertificatesWithStreamingResponse(self)

    async def create(
        self,
        *,
        certificate: str,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Certificate:
        """Upload a certificate to the organization.

        This does **not** automatically
        activate the certificate.

        Organizations can upload up to 50 certificates.

        Args:
          certificate: The certificate content in PEM format

          name: An optional name for the certificate

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/organization/certificates",
            body=await async_maybe_transform(
                {
                    "certificate": certificate,
                    "name": name,
                },
                certificate_create_params.CertificateCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=Certificate,
        )

    async def retrieve(
        self,
        certificate_id: str,
        *,
        include: List[Literal["content"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Certificate:
        """
        Get a certificate that has been uploaded to the organization.

        You can get a certificate regardless of whether it is active or not.

        Args:
          include: A list of additional fields to include in the response. Currently the only
              supported value is `content` to fetch the PEM content of the certificate.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not certificate_id:
            raise ValueError(f"Expected a non-empty value for `certificate_id` but received {certificate_id!r}")
        return await self._get(
            path_template("/organization/certificates/{certificate_id}", certificate_id=certificate_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"include": include}, certificate_retrieve_params.CertificateRetrieveParams
                ),
                security={"admin_api_key_auth": True},
            ),
            cast_to=Certificate,
        )

    async def update(
        self,
        certificate_id: str,
        *,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Certificate:
        """Modify a certificate.

        Note that only the name can be modified.

        Args:
          name: The updated name for the certificate

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not certificate_id:
            raise ValueError(f"Expected a non-empty value for `certificate_id` but received {certificate_id!r}")
        return await self._post(
            path_template("/organization/certificates/{certificate_id}", certificate_id=certificate_id),
            body=await async_maybe_transform({"name": name}, certificate_update_params.CertificateUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=Certificate,
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
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[CertificateListResponse, AsyncConversationCursorPage[CertificateListResponse]]:
        """
        List uploaded certificates for this organization.

        Args:
          after: A cursor for use in pagination. `after` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include after=obj_foo in order to
              fetch the next page of the list.

          limit: A limit on the number of objects to be returned. Limit can range between 1 and
              100, and the default is 20.

          order: Sort order by the `created_at` timestamp of the objects. `asc` for ascending
              order and `desc` for descending order.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/organization/certificates",
            page=AsyncConversationCursorPage[CertificateListResponse],
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
                    certificate_list_params.CertificateListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=CertificateListResponse,
        )

    async def delete(
        self,
        certificate_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CertificateDeleteResponse:
        """
        Delete a certificate from the organization.

        The certificate must be inactive for the organization and all projects.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not certificate_id:
            raise ValueError(f"Expected a non-empty value for `certificate_id` but received {certificate_id!r}")
        return await self._delete(
            path_template("/organization/certificates/{certificate_id}", certificate_id=certificate_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=CertificateDeleteResponse,
        )

    def activate(
        self,
        *,
        certificate_ids: SequenceNotStr[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[CertificateActivateResponse, AsyncPage[CertificateActivateResponse]]:
        """
        Activate certificates at the organization level.

        You can atomically and idempotently activate up to 10 certificates at a time.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/organization/certificates/activate",
            page=AsyncPage[CertificateActivateResponse],
            body=maybe_transform(
                {"certificate_ids": certificate_ids}, certificate_activate_params.CertificateActivateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            model=CertificateActivateResponse,
            method="post",
        )

    def deactivate(
        self,
        *,
        certificate_ids: SequenceNotStr[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[CertificateDeactivateResponse, AsyncPage[CertificateDeactivateResponse]]:
        """
        Deactivate certificates at the organization level.

        You can atomically and idempotently deactivate up to 10 certificates at a time.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/organization/certificates/deactivate",
            page=AsyncPage[CertificateDeactivateResponse],
            body=maybe_transform(
                {"certificate_ids": certificate_ids}, certificate_deactivate_params.CertificateDeactivateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            model=CertificateDeactivateResponse,
            method="post",
        )


class CertificatesWithRawResponse:
    def __init__(self, certificates: Certificates) -> None:
        self._certificates = certificates

        self.create = _legacy_response.to_raw_response_wrapper(
            certificates.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            certificates.retrieve,
        )
        self.update = _legacy_response.to_raw_response_wrapper(
            certificates.update,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            certificates.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            certificates.delete,
        )
        self.activate = _legacy_response.to_raw_response_wrapper(
            certificates.activate,
        )
        self.deactivate = _legacy_response.to_raw_response_wrapper(
            certificates.deactivate,
        )


class AsyncCertificatesWithRawResponse:
    def __init__(self, certificates: AsyncCertificates) -> None:
        self._certificates = certificates

        self.create = _legacy_response.async_to_raw_response_wrapper(
            certificates.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            certificates.retrieve,
        )
        self.update = _legacy_response.async_to_raw_response_wrapper(
            certificates.update,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            certificates.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            certificates.delete,
        )
        self.activate = _legacy_response.async_to_raw_response_wrapper(
            certificates.activate,
        )
        self.deactivate = _legacy_response.async_to_raw_response_wrapper(
            certificates.deactivate,
        )


class CertificatesWithStreamingResponse:
    def __init__(self, certificates: Certificates) -> None:
        self._certificates = certificates

        self.create = to_streamed_response_wrapper(
            certificates.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            certificates.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            certificates.update,
        )
        self.list = to_streamed_response_wrapper(
            certificates.list,
        )
        self.delete = to_streamed_response_wrapper(
            certificates.delete,
        )
        self.activate = to_streamed_response_wrapper(
            certificates.activate,
        )
        self.deactivate = to_streamed_response_wrapper(
            certificates.deactivate,
        )


class AsyncCertificatesWithStreamingResponse:
    def __init__(self, certificates: AsyncCertificates) -> None:
        self._certificates = certificates

        self.create = async_to_streamed_response_wrapper(
            certificates.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            certificates.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            certificates.update,
        )
        self.list = async_to_streamed_response_wrapper(
            certificates.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            certificates.delete,
        )
        self.activate = async_to_streamed_response_wrapper(
            certificates.activate,
        )
        self.deactivate = async_to_streamed_response_wrapper(
            certificates.deactivate,
        )
