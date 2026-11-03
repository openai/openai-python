# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Optional
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
from .....types.admin.organization.workload_identity_providers import (
    federation_rule_list_params,
    federation_rule_create_params,
    federation_rule_update_params,
)
from .....types.admin.organization.workload_identity_providers.federation_rule import FederationRule
from .....types.admin.organization.workload_identity_providers.federation_rule_deleted import FederationRuleDeleted

__all__ = ["FederationRules", "AsyncFederationRules"]


class FederationRules(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FederationRulesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return FederationRulesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FederationRulesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return FederationRulesWithStreamingResponse(self)

    def create(
        self,
        workload_identity_provider_id: str,
        *,
        attribute_matchers: Dict[str, Union[str, bool, Union[int, float]]],
        project_id: str,
        service_account_id: str,
        description: str | Omit = omit,
        enabled: bool | Omit = omit,
        name: str | Omit = omit,
        permissions: federation_rule_create_params.Permissions | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> FederationRule:
        """
        Bind verified token attributes to an existing project service account.

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
                "/organization/workload_identity_providers/{workload_identity_provider_id}/federation_rules",
                workload_identity_provider_id=workload_identity_provider_id,
            ),
            body=maybe_transform(
                {
                    "attribute_matchers": attribute_matchers,
                    "project_id": project_id,
                    "service_account_id": service_account_id,
                    "description": description,
                    "enabled": enabled,
                    "name": name,
                    "permissions": permissions,
                },
                federation_rule_create_params.FederationRuleCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=FederationRule,
        )

    def retrieve(
        self,
        workload_identity_federation_rule_id: str,
        *,
        workload_identity_provider_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> FederationRule:
        """
        Retrieve a federation rule owned by the authenticated organization and provider.

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
        if not workload_identity_federation_rule_id:
            raise ValueError(
                f"Expected a non-empty value for `workload_identity_federation_rule_id` but received {workload_identity_federation_rule_id!r}"
            )
        return self._get(
            path_template(
                "/organization/workload_identity_providers/{workload_identity_provider_id}/federation_rules/{workload_identity_federation_rule_id}",
                workload_identity_provider_id=workload_identity_provider_id,
                workload_identity_federation_rule_id=workload_identity_federation_rule_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=FederationRule,
        )

    def update(
        self,
        workload_identity_federation_rule_id: str,
        *,
        workload_identity_provider_id: str,
        attribute_matchers: Dict[str, Union[str, bool, Union[int, float]]] | Omit = omit,
        description: Optional[str] | Omit = omit,
        enabled: bool | Omit = omit,
        name: Optional[str] | Omit = omit,
        permissions: federation_rule_update_params.Permissions | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> FederationRule:
        """
        Update supplied matcher, permission, metadata, or enabled fields.

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
        if not workload_identity_federation_rule_id:
            raise ValueError(
                f"Expected a non-empty value for `workload_identity_federation_rule_id` but received {workload_identity_federation_rule_id!r}"
            )
        return self._post(
            path_template(
                "/organization/workload_identity_providers/{workload_identity_provider_id}/federation_rules/{workload_identity_federation_rule_id}",
                workload_identity_provider_id=workload_identity_provider_id,
                workload_identity_federation_rule_id=workload_identity_federation_rule_id,
            ),
            body=maybe_transform(
                {
                    "attribute_matchers": attribute_matchers,
                    "description": description,
                    "enabled": enabled,
                    "name": name,
                    "permissions": permissions,
                },
                federation_rule_update_params.FederationRuleUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=FederationRule,
        )

    def list(
        self,
        workload_identity_provider_id: str,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        service_account_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPage[FederationRule]:
        """
        List the provider's federation rules to project service accounts.

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
        return self._get_api_list(
            path_template(
                "/organization/workload_identity_providers/{workload_identity_provider_id}/federation_rules",
                workload_identity_provider_id=workload_identity_provider_id,
            ),
            page=SyncCursorPage[FederationRule],
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
                        "service_account_id": service_account_id,
                    },
                    federation_rule_list_params.FederationRuleListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=FederationRule,
        )

    def delete(
        self,
        workload_identity_federation_rule_id: str,
        *,
        workload_identity_provider_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> FederationRuleDeleted:
        """
        Delete a federation rule to a project service account.

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
        if not workload_identity_federation_rule_id:
            raise ValueError(
                f"Expected a non-empty value for `workload_identity_federation_rule_id` but received {workload_identity_federation_rule_id!r}"
            )
        return self._delete(
            path_template(
                "/organization/workload_identity_providers/{workload_identity_provider_id}/federation_rules/{workload_identity_federation_rule_id}",
                workload_identity_provider_id=workload_identity_provider_id,
                workload_identity_federation_rule_id=workload_identity_federation_rule_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=FederationRuleDeleted,
        )


class AsyncFederationRules(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFederationRulesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncFederationRulesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFederationRulesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncFederationRulesWithStreamingResponse(self)

    async def create(
        self,
        workload_identity_provider_id: str,
        *,
        attribute_matchers: Dict[str, Union[str, bool, Union[int, float]]],
        project_id: str,
        service_account_id: str,
        description: str | Omit = omit,
        enabled: bool | Omit = omit,
        name: str | Omit = omit,
        permissions: federation_rule_create_params.Permissions | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> FederationRule:
        """
        Bind verified token attributes to an existing project service account.

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
                "/organization/workload_identity_providers/{workload_identity_provider_id}/federation_rules",
                workload_identity_provider_id=workload_identity_provider_id,
            ),
            body=await async_maybe_transform(
                {
                    "attribute_matchers": attribute_matchers,
                    "project_id": project_id,
                    "service_account_id": service_account_id,
                    "description": description,
                    "enabled": enabled,
                    "name": name,
                    "permissions": permissions,
                },
                federation_rule_create_params.FederationRuleCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=FederationRule,
        )

    async def retrieve(
        self,
        workload_identity_federation_rule_id: str,
        *,
        workload_identity_provider_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> FederationRule:
        """
        Retrieve a federation rule owned by the authenticated organization and provider.

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
        if not workload_identity_federation_rule_id:
            raise ValueError(
                f"Expected a non-empty value for `workload_identity_federation_rule_id` but received {workload_identity_federation_rule_id!r}"
            )
        return await self._get(
            path_template(
                "/organization/workload_identity_providers/{workload_identity_provider_id}/federation_rules/{workload_identity_federation_rule_id}",
                workload_identity_provider_id=workload_identity_provider_id,
                workload_identity_federation_rule_id=workload_identity_federation_rule_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=FederationRule,
        )

    async def update(
        self,
        workload_identity_federation_rule_id: str,
        *,
        workload_identity_provider_id: str,
        attribute_matchers: Dict[str, Union[str, bool, Union[int, float]]] | Omit = omit,
        description: Optional[str] | Omit = omit,
        enabled: bool | Omit = omit,
        name: Optional[str] | Omit = omit,
        permissions: federation_rule_update_params.Permissions | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> FederationRule:
        """
        Update supplied matcher, permission, metadata, or enabled fields.

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
        if not workload_identity_federation_rule_id:
            raise ValueError(
                f"Expected a non-empty value for `workload_identity_federation_rule_id` but received {workload_identity_federation_rule_id!r}"
            )
        return await self._post(
            path_template(
                "/organization/workload_identity_providers/{workload_identity_provider_id}/federation_rules/{workload_identity_federation_rule_id}",
                workload_identity_provider_id=workload_identity_provider_id,
                workload_identity_federation_rule_id=workload_identity_federation_rule_id,
            ),
            body=await async_maybe_transform(
                {
                    "attribute_matchers": attribute_matchers,
                    "description": description,
                    "enabled": enabled,
                    "name": name,
                    "permissions": permissions,
                },
                federation_rule_update_params.FederationRuleUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=FederationRule,
        )

    def list(
        self,
        workload_identity_provider_id: str,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        service_account_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[FederationRule, AsyncCursorPage[FederationRule]]:
        """
        List the provider's federation rules to project service accounts.

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
        return self._get_api_list(
            path_template(
                "/organization/workload_identity_providers/{workload_identity_provider_id}/federation_rules",
                workload_identity_provider_id=workload_identity_provider_id,
            ),
            page=AsyncCursorPage[FederationRule],
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
                        "service_account_id": service_account_id,
                    },
                    federation_rule_list_params.FederationRuleListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=FederationRule,
        )

    async def delete(
        self,
        workload_identity_federation_rule_id: str,
        *,
        workload_identity_provider_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> FederationRuleDeleted:
        """
        Delete a federation rule to a project service account.

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
        if not workload_identity_federation_rule_id:
            raise ValueError(
                f"Expected a non-empty value for `workload_identity_federation_rule_id` but received {workload_identity_federation_rule_id!r}"
            )
        return await self._delete(
            path_template(
                "/organization/workload_identity_providers/{workload_identity_provider_id}/federation_rules/{workload_identity_federation_rule_id}",
                workload_identity_provider_id=workload_identity_provider_id,
                workload_identity_federation_rule_id=workload_identity_federation_rule_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=FederationRuleDeleted,
        )


class FederationRulesWithRawResponse:
    def __init__(self, federation_rules: FederationRules) -> None:
        self._federation_rules = federation_rules

        self.create = _legacy_response.to_raw_response_wrapper(
            federation_rules.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            federation_rules.retrieve,
        )
        self.update = _legacy_response.to_raw_response_wrapper(
            federation_rules.update,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            federation_rules.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            federation_rules.delete,
        )


class AsyncFederationRulesWithRawResponse:
    def __init__(self, federation_rules: AsyncFederationRules) -> None:
        self._federation_rules = federation_rules

        self.create = _legacy_response.async_to_raw_response_wrapper(
            federation_rules.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            federation_rules.retrieve,
        )
        self.update = _legacy_response.async_to_raw_response_wrapper(
            federation_rules.update,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            federation_rules.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            federation_rules.delete,
        )


class FederationRulesWithStreamingResponse:
    def __init__(self, federation_rules: FederationRules) -> None:
        self._federation_rules = federation_rules

        self.create = to_streamed_response_wrapper(
            federation_rules.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            federation_rules.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            federation_rules.update,
        )
        self.list = to_streamed_response_wrapper(
            federation_rules.list,
        )
        self.delete = to_streamed_response_wrapper(
            federation_rules.delete,
        )


class AsyncFederationRulesWithStreamingResponse:
    def __init__(self, federation_rules: AsyncFederationRules) -> None:
        self._federation_rules = federation_rules

        self.create = async_to_streamed_response_wrapper(
            federation_rules.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            federation_rules.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            federation_rules.update,
        )
        self.list = async_to_streamed_response_wrapper(
            federation_rules.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            federation_rules.delete,
        )
