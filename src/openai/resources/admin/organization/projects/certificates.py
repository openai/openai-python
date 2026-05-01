# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..... import _legacy_response
from ....._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from ....._utils import path_template, maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from .....pagination import SyncPage, AsyncPage, SyncConversationCursorPage, AsyncConversationCursorPage
from ....._base_client import AsyncPaginator, make_request_options
from .....types.admin.organization.projects import (
    certificate_list_params,
    certificate_activate_params,
    certificate_deactivate_params,
)
from .....types.admin.organization.projects.certificate_list_response import CertificateListResponse
from .....types.admin.organization.projects.certificate_activate_response import CertificateActivateResponse
from .....types.admin.organization.projects.certificate_deactivate_response import CertificateDeactivateResponse

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

    def list(
        self,
        project_id: str,
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
        List certificates for this project.

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
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get_api_list(
            path_template("/organization/projects/{project_id}/certificates", project_id=project_id),
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

    def activate(
        self,
        project_id: str,
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
        Activate certificates at the project level.

        You can atomically and idempotently activate up to 10 certificates at a time.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get_api_list(
            path_template("/organization/projects/{project_id}/certificates/activate", project_id=project_id),
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
        project_id: str,
        *,
        certificate_ids: SequenceNotStr[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SyncPage[CertificateDeactivateResponse]:
        """Deactivate certificates at the project level.

        You can atomically and
        idempotently deactivate up to 10 certificates at a time.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get_api_list(
            path_template("/organization/projects/{project_id}/certificates/deactivate", project_id=project_id),
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

    def list(
        self,
        project_id: str,
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
        List certificates for this project.

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
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get_api_list(
            path_template("/organization/projects/{project_id}/certificates", project_id=project_id),
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

    def activate(
        self,
        project_id: str,
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
        Activate certificates at the project level.

        You can atomically and idempotently activate up to 10 certificates at a time.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get_api_list(
            path_template("/organization/projects/{project_id}/certificates/activate", project_id=project_id),
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
        project_id: str,
        *,
        certificate_ids: SequenceNotStr[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[CertificateDeactivateResponse, AsyncPage[CertificateDeactivateResponse]]:
        """Deactivate certificates at the project level.

        You can atomically and
        idempotently deactivate up to 10 certificates at a time.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get_api_list(
            path_template("/organization/projects/{project_id}/certificates/deactivate", project_id=project_id),
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

        self.list = _legacy_response.to_raw_response_wrapper(
            certificates.list,
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

        self.list = _legacy_response.async_to_raw_response_wrapper(
            certificates.list,
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

        self.list = to_streamed_response_wrapper(
            certificates.list,
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

        self.list = async_to_streamed_response_wrapper(
            certificates.list,
        )
        self.activate = async_to_streamed_response_wrapper(
            certificates.activate,
        )
        self.deactivate = async_to_streamed_response_wrapper(
            certificates.deactivate,
        )
