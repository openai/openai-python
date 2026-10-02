# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Literal

import httpx2

from ..... import _legacy_response
from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ....._utils import path_template, maybe_transform, async_maybe_transform
from ....._compat import cached_property
from .credentials import (
    Credentials,
    AsyncCredentials,
    CredentialsWithRawResponse,
    AsyncCredentialsWithRawResponse,
    CredentialsWithStreamingResponse,
    AsyncCredentialsWithStreamingResponse,
)
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from .....pagination import SyncCursorPage, AsyncCursorPage
from ....._base_client import AsyncPaginator, make_request_options
from .....types.beta.agents import vault_list_params, vault_create_params
from .....types.beta.agents.vault import Vault
from .....types.beta.agents.vault_deleted import VaultDeleted
from .....types.beta.agents.vault_status_filter_param import VaultStatusFilterParam

__all__ = ["Vaults", "AsyncVaults"]


class Vaults(SyncAPIResource):
    @cached_property
    def credentials(self) -> Credentials:
        return Credentials(self._client)

    @cached_property
    def with_raw_response(self) -> VaultsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return VaultsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> VaultsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return VaultsWithStreamingResponse(self)

    def create(
        self,
        *,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Vault:
        """Creates a vault for the current project.

        See
        [vaults](https://developers.openai.com/api/docs/guides/agents-api/tools/vaults).

        Args:
          metadata: Key-value pairs to associate with the vault, such as an application or team
              identifier.

          name: The name is trimmed before storage. It must contain 1 to 256 UTF-8 bytes after
              trimming.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._post(
            "/vaults",
            body=maybe_transform(
                {
                    "metadata": metadata,
                    "name": name,
                },
                vault_create_params.VaultCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Vault,
        )

    def retrieve(
        self,
        vault_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Vault:
        """Retrieves a vault by its ID.

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
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get(
            path_template("/vaults/{vault_id}", vault_id=vault_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Vault,
        )

    def list(
        self,
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
    ) -> SyncCursorPage[Vault]:
        """Lists vaults using ID-based pagination.

        See
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
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get_api_list(
            "/vaults",
            page=SyncCursorPage[Vault],
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
                    vault_list_params.VaultListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=Vault,
        )

    def delete(
        self,
        vault_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> VaultDeleted:
        """Deletes a vault and all its credentials.

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
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._delete(
            path_template("/vaults/{vault_id}", vault_id=vault_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=VaultDeleted,
        )


class AsyncVaults(AsyncAPIResource):
    @cached_property
    def credentials(self) -> AsyncCredentials:
        return AsyncCredentials(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncVaultsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncVaultsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncVaultsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncVaultsWithStreamingResponse(self)

    async def create(
        self,
        *,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Vault:
        """Creates a vault for the current project.

        See
        [vaults](https://developers.openai.com/api/docs/guides/agents-api/tools/vaults).

        Args:
          metadata: Key-value pairs to associate with the vault, such as an application or team
              identifier.

          name: The name is trimmed before storage. It must contain 1 to 256 UTF-8 bytes after
              trimming.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._post(
            "/vaults",
            body=await async_maybe_transform(
                {
                    "metadata": metadata,
                    "name": name,
                },
                vault_create_params.VaultCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Vault,
        )

    async def retrieve(
        self,
        vault_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Vault:
        """Retrieves a vault by its ID.

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
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._get(
            path_template("/vaults/{vault_id}", vault_id=vault_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Vault,
        )

    def list(
        self,
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
    ) -> AsyncPaginator[Vault, AsyncCursorPage[Vault]]:
        """Lists vaults using ID-based pagination.

        See
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
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get_api_list(
            "/vaults",
            page=AsyncCursorPage[Vault],
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
                    vault_list_params.VaultListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=Vault,
        )

    async def delete(
        self,
        vault_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> VaultDeleted:
        """Deletes a vault and all its credentials.

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
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._delete(
            path_template("/vaults/{vault_id}", vault_id=vault_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=VaultDeleted,
        )


class VaultsWithRawResponse:
    def __init__(self, vaults: Vaults) -> None:
        self._vaults = vaults

        self.create = _legacy_response.to_raw_response_wrapper(
            vaults.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            vaults.retrieve,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            vaults.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            vaults.delete,
        )

    @cached_property
    def credentials(self) -> CredentialsWithRawResponse:
        return CredentialsWithRawResponse(self._vaults.credentials)


class AsyncVaultsWithRawResponse:
    def __init__(self, vaults: AsyncVaults) -> None:
        self._vaults = vaults

        self.create = _legacy_response.async_to_raw_response_wrapper(
            vaults.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            vaults.retrieve,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            vaults.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            vaults.delete,
        )

    @cached_property
    def credentials(self) -> AsyncCredentialsWithRawResponse:
        return AsyncCredentialsWithRawResponse(self._vaults.credentials)


class VaultsWithStreamingResponse:
    def __init__(self, vaults: Vaults) -> None:
        self._vaults = vaults

        self.create = to_streamed_response_wrapper(
            vaults.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            vaults.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            vaults.list,
        )
        self.delete = to_streamed_response_wrapper(
            vaults.delete,
        )

    @cached_property
    def credentials(self) -> CredentialsWithStreamingResponse:
        return CredentialsWithStreamingResponse(self._vaults.credentials)


class AsyncVaultsWithStreamingResponse:
    def __init__(self, vaults: AsyncVaults) -> None:
        self._vaults = vaults

        self.create = async_to_streamed_response_wrapper(
            vaults.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            vaults.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            vaults.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            vaults.delete,
        )

    @cached_property
    def credentials(self) -> AsyncCredentialsWithStreamingResponse:
        return AsyncCredentialsWithStreamingResponse(self._vaults.credentials)
