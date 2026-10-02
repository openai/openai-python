# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx2

from ...... import _legacy_response
from .items import (
    Items,
    AsyncItems,
    ItemsWithRawResponse,
    AsyncItemsWithRawResponse,
    ItemsWithStreamingResponse,
    AsyncItemsWithStreamingResponse,
)
from ......_types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ......_utils import path_template, maybe_transform
from .turns.turns import (
    Turns,
    AsyncTurns,
    TurnsWithRawResponse,
    AsyncTurnsWithRawResponse,
    TurnsWithStreamingResponse,
    AsyncTurnsWithStreamingResponse,
)
from ......_compat import cached_property
from ......_resource import SyncAPIResource, AsyncAPIResource
from ......_response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ......pagination import SyncCursorPage, AsyncCursorPage
from ......_base_client import AsyncPaginator, make_request_options
from ......types.beta.subagent import Subagent
from ......types.beta.agents.sessions import subagent_list_params

__all__ = ["Subagents", "AsyncSubagents"]


class Subagents(SyncAPIResource):
    @cached_property
    def items(self) -> Items:
        return Items(self._client)

    @cached_property
    def turns(self) -> Turns:
        return Turns(self._client)

    @cached_property
    def with_raw_response(self) -> SubagentsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return SubagentsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SubagentsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return SubagentsWithStreamingResponse(self)

    def retrieve(
        self,
        subagent_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Subagent:
        """Retrieves a subagent belonging to this session.

        See
        [subagent workflows](https://developers.openai.com/api/docs/guides/agents-api/multi-agent).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not subagent_id:
            raise ValueError(f"Expected a non-empty value for `subagent_id` but received {subagent_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get(
            path_template(
                "/agents/sessions/{session_id}/subagents/{subagent_id}", session_id=session_id, subagent_id=subagent_id
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Subagent,
        )

    def list(
        self,
        session_id: str,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPage[Subagent]:
        """Lists subagents in a session, including nested and closed subagents.

        See
        [subagent workflows](https://developers.openai.com/api/docs/guides/agents-api/multi-agent).

        Args:
          after: Return resources after this resource ID in the selected order.

          limit: The maximum number of resources to return, between 1 and 100. Defaults to 20.

          order: The order in which resources are returned. Defaults to `desc`.

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
            path_template("/agents/sessions/{session_id}/subagents", session_id=session_id),
            page=SyncCursorPage[Subagent],
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
                    subagent_list_params.SubagentListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=Subagent,
        )


class AsyncSubagents(AsyncAPIResource):
    @cached_property
    def items(self) -> AsyncItems:
        return AsyncItems(self._client)

    @cached_property
    def turns(self) -> AsyncTurns:
        return AsyncTurns(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncSubagentsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSubagentsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSubagentsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncSubagentsWithStreamingResponse(self)

    async def retrieve(
        self,
        subagent_id: str,
        *,
        session_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Subagent:
        """Retrieves a subagent belonging to this session.

        See
        [subagent workflows](https://developers.openai.com/api/docs/guides/agents-api/multi-agent).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        if not subagent_id:
            raise ValueError(f"Expected a non-empty value for `subagent_id` but received {subagent_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._get(
            path_template(
                "/agents/sessions/{session_id}/subagents/{subagent_id}", session_id=session_id, subagent_id=subagent_id
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Subagent,
        )

    def list(
        self,
        session_id: str,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[Subagent, AsyncCursorPage[Subagent]]:
        """Lists subagents in a session, including nested and closed subagents.

        See
        [subagent workflows](https://developers.openai.com/api/docs/guides/agents-api/multi-agent).

        Args:
          after: Return resources after this resource ID in the selected order.

          limit: The maximum number of resources to return, between 1 and 100. Defaults to 20.

          order: The order in which resources are returned. Defaults to `desc`.

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
            path_template("/agents/sessions/{session_id}/subagents", session_id=session_id),
            page=AsyncCursorPage[Subagent],
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
                    subagent_list_params.SubagentListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=Subagent,
        )


class SubagentsWithRawResponse:
    def __init__(self, subagents: Subagents) -> None:
        self._subagents = subagents

        self.retrieve = _legacy_response.to_raw_response_wrapper(
            subagents.retrieve,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            subagents.list,
        )

    @cached_property
    def items(self) -> ItemsWithRawResponse:
        return ItemsWithRawResponse(self._subagents.items)

    @cached_property
    def turns(self) -> TurnsWithRawResponse:
        return TurnsWithRawResponse(self._subagents.turns)


class AsyncSubagentsWithRawResponse:
    def __init__(self, subagents: AsyncSubagents) -> None:
        self._subagents = subagents

        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            subagents.retrieve,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            subagents.list,
        )

    @cached_property
    def items(self) -> AsyncItemsWithRawResponse:
        return AsyncItemsWithRawResponse(self._subagents.items)

    @cached_property
    def turns(self) -> AsyncTurnsWithRawResponse:
        return AsyncTurnsWithRawResponse(self._subagents.turns)


class SubagentsWithStreamingResponse:
    def __init__(self, subagents: Subagents) -> None:
        self._subagents = subagents

        self.retrieve = to_streamed_response_wrapper(
            subagents.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            subagents.list,
        )

    @cached_property
    def items(self) -> ItemsWithStreamingResponse:
        return ItemsWithStreamingResponse(self._subagents.items)

    @cached_property
    def turns(self) -> TurnsWithStreamingResponse:
        return TurnsWithStreamingResponse(self._subagents.turns)


class AsyncSubagentsWithStreamingResponse:
    def __init__(self, subagents: AsyncSubagents) -> None:
        self._subagents = subagents

        self.retrieve = async_to_streamed_response_wrapper(
            subagents.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            subagents.list,
        )

    @cached_property
    def items(self) -> AsyncItemsWithStreamingResponse:
        return AsyncItemsWithStreamingResponse(self._subagents.items)

    @cached_property
    def turns(self) -> AsyncTurnsWithStreamingResponse:
        return AsyncTurnsWithStreamingResponse(self._subagents.turns)
