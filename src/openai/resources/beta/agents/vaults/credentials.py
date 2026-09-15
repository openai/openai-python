# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
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
from .....types.beta.agents.vaults import (
    credential_list_params,
    credential_create_params,
    credential_update_params,
)
from .....types.beta.agents.vaults.credential import Credential
from .....types.beta.agents.vault_status_filter_param import VaultStatusFilterParam
from .....types.beta.agents.vaults.credential_deleted import CredentialDeleted
from .....types.beta.agents.vaults.credential_auth_create_param import CredentialAuthCreateParam
from .....types.beta.agents.vaults.credential_auth_rotate_param import CredentialAuthRotateParam

__all__ = ["Credentials", "AsyncCredentials"]


class Credentials(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CredentialsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return CredentialsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CredentialsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return CredentialsWithStreamingResponse(self)

    def create(
        self,
        vault_id: str,
        *,
        auth: CredentialAuthCreateParam,
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Credential:
        """Creates a vault credential.

        Secret values are write-only and are never returned.
        See
        [vaults](https://developers.openai.com/api/docs/guides/agents-api/tools/vaults).

        Args:
          auth: The authentication method and secret values to store for the MCP server.

          name: The name is trimmed before storage. It must contain 1 to 256 UTF-8 bytes after
              trimming.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vault_id:
            raise ValueError(f"Expected a non-empty value for `vault_id` but received {vault_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._post(
            path_template("/vaults/{vault_id}/credentials", vault_id=vault_id),
            body=maybe_transform(
                {
                    "auth": auth,
                    "name": name,
                },
                credential_create_params.CredentialCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Credential,
        )

    def retrieve(
        self,
        credential_id: str,
        *,
        vault_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Credential:
        """Retrieves vault credential metadata without returning secret values.

        See
        [vaults](https://developers.openai.com/api/docs/guides/agents-api/tools/vaults).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vault_id:
            raise ValueError(f"Expected a non-empty value for `vault_id` but received {vault_id!r}")
        if not credential_id:
            raise ValueError(f"Expected a non-empty value for `credential_id` but received {credential_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get(
            path_template(
                "/vaults/{vault_id}/credentials/{credential_id}", vault_id=vault_id, credential_id=credential_id
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Credential,
        )

    def update(
        self,
        credential_id: str,
        *,
        vault_id: str,
        auth: CredentialAuthRotateParam,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Credential:
        """
        Rotates a vault credential's write-only secret and returns only credential
        metadata. See
        [vaults](https://developers.openai.com/api/docs/guides/agents-api/tools/vaults).

        Args:
          auth: Replacement values for the credential's existing authentication method.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vault_id:
            raise ValueError(f"Expected a non-empty value for `vault_id` but received {vault_id!r}")
        if not credential_id:
            raise ValueError(f"Expected a non-empty value for `credential_id` but received {credential_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._post(
            path_template(
                "/vaults/{vault_id}/credentials/{credential_id}", vault_id=vault_id, credential_id=credential_id
            ),
            body=maybe_transform({"auth": auth}, credential_update_params.CredentialUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Credential,
        )

    def list(
        self,
        vault_id: str,
        *,
        after: str | Omit = omit,
        limit: Optional[int] | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        status: VaultStatusFilterParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPage[Credential]:
        """
        Lists a vault's credentials using ID-based pagination without returning secret
        values. See
        [vaults](https://developers.openai.com/api/docs/guides/agents-api/tools/vaults).

        Args:
          after: Return resources after this resource ID in the selected order.

          limit: The maximum number of resources to return. Defaults to 20. Values are clamped
              between 1 and 100.

          order: Sort order by the `created_at` timestamp. Use `asc` for ascending order or
              `desc` for descending order. Defaults to `desc`.

              - `asc` - Returns resources in ascending order.
              - `desc` - Returns resources in descending order.

          status: Filter by one status or a list, such as `status=active` or
              `status[]=active&status[]=archived`. Both statuses are included by default.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vault_id:
            raise ValueError(f"Expected a non-empty value for `vault_id` but received {vault_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get_api_list(
            path_template("/vaults/{vault_id}/credentials", vault_id=vault_id),
            page=SyncCursorPage[Credential],
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
                        "status": status,
                    },
                    credential_list_params.CredentialListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=Credential,
        )

    def delete(
        self,
        credential_id: str,
        *,
        vault_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> CredentialDeleted:
        """Deletes a vault credential.

        See
        [vaults](https://developers.openai.com/api/docs/guides/agents-api/tools/vaults).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vault_id:
            raise ValueError(f"Expected a non-empty value for `vault_id` but received {vault_id!r}")
        if not credential_id:
            raise ValueError(f"Expected a non-empty value for `credential_id` but received {credential_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._delete(
            path_template(
                "/vaults/{vault_id}/credentials/{credential_id}", vault_id=vault_id, credential_id=credential_id
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=CredentialDeleted,
        )


class AsyncCredentials(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCredentialsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCredentialsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCredentialsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncCredentialsWithStreamingResponse(self)

    async def create(
        self,
        vault_id: str,
        *,
        auth: CredentialAuthCreateParam,
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Credential:
        """Creates a vault credential.

        Secret values are write-only and are never returned.
        See
        [vaults](https://developers.openai.com/api/docs/guides/agents-api/tools/vaults).

        Args:
          auth: The authentication method and secret values to store for the MCP server.

          name: The name is trimmed before storage. It must contain 1 to 256 UTF-8 bytes after
              trimming.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vault_id:
            raise ValueError(f"Expected a non-empty value for `vault_id` but received {vault_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._post(
            path_template("/vaults/{vault_id}/credentials", vault_id=vault_id),
            body=await async_maybe_transform(
                {
                    "auth": auth,
                    "name": name,
                },
                credential_create_params.CredentialCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Credential,
        )

    async def retrieve(
        self,
        credential_id: str,
        *,
        vault_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Credential:
        """Retrieves vault credential metadata without returning secret values.

        See
        [vaults](https://developers.openai.com/api/docs/guides/agents-api/tools/vaults).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vault_id:
            raise ValueError(f"Expected a non-empty value for `vault_id` but received {vault_id!r}")
        if not credential_id:
            raise ValueError(f"Expected a non-empty value for `credential_id` but received {credential_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._get(
            path_template(
                "/vaults/{vault_id}/credentials/{credential_id}", vault_id=vault_id, credential_id=credential_id
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Credential,
        )

    async def update(
        self,
        credential_id: str,
        *,
        vault_id: str,
        auth: CredentialAuthRotateParam,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Credential:
        """
        Rotates a vault credential's write-only secret and returns only credential
        metadata. See
        [vaults](https://developers.openai.com/api/docs/guides/agents-api/tools/vaults).

        Args:
          auth: Replacement values for the credential's existing authentication method.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vault_id:
            raise ValueError(f"Expected a non-empty value for `vault_id` but received {vault_id!r}")
        if not credential_id:
            raise ValueError(f"Expected a non-empty value for `credential_id` but received {credential_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._post(
            path_template(
                "/vaults/{vault_id}/credentials/{credential_id}", vault_id=vault_id, credential_id=credential_id
            ),
            body=await async_maybe_transform({"auth": auth}, credential_update_params.CredentialUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Credential,
        )

    def list(
        self,
        vault_id: str,
        *,
        after: str | Omit = omit,
        limit: Optional[int] | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        status: VaultStatusFilterParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[Credential, AsyncCursorPage[Credential]]:
        """
        Lists a vault's credentials using ID-based pagination without returning secret
        values. See
        [vaults](https://developers.openai.com/api/docs/guides/agents-api/tools/vaults).

        Args:
          after: Return resources after this resource ID in the selected order.

          limit: The maximum number of resources to return. Defaults to 20. Values are clamped
              between 1 and 100.

          order: Sort order by the `created_at` timestamp. Use `asc` for ascending order or
              `desc` for descending order. Defaults to `desc`.

              - `asc` - Returns resources in ascending order.
              - `desc` - Returns resources in descending order.

          status: Filter by one status or a list, such as `status=active` or
              `status[]=active&status[]=archived`. Both statuses are included by default.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vault_id:
            raise ValueError(f"Expected a non-empty value for `vault_id` but received {vault_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get_api_list(
            path_template("/vaults/{vault_id}/credentials", vault_id=vault_id),
            page=AsyncCursorPage[Credential],
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
                        "status": status,
                    },
                    credential_list_params.CredentialListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=Credential,
        )

    async def delete(
        self,
        credential_id: str,
        *,
        vault_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> CredentialDeleted:
        """Deletes a vault credential.

        See
        [vaults](https://developers.openai.com/api/docs/guides/agents-api/tools/vaults).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not vault_id:
            raise ValueError(f"Expected a non-empty value for `vault_id` but received {vault_id!r}")
        if not credential_id:
            raise ValueError(f"Expected a non-empty value for `credential_id` but received {credential_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._delete(
            path_template(
                "/vaults/{vault_id}/credentials/{credential_id}", vault_id=vault_id, credential_id=credential_id
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=CredentialDeleted,
        )


class CredentialsWithRawResponse:
    def __init__(self, credentials: Credentials) -> None:
        self._credentials = credentials

        self.create = _legacy_response.to_raw_response_wrapper(
            credentials.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            credentials.retrieve,
        )
        self.update = _legacy_response.to_raw_response_wrapper(
            credentials.update,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            credentials.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            credentials.delete,
        )


class AsyncCredentialsWithRawResponse:
    def __init__(self, credentials: AsyncCredentials) -> None:
        self._credentials = credentials

        self.create = _legacy_response.async_to_raw_response_wrapper(
            credentials.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            credentials.retrieve,
        )
        self.update = _legacy_response.async_to_raw_response_wrapper(
            credentials.update,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            credentials.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            credentials.delete,
        )


class CredentialsWithStreamingResponse:
    def __init__(self, credentials: Credentials) -> None:
        self._credentials = credentials

        self.create = to_streamed_response_wrapper(
            credentials.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            credentials.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            credentials.update,
        )
        self.list = to_streamed_response_wrapper(
            credentials.list,
        )
        self.delete = to_streamed_response_wrapper(
            credentials.delete,
        )


class AsyncCredentialsWithStreamingResponse:
    def __init__(self, credentials: AsyncCredentials) -> None:
        self._credentials = credentials

        self.create = async_to_streamed_response_wrapper(
            credentials.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            credentials.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            credentials.update,
        )
        self.list = async_to_streamed_response_wrapper(
            credentials.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            credentials.delete,
        )
