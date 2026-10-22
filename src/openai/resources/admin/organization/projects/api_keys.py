# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx2

from ..... import _legacy_response
from ....._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from ....._utils import path_template, maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from .....pagination import SyncConversationCursorPage, AsyncConversationCursorPage
from ....._base_client import AsyncPaginator, make_request_options
from .....types.admin.organization.projects import api_key_list_params, api_key_update_params
from .....types.admin.organization.projects.project_api_key import ProjectAPIKey
from .....types.admin.organization.projects.api_key_delete_response import APIKeyDeleteResponse

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

    def retrieve(
        self,
        api_key_id: str,
        *,
        project_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ProjectAPIKey:
        """
        Retrieves an API key in the project.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not api_key_id:
            raise ValueError(f"Expected a non-empty value for `api_key_id` but received {api_key_id!r}")
        return self._get(
            path_template(
                "/organization/projects/{project_id}/api_keys/{api_key_id}",
                project_id=project_id,
                api_key_id=api_key_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectAPIKey,
        )

    def update(
        self,
        api_key_id: str,
        *,
        project_id: str,
        expires_in_seconds: int | Omit = omit,
        scopes: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ProjectAPIKey:
        """
        Updates the scopes and/or expiration of an existing API key in the project,
        including a service-account-owned key. Requires permission to write project API
        keys.

        Provide at least one of `scopes` or `expires_in_seconds`. Omitted fields stay
        unchanged; neither field accepts `null`. Both changes are saved together.

        `scopes` replaces the key's scope restrictions using the same scope identifiers
        as the dashboard. An empty array means All permissions, subject to the owner's
        effective access; it does not mean no access. Use `["api.all.read"]` for
        read-only access or specific scopes such as `["api.files.read"]` for restricted
        access. This does not change user or service-account roles or grant admin
        permissions. Scope changes follow the same authentication-cache propagation as
        dashboard edits.

        Provide `expires_in_seconds` to set the expiration relative to this request.
        The value must satisfy the organization's and project's expiry policies.
        Expired keys cannot be updated. Retrying resets the expiration relative to
        the new request. The response contains only the redacted key, not its secret.

        Args:
          expires_in_seconds: Number of seconds from this request until the API key expires. Must comply with
              the organization and project expiry policies. Expired keys cannot be updated.
              Retrying resets the expiry relative to the new request. Omit to keep the current
              expiration.

          scopes: Replace the API key scope restrictions. Omit to leave scopes unchanged. An empty
              array removes key restrictions (All permissions), subject to the owner's
              effective permissions. Use ["api.all.read"] for read-only access. Scopes do not
              change the owner's roles or grant administrative permissions.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not api_key_id:
            raise ValueError(f"Expected a non-empty value for `api_key_id` but received {api_key_id!r}")
        return self._post(
            path_template(
                "/organization/projects/{project_id}/api_keys/{api_key_id}",
                project_id=project_id,
                api_key_id=api_key_id,
            ),
            body=maybe_transform(
                {
                    "expires_in_seconds": expires_in_seconds,
                    "scopes": scopes,
                },
                api_key_update_params.APIKeyUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectAPIKey,
        )

    def list(
        self,
        project_id: str,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        owner_project_access: Literal["active", "inactive", "any"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SyncConversationCursorPage[ProjectAPIKey]:
        """
        Returns a list of API keys in the project.

        Args:
          after: A cursor for use in pagination. `after` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include after=obj_foo in order to
              fetch the next page of the list.

          limit: A limit on the number of objects to be returned. Limit can range between 1 and
              100, and the default is 20.

          owner_project_access: Filter API keys by whether the owner currently has effective access to the
              project. Use `active` for owners with access, `inactive` for owners without
              access, or `any` for all enabled project API keys. If omitted, the endpoint
              applies its existing membership-based visibility rules, which may exclude some
              enabled keys.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get_api_list(
            path_template("/organization/projects/{project_id}/api_keys", project_id=project_id),
            page=SyncConversationCursorPage[ProjectAPIKey],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                        "owner_project_access": owner_project_access,
                    },
                    api_key_list_params.APIKeyListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=ProjectAPIKey,
        )

    def delete(
        self,
        api_key_id: str,
        *,
        project_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> APIKeyDeleteResponse:
        """
        Deletes an API key from the project, including keys owned by service accounts.

        Requires permission to write project API keys. Deleting a service-account key
        does not delete the service account or its other keys.

        Returns confirmation of the key deletion.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not api_key_id:
            raise ValueError(f"Expected a non-empty value for `api_key_id` but received {api_key_id!r}")
        return self._delete(
            path_template(
                "/organization/projects/{project_id}/api_keys/{api_key_id}",
                project_id=project_id,
                api_key_id=api_key_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=APIKeyDeleteResponse,
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

    async def retrieve(
        self,
        api_key_id: str,
        *,
        project_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ProjectAPIKey:
        """
        Retrieves an API key in the project.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not api_key_id:
            raise ValueError(f"Expected a non-empty value for `api_key_id` but received {api_key_id!r}")
        return await self._get(
            path_template(
                "/organization/projects/{project_id}/api_keys/{api_key_id}",
                project_id=project_id,
                api_key_id=api_key_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectAPIKey,
        )

    async def update(
        self,
        api_key_id: str,
        *,
        project_id: str,
        expires_in_seconds: int | Omit = omit,
        scopes: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> ProjectAPIKey:
        """
        Updates the scopes and/or expiration of an existing API key in the project,
        including a service-account-owned key. Requires permission to write project API
        keys.

        Provide at least one of `scopes` or `expires_in_seconds`. Omitted fields stay
        unchanged; neither field accepts `null`. Both changes are saved together.

        `scopes` replaces the key's scope restrictions using the same scope identifiers
        as the dashboard. An empty array means All permissions, subject to the owner's
        effective access; it does not mean no access. Use `["api.all.read"]` for
        read-only access or specific scopes such as `["api.files.read"]` for restricted
        access. This does not change user or service-account roles or grant admin
        permissions. Scope changes follow the same authentication-cache propagation as
        dashboard edits.

        Provide `expires_in_seconds` to set the expiration relative to this request.
        The value must satisfy the organization's and project's expiry policies.
        Expired keys cannot be updated. Retrying resets the expiration relative to
        the new request. The response contains only the redacted key, not its secret.

        Args:
          expires_in_seconds: Number of seconds from this request until the API key expires. Must comply with
              the organization and project expiry policies. Expired keys cannot be updated.
              Retrying resets the expiry relative to the new request. Omit to keep the current
              expiration.

          scopes: Replace the API key scope restrictions. Omit to leave scopes unchanged. An empty
              array removes key restrictions (All permissions), subject to the owner's
              effective permissions. Use ["api.all.read"] for read-only access. Scopes do not
              change the owner's roles or grant administrative permissions.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not api_key_id:
            raise ValueError(f"Expected a non-empty value for `api_key_id` but received {api_key_id!r}")
        return await self._post(
            path_template(
                "/organization/projects/{project_id}/api_keys/{api_key_id}",
                project_id=project_id,
                api_key_id=api_key_id,
            ),
            body=await async_maybe_transform(
                {
                    "expires_in_seconds": expires_in_seconds,
                    "scopes": scopes,
                },
                api_key_update_params.APIKeyUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=ProjectAPIKey,
        )

    def list(
        self,
        project_id: str,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        owner_project_access: Literal["active", "inactive", "any"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[ProjectAPIKey, AsyncConversationCursorPage[ProjectAPIKey]]:
        """
        Returns a list of API keys in the project.

        Args:
          after: A cursor for use in pagination. `after` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include after=obj_foo in order to
              fetch the next page of the list.

          limit: A limit on the number of objects to be returned. Limit can range between 1 and
              100, and the default is 20.

          owner_project_access: Filter API keys by whether the owner currently has effective access to the
              project. Use `active` for owners with access, `inactive` for owners without
              access, or `any` for all enabled project API keys. If omitted, the endpoint
              applies its existing membership-based visibility rules, which may exclude some
              enabled keys.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        return self._get_api_list(
            path_template("/organization/projects/{project_id}/api_keys", project_id=project_id),
            page=AsyncConversationCursorPage[ProjectAPIKey],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                        "owner_project_access": owner_project_access,
                    },
                    api_key_list_params.APIKeyListParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            model=ProjectAPIKey,
        )

    async def delete(
        self,
        api_key_id: str,
        *,
        project_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> APIKeyDeleteResponse:
        """
        Deletes an API key from the project, including keys owned by service accounts.

        Requires permission to write project API keys. Deleting a service-account key
        does not delete the service account or its other keys.

        Returns confirmation of the key deletion.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not project_id:
            raise ValueError(f"Expected a non-empty value for `project_id` but received {project_id!r}")
        if not api_key_id:
            raise ValueError(f"Expected a non-empty value for `api_key_id` but received {api_key_id!r}")
        return await self._delete(
            path_template(
                "/organization/projects/{project_id}/api_keys/{api_key_id}",
                project_id=project_id,
                api_key_id=api_key_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"admin_api_key_auth": True},
            ),
            cast_to=APIKeyDeleteResponse,
        )


class APIKeysWithRawResponse:
    def __init__(self, api_keys: APIKeys) -> None:
        self._api_keys = api_keys

        self.retrieve = _legacy_response.to_raw_response_wrapper(
            api_keys.retrieve,
        )
        self.update = _legacy_response.to_raw_response_wrapper(
            api_keys.update,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            api_keys.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            api_keys.delete,
        )


class AsyncAPIKeysWithRawResponse:
    def __init__(self, api_keys: AsyncAPIKeys) -> None:
        self._api_keys = api_keys

        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            api_keys.retrieve,
        )
        self.update = _legacy_response.async_to_raw_response_wrapper(
            api_keys.update,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            api_keys.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            api_keys.delete,
        )


class APIKeysWithStreamingResponse:
    def __init__(self, api_keys: APIKeys) -> None:
        self._api_keys = api_keys

        self.retrieve = to_streamed_response_wrapper(
            api_keys.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            api_keys.update,
        )
        self.list = to_streamed_response_wrapper(
            api_keys.list,
        )
        self.delete = to_streamed_response_wrapper(
            api_keys.delete,
        )


class AsyncAPIKeysWithStreamingResponse:
    def __init__(self, api_keys: AsyncAPIKeys) -> None:
        self._api_keys = api_keys

        self.retrieve = async_to_streamed_response_wrapper(
            api_keys.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            api_keys.update,
        )
        self.list = async_to_streamed_response_wrapper(
            api_keys.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            api_keys.delete,
        )
