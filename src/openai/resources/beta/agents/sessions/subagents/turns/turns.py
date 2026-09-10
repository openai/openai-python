# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx2

from .items import (
    Items,
    AsyncItems,
    ItemsWithRawResponse,
    AsyncItemsWithRawResponse,
    ItemsWithStreamingResponse,
    AsyncItemsWithStreamingResponse,
)
from ....... import _legacy_response
from ......._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ......._utils import path_template, maybe_transform
from ......._compat import cached_property
from ......._resource import SyncAPIResource, AsyncAPIResource
from ......._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from .......pagination import SyncCursorPage, AsyncCursorPage
from ......._base_client import AsyncPaginator, make_request_options
from .......types.beta.agents.sessions.turn import Turn
from .......types.beta.agents.sessions.subagents import turn_list_params

__all__ = ["Turns", "AsyncTurns"]


class Turns(SyncAPIResource):
    @cached_property
    def items(self) -> Items:
        return Items(self._client)

    @cached_property
    def with_raw_response(self) -> TurnsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return TurnsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TurnsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return TurnsWithStreamingResponse(self)

    def retrieve(
        self,
        turn_id: str,
        *,
        session_id: str,
        subagent_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Turn:
        """Retrieves a turn belonging to this subagent.

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
        if not turn_id:
            raise ValueError(f"Expected a non-empty value for `turn_id` but received {turn_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get(
            path_template(
                "/agents/sessions/{session_id}/subagents/{subagent_id}/turns/{turn_id}",
                session_id=session_id,
                subagent_id=subagent_id,
                turn_id=turn_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Turn,
        )

    def list(
        self,
        subagent_id: str,
        *,
        session_id: str,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPage[Turn]:
        """Lists all turns of this subagent, including turns after a resume.

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
        if not subagent_id:
            raise ValueError(f"Expected a non-empty value for `subagent_id` but received {subagent_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get_api_list(
            path_template(
                "/agents/sessions/{session_id}/subagents/{subagent_id}/turns",
                session_id=session_id,
                subagent_id=subagent_id,
            ),
            page=SyncCursorPage[Turn],
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
                    turn_list_params.TurnListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=Turn,
        )


class AsyncTurns(AsyncAPIResource):
    @cached_property
    def items(self) -> AsyncItems:
        return AsyncItems(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncTurnsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTurnsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTurnsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncTurnsWithStreamingResponse(self)

    async def retrieve(
        self,
        turn_id: str,
        *,
        session_id: str,
        subagent_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Turn:
        """Retrieves a turn belonging to this subagent.

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
        if not turn_id:
            raise ValueError(f"Expected a non-empty value for `turn_id` but received {turn_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._get(
            path_template(
                "/agents/sessions/{session_id}/subagents/{subagent_id}/turns/{turn_id}",
                session_id=session_id,
                subagent_id=subagent_id,
                turn_id=turn_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Turn,
        )

    def list(
        self,
        subagent_id: str,
        *,
        session_id: str,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[Turn, AsyncCursorPage[Turn]]:
        """Lists all turns of this subagent, including turns after a resume.

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
        if not subagent_id:
            raise ValueError(f"Expected a non-empty value for `subagent_id` but received {subagent_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get_api_list(
            path_template(
                "/agents/sessions/{session_id}/subagents/{subagent_id}/turns",
                session_id=session_id,
                subagent_id=subagent_id,
            ),
            page=AsyncCursorPage[Turn],
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
                    turn_list_params.TurnListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=Turn,
        )


class TurnsWithRawResponse:
    def __init__(self, turns: Turns) -> None:
        self._turns = turns

        self.retrieve = _legacy_response.to_raw_response_wrapper(
            turns.retrieve,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            turns.list,
        )

    @cached_property
    def items(self) -> ItemsWithRawResponse:
        return ItemsWithRawResponse(self._turns.items)


class AsyncTurnsWithRawResponse:
    def __init__(self, turns: AsyncTurns) -> None:
        self._turns = turns

        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            turns.retrieve,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            turns.list,
        )

    @cached_property
    def items(self) -> AsyncItemsWithRawResponse:
        return AsyncItemsWithRawResponse(self._turns.items)


class TurnsWithStreamingResponse:
    def __init__(self, turns: Turns) -> None:
        self._turns = turns

        self.retrieve = to_streamed_response_wrapper(
            turns.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            turns.list,
        )

    @cached_property
    def items(self) -> ItemsWithStreamingResponse:
        return ItemsWithStreamingResponse(self._turns.items)


class AsyncTurnsWithStreamingResponse:
    def __init__(self, turns: AsyncTurns) -> None:
        self._turns = turns

        self.retrieve = async_to_streamed_response_wrapper(
            turns.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            turns.list,
        )

    @cached_property
    def items(self) -> AsyncItemsWithStreamingResponse:
        return AsyncItemsWithStreamingResponse(self._turns.items)
