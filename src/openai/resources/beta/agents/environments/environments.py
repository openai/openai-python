# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

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
from ....._types import Body, Query, Headers, NotGiven, not_given
from ....._utils import path_template
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ....._base_client import make_request_options
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


class EnvironmentsWithRawResponse:
    def __init__(self, environments: Environments) -> None:
        self._environments = environments

        self.retrieve = _legacy_response.to_raw_response_wrapper(
            environments.retrieve,
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

        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            environments.retrieve,
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

        self.retrieve = to_streamed_response_wrapper(
            environments.retrieve,
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

        self.retrieve = async_to_streamed_response_wrapper(
            environments.retrieve,
        )

    @cached_property
    def files(self) -> AsyncFilesWithStreamingResponse:
        return AsyncFilesWithStreamingResponse(self._environments.files)

    @cached_property
    def templates(self) -> AsyncTemplatesWithStreamingResponse:
        return AsyncTemplatesWithStreamingResponse(self._environments.templates)
