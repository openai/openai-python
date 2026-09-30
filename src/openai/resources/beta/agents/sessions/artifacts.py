# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal

import httpx2

from ..... import _legacy_response
from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ....._utils import path_template, maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
    to_streamed_response_wrapper,
    async_to_streamed_response_wrapper,
    to_custom_streamed_response_wrapper,
    async_to_custom_streamed_response_wrapper,
)
from .....pagination import SyncCursorPage, AsyncCursorPage
from ....._base_client import AsyncPaginator, make_request_options
from .....types.beta.agents.sessions import artifact_list_params
from .....types.beta.agents.sessions.session_artifact import SessionArtifact
from .....types.beta.agents.sessions.session_artifact_deleted import SessionArtifactDeleted

__all__ = ["Artifacts", "AsyncArtifacts"]


class Artifacts(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ArtifactsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return ArtifactsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ArtifactsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return ArtifactsWithStreamingResponse(self)

    def retrieve(
        self,
        artifact_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SessionArtifact:
        """Retrieves immutable metadata for one durable session artifact.

        See
        [session artifacts](https://developers.openai.com/api/docs/guides/agents-api/environments/files#openai-hosted-artifacts).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not artifact_id:
            raise ValueError(f"Expected a non-empty value for `artifact_id` but received {artifact_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get(
            path_template(
                "/agents/sessions/{session_id}/artifacts/{artifact_id}", session_id=session_id, artifact_id=artifact_id
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=SessionArtifact,
        )

    def list(
        self,
        session_id: str,
        *,
        after: Optional[str] | Omit = omit,
        environment_id: Optional[str] | Omit = omit,
        limit: Optional[int] | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPage[SessionArtifact]:
        """Lists immutable artifacts published by completed hosted session turns.

        See
        [session artifacts](https://developers.openai.com/api/docs/guides/agents-api/environments/files#openai-hosted-artifacts).

        Args:
          after: Return artifacts after this immutable artifact ID.

          environment_id: Restrict the listing to artifacts produced by this environment.

          limit: The maximum number of artifacts to return, between 1 and 100.

          order: Sort by creation time and ID. Defaults to descending.

              - `asc` - Returns resources in ascending order.
              - `desc` - Returns resources in descending order.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get_api_list(
            path_template("/agents/sessions/{session_id}/artifacts", session_id=session_id),
            page=SyncCursorPage[SessionArtifact],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "environment_id": environment_id,
                        "limit": limit,
                        "order": order,
                    },
                    artifact_list_params.ArtifactListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=SessionArtifact,
        )

    def delete(
        self,
        artifact_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SessionArtifactDeleted:
        """
        Deletes an immutable session artifact without deleting its live environment file
        or original Files API object. See
        [session artifacts](https://developers.openai.com/api/docs/guides/agents-api/environments/files#openai-hosted-artifacts).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not artifact_id:
            raise ValueError(f"Expected a non-empty value for `artifact_id` but received {artifact_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._delete(
            path_template(
                "/agents/sessions/{session_id}/artifacts/{artifact_id}", session_id=session_id, artifact_id=artifact_id
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=SessionArtifactDeleted,
        )

    def content(
        self,
        artifact_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> _legacy_response.HttpxBinaryResponseContent:
        """
        Downloads immutable session artifact bytes after the execution environment
        expires. See
        [session artifacts](https://developers.openai.com/api/docs/guides/agents-api/environments/files#openai-hosted-artifacts).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not artifact_id:
            raise ValueError(f"Expected a non-empty value for `artifact_id` but received {artifact_id!r}")
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get(
            path_template(
                "/agents/sessions/{session_id}/artifacts/{artifact_id}/content",
                session_id=session_id,
                artifact_id=artifact_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=_legacy_response.HttpxBinaryResponseContent,
        )


class AsyncArtifacts(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncArtifactsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncArtifactsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncArtifactsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncArtifactsWithStreamingResponse(self)

    async def retrieve(
        self,
        artifact_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SessionArtifact:
        """Retrieves immutable metadata for one durable session artifact.

        See
        [session artifacts](https://developers.openai.com/api/docs/guides/agents-api/environments/files#openai-hosted-artifacts).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not artifact_id:
            raise ValueError(f"Expected a non-empty value for `artifact_id` but received {artifact_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._get(
            path_template(
                "/agents/sessions/{session_id}/artifacts/{artifact_id}", session_id=session_id, artifact_id=artifact_id
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=SessionArtifact,
        )

    def list(
        self,
        session_id: str,
        *,
        after: Optional[str] | Omit = omit,
        environment_id: Optional[str] | Omit = omit,
        limit: Optional[int] | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[SessionArtifact, AsyncCursorPage[SessionArtifact]]:
        """Lists immutable artifacts published by completed hosted session turns.

        See
        [session artifacts](https://developers.openai.com/api/docs/guides/agents-api/environments/files#openai-hosted-artifacts).

        Args:
          after: Return artifacts after this immutable artifact ID.

          environment_id: Restrict the listing to artifacts produced by this environment.

          limit: The maximum number of artifacts to return, between 1 and 100.

          order: Sort by creation time and ID. Defaults to descending.

              - `asc` - Returns resources in ascending order.
              - `desc` - Returns resources in descending order.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get_api_list(
            path_template("/agents/sessions/{session_id}/artifacts", session_id=session_id),
            page=AsyncCursorPage[SessionArtifact],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "environment_id": environment_id,
                        "limit": limit,
                        "order": order,
                    },
                    artifact_list_params.ArtifactListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=SessionArtifact,
        )

    async def delete(
        self,
        artifact_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SessionArtifactDeleted:
        """
        Deletes an immutable session artifact without deleting its live environment file
        or original Files API object. See
        [session artifacts](https://developers.openai.com/api/docs/guides/agents-api/environments/files#openai-hosted-artifacts).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not artifact_id:
            raise ValueError(f"Expected a non-empty value for `artifact_id` but received {artifact_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._delete(
            path_template(
                "/agents/sessions/{session_id}/artifacts/{artifact_id}", session_id=session_id, artifact_id=artifact_id
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=SessionArtifactDeleted,
        )

    async def content(
        self,
        artifact_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> _legacy_response.HttpxBinaryResponseContent:
        """
        Downloads immutable session artifact bytes after the execution environment
        expires. See
        [session artifacts](https://developers.openai.com/api/docs/guides/agents-api/environments/files#openai-hosted-artifacts).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not artifact_id:
            raise ValueError(f"Expected a non-empty value for `artifact_id` but received {artifact_id!r}")
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._get(
            path_template(
                "/agents/sessions/{session_id}/artifacts/{artifact_id}/content",
                session_id=session_id,
                artifact_id=artifact_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=_legacy_response.HttpxBinaryResponseContent,
        )


class ArtifactsWithRawResponse:
    def __init__(self, artifacts: Artifacts) -> None:
        self._artifacts = artifacts

        self.retrieve = _legacy_response.to_raw_response_wrapper(
            artifacts.retrieve,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            artifacts.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            artifacts.delete,
        )
        self.content = _legacy_response.to_raw_response_wrapper(
            artifacts.content,
        )


class AsyncArtifactsWithRawResponse:
    def __init__(self, artifacts: AsyncArtifacts) -> None:
        self._artifacts = artifacts

        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            artifacts.retrieve,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            artifacts.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            artifacts.delete,
        )
        self.content = _legacy_response.async_to_raw_response_wrapper(
            artifacts.content,
        )


class ArtifactsWithStreamingResponse:
    def __init__(self, artifacts: Artifacts) -> None:
        self._artifacts = artifacts

        self.retrieve = to_streamed_response_wrapper(
            artifacts.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            artifacts.list,
        )
        self.delete = to_streamed_response_wrapper(
            artifacts.delete,
        )
        self.content = to_custom_streamed_response_wrapper(
            artifacts.content,
            StreamedBinaryAPIResponse,
        )


class AsyncArtifactsWithStreamingResponse:
    def __init__(self, artifacts: AsyncArtifacts) -> None:
        self._artifacts = artifacts

        self.retrieve = async_to_streamed_response_wrapper(
            artifacts.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            artifacts.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            artifacts.delete,
        )
        self.content = async_to_custom_streamed_response_wrapper(
            artifacts.content,
            AsyncStreamedBinaryAPIResponse,
        )
