# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal

import httpx2

from ..... import _legacy_response
from .files import (
    Files,
    AsyncFiles,
    FilesWithRawResponse,
    AsyncFilesWithRawResponse,
    FilesWithStreamingResponse,
    AsyncFilesWithStreamingResponse,
)
from .templates import (
    Templates,
    AsyncTemplates,
    TemplatesWithRawResponse,
    AsyncTemplatesWithRawResponse,
    TemplatesWithStreamingResponse,
    AsyncTemplatesWithStreamingResponse,
)
from ....._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from ....._utils import path_template, maybe_transform, strip_not_given, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from .....pagination import SyncCursorPage, AsyncCursorPage
from ....._base_client import AsyncPaginator, make_request_options
from .....types.beta.agents import environment_list_params, environment_create_params
from .....types.beta.agents.environment_info import EnvironmentInfo

__all__ = ["Environments", "AsyncEnvironments"]


class Environments(SyncAPIResource):
    @cached_property
    def files(self) -> Files:
        return Files(self._client)

    @cached_property
    def templates(self) -> Templates:
        return Templates(self._client)

    @cached_property
    def with_raw_response(self) -> EnvironmentsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return EnvironmentsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EnvironmentsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return EnvironmentsWithStreamingResponse(self)

    def create(
        self,
        *,
        environment: environment_create_params.Environment,
        vault_ids: Optional[SequenceNotStr[str]] | Omit = omit,
        idempotency_key: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentInfo:
        """Creates an OpenAI-hosted environment before creating a session.

        Requires access
        to the prewarming beta.

        Args:
          environment: The required hosting type and its configuration.

          vault_ids: The IDs of up to 10 vaults made available to an OpenAI-hosted environment.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"Idempotency-Key": idempotency_key}), **(extra_headers or {})}
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._post(
            "/agents/environments",
            body=maybe_transform(
                {
                    "environment": environment,
                    "vault_ids": vault_ids,
                },
                environment_create_params.EnvironmentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=EnvironmentInfo,
        )

    def retrieve(
        self,
        environment_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentInfo:
        """
        Retrieves an execution environment's connection status and safe installed
        metadata. See
        [environment lifecycle](https://developers.openai.com/api/docs/guides/agents-api/environments/lifecycle).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not environment_id:
            raise ValueError(f"Expected a non-empty value for `environment_id` but received {environment_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get(
            path_template("/agents/environments/{environment_id}", environment_id=environment_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=EnvironmentInfo,
        )

    def list(
        self,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        type: Literal["openai_hosted"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPage[EnvironmentInfo]:
        """Lists OpenAI-hosted environments owned by the authenticated principal.

        Requires
        access to the prewarming beta.

        Args:
          after: Return environments after this environment ID in the selected order.

          limit: The maximum number of environments to return, between 1 and 100. Defaults to 20.

          order: The order in which environments are returned. Defaults to `desc`.

              - `asc` - Returns resources in ascending order.
              - `desc` - Returns resources in descending order.

          type: The hosting type to list. Defaults to `openai_hosted`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get_api_list(
            "/agents/environments",
            page=SyncCursorPage[EnvironmentInfo],
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
                        "type": type,
                    },
                    environment_list_params.EnvironmentListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=EnvironmentInfo,
        )


class AsyncEnvironments(AsyncAPIResource):
    @cached_property
    def files(self) -> AsyncFiles:
        return AsyncFiles(self._client)

    @cached_property
    def templates(self) -> AsyncTemplates:
        return AsyncTemplates(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncEnvironmentsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncEnvironmentsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEnvironmentsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncEnvironmentsWithStreamingResponse(self)

    async def create(
        self,
        *,
        environment: environment_create_params.Environment,
        vault_ids: Optional[SequenceNotStr[str]] | Omit = omit,
        idempotency_key: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentInfo:
        """Creates an OpenAI-hosted environment before creating a session.

        Requires access
        to the prewarming beta.

        Args:
          environment: The required hosting type and its configuration.

          vault_ids: The IDs of up to 10 vaults made available to an OpenAI-hosted environment.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"Idempotency-Key": idempotency_key}), **(extra_headers or {})}
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._post(
            "/agents/environments",
            body=await async_maybe_transform(
                {
                    "environment": environment,
                    "vault_ids": vault_ids,
                },
                environment_create_params.EnvironmentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=EnvironmentInfo,
        )

    async def retrieve(
        self,
        environment_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentInfo:
        """
        Retrieves an execution environment's connection status and safe installed
        metadata. See
        [environment lifecycle](https://developers.openai.com/api/docs/guides/agents-api/environments/lifecycle).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not environment_id:
            raise ValueError(f"Expected a non-empty value for `environment_id` but received {environment_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._get(
            path_template("/agents/environments/{environment_id}", environment_id=environment_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=EnvironmentInfo,
        )

    def list(
        self,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        type: Literal["openai_hosted"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[EnvironmentInfo, AsyncCursorPage[EnvironmentInfo]]:
        """Lists OpenAI-hosted environments owned by the authenticated principal.

        Requires
        access to the prewarming beta.

        Args:
          after: Return environments after this environment ID in the selected order.

          limit: The maximum number of environments to return, between 1 and 100. Defaults to 20.

          order: The order in which environments are returned. Defaults to `desc`.

              - `asc` - Returns resources in ascending order.
              - `desc` - Returns resources in descending order.

          type: The hosting type to list. Defaults to `openai_hosted`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get_api_list(
            "/agents/environments",
            page=AsyncCursorPage[EnvironmentInfo],
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
                        "type": type,
                    },
                    environment_list_params.EnvironmentListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=EnvironmentInfo,
        )


class EnvironmentsWithRawResponse:
    def __init__(self, environments: Environments) -> None:
        self._environments = environments

        self.create = _legacy_response.to_raw_response_wrapper(
            environments.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            environments.retrieve,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            environments.list,
        )

    @cached_property
    def files(self) -> FilesWithRawResponse:
        return FilesWithRawResponse(self._environments.files)

    @cached_property
    def templates(self) -> TemplatesWithRawResponse:
        return TemplatesWithRawResponse(self._environments.templates)


class AsyncEnvironmentsWithRawResponse:
    def __init__(self, environments: AsyncEnvironments) -> None:
        self._environments = environments

        self.create = _legacy_response.async_to_raw_response_wrapper(
            environments.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            environments.retrieve,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            environments.list,
        )

    @cached_property
    def files(self) -> AsyncFilesWithRawResponse:
        return AsyncFilesWithRawResponse(self._environments.files)

    @cached_property
    def templates(self) -> AsyncTemplatesWithRawResponse:
        return AsyncTemplatesWithRawResponse(self._environments.templates)


class EnvironmentsWithStreamingResponse:
    def __init__(self, environments: Environments) -> None:
        self._environments = environments

        self.create = to_streamed_response_wrapper(
            environments.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            environments.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            environments.list,
        )

    @cached_property
    def files(self) -> FilesWithStreamingResponse:
        return FilesWithStreamingResponse(self._environments.files)

    @cached_property
    def templates(self) -> TemplatesWithStreamingResponse:
        return TemplatesWithStreamingResponse(self._environments.templates)


class AsyncEnvironmentsWithStreamingResponse:
    def __init__(self, environments: AsyncEnvironments) -> None:
        self._environments = environments

        self.create = async_to_streamed_response_wrapper(
            environments.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            environments.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            environments.list,
        )

    @cached_property
    def files(self) -> AsyncFilesWithStreamingResponse:
        return AsyncFilesWithStreamingResponse(self._environments.files)

    @cached_property
    def templates(self) -> AsyncTemplatesWithStreamingResponse:
        return AsyncTemplatesWithStreamingResponse(self._environments.templates)
