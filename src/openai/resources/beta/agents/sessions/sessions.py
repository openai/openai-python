# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Mapping, Iterable, Optional
from typing_extensions import Literal, overload

import httpx2

from ..... import _legacy_response
from .items import (
    Items,
    AsyncItems,
    ItemsWithRawResponse,
    AsyncItemsWithRawResponse,
    ItemsWithStreamingResponse,
    AsyncItemsWithStreamingResponse,
)
from .turns import (
    Turns,
    AsyncTurns,
    TurnsWithRawResponse,
    AsyncTurnsWithRawResponse,
    TurnsWithStreamingResponse,
    AsyncTurnsWithStreamingResponse,
)
from .events import (
    Events,
    AsyncEvents,
    EventsWithRawResponse,
    AsyncEventsWithRawResponse,
    EventsWithStreamingResponse,
    AsyncEventsWithStreamingResponse,
)
from .artifacts import (
    Artifacts,
    AsyncArtifacts,
    ArtifactsWithRawResponse,
    AsyncArtifactsWithRawResponse,
    ArtifactsWithStreamingResponse,
    AsyncArtifactsWithStreamingResponse,
)
from ....._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from ....._utils import path_template, required_args, maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ....._streaming import Stream, AsyncStream
from .....pagination import SyncCursorPage, AsyncCursorPage
from ....._base_client import AsyncPaginator, make_request_options
from .subagents.subagents import (
    Subagents,
    AsyncSubagents,
    SubagentsWithRawResponse,
    AsyncSubagentsWithRawResponse,
    SubagentsWithStreamingResponse,
    AsyncSubagentsWithStreamingResponse,
)
from .....types.beta.agents import session_list_params, session_create_params, session_update_params
from .....lib.streaming.agents import ToolHandler, AsyncToolHandler, AgentSessionStream, AsyncAgentSessionStream
from .....types.beta.agent_session import AgentSession
from .....types.beta.environment_param import EnvironmentParam
from .....types.beta.agent_session_event import AgentSessionEvent
from .....types.beta.agent_session_deleted import AgentSessionDeleted
from .....types.beta.agent_session_input_message_param import AgentSessionInputMessageParam

__all__ = ["Sessions", "AsyncSessions"]


class Sessions(SyncAPIResource):
    def stream(
        self,
        session_id: str,
        *,
        input: str | Iterable[AgentSessionInputMessageParam],
        tool_handlers: Mapping[str, ToolHandler] | None = None,
        idempotency_key: str | Omit = omit,
        extra_headers: Headers | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AgentSessionStream:
        """Stream one turn of an idle session, subscribing before submitting input.

        Use as a context manager. Only one caller may submit input to the session
        while this helper runs. Optional tool handlers receive an arguments dict;
        their results are submitted automatically. See AgentSessionStream for details.
        """
        return AgentSessionStream(
            self,
            session_id,
            input=input,
            tool_handlers=tool_handlers,
            idempotency_key=idempotency_key,
            extra_headers=extra_headers,
            timeout=timeout,
        )

    @cached_property
    def subagents(self) -> Subagents:
        return Subagents(self._client)

    @cached_property
    def artifacts(self) -> Artifacts:
        return Artifacts(self._client)

    @cached_property
    def items(self) -> Items:
        return Items(self._client)

    @cached_property
    def events(self) -> Events:
        return Events(self._client)

    @cached_property
    def turns(self) -> Turns:
        return Turns(self._client)

    @cached_property
    def with_raw_response(self) -> SessionsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return SessionsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SessionsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return SessionsWithStreamingResponse(self)

    @overload
    def create(
        self,
        *,
        environment: EnvironmentParam,
        agent: session_create_params.Agent | Omit = omit,
        agent_id: str | Omit = omit,
        input: Union[str, Iterable[AgentSessionInputMessageParam], None] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        stream: Literal[False] | Omit = omit,
        vault_ids: Optional[SequenceNotStr[str]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AgentSession:
        """
        Creates a managed agent session, optionally submits initial input, and returns
        the session or streams its events when stream is true. See
        [running sessions](https://developers.openai.com/api/docs/guides/agents-api/sessions).

        Args:
          environment: An inline execution environment or a reference to an environment template.

          agent: Agent configuration. With `agent_id`, supplied fields override the saved agent
              for this session. Without `agent_id`, `model` is required.

          agent_id: The ID of a saved reusable agent. Omit `agent` to use its configuration
              unchanged.

          input: Initial input submitted when creating a session.

          metadata: Up to 16 string key-value pairs, with keys up to 64 and values up to 512
              characters. Omission or null defaults to an empty map.

          stream: Whether to stream session events as server-sent events. Defaults to `false`.

          vault_ids: The IDs of vaults made available to the session.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        *,
        environment: EnvironmentParam,
        stream: Literal[True],
        agent: session_create_params.Agent | Omit = omit,
        agent_id: str | Omit = omit,
        input: Union[str, Iterable[AgentSessionInputMessageParam], None] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        vault_ids: Optional[SequenceNotStr[str]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Stream[AgentSessionEvent]:
        """
        Creates a managed agent session, optionally submits initial input, and returns
        the session or streams its events when stream is true. See
        [running sessions](https://developers.openai.com/api/docs/guides/agents-api/sessions).

        Args:
          environment: An inline execution environment or a reference to an environment template.

          stream: Whether to stream session events as server-sent events. Defaults to `false`.

          agent: Agent configuration. With `agent_id`, supplied fields override the saved agent
              for this session. Without `agent_id`, `model` is required.

          agent_id: The ID of a saved reusable agent. Omit `agent` to use its configuration
              unchanged.

          input: Initial input submitted when creating a session.

          metadata: Up to 16 string key-value pairs, with keys up to 64 and values up to 512
              characters. Omission or null defaults to an empty map.

          vault_ids: The IDs of vaults made available to the session.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        *,
        environment: EnvironmentParam,
        stream: bool,
        agent: session_create_params.Agent | Omit = omit,
        agent_id: str | Omit = omit,
        input: Union[str, Iterable[AgentSessionInputMessageParam], None] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        vault_ids: Optional[SequenceNotStr[str]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AgentSession | Stream[AgentSessionEvent]:
        """
        Creates a managed agent session, optionally submits initial input, and returns
        the session or streams its events when stream is true. See
        [running sessions](https://developers.openai.com/api/docs/guides/agents-api/sessions).

        Args:
          environment: An inline execution environment or a reference to an environment template.

          stream: Whether to stream session events as server-sent events. Defaults to `false`.

          agent: Agent configuration. With `agent_id`, supplied fields override the saved agent
              for this session. Without `agent_id`, `model` is required.

          agent_id: The ID of a saved reusable agent. Omit `agent` to use its configuration
              unchanged.

          input: Initial input submitted when creating a session.

          metadata: Up to 16 string key-value pairs, with keys up to 64 and values up to 512
              characters. Omission or null defaults to an empty map.

          vault_ids: The IDs of vaults made available to the session.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["environment"], ["environment", "stream"])
    def create(
        self,
        *,
        environment: EnvironmentParam,
        agent: session_create_params.Agent | Omit = omit,
        agent_id: str | Omit = omit,
        input: Union[str, Iterable[AgentSessionInputMessageParam], None] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        stream: Literal[False] | Literal[True] | Omit = omit,
        vault_ids: Optional[SequenceNotStr[str]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AgentSession | Stream[AgentSessionEvent]:
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._post(
            "/agents/sessions",
            body=maybe_transform(
                {
                    "environment": environment,
                    "agent": agent,
                    "agent_id": agent_id,
                    "input": input,
                    "metadata": metadata,
                    "stream": stream,
                    "vault_ids": vault_ids,
                },
                session_create_params.SessionCreateParamsStreaming
                if stream
                else session_create_params.SessionCreateParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=AgentSession,
            stream=stream or False,
            stream_cls=Stream[AgentSessionEvent],
        )

    def retrieve(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AgentSession:
        """Retrieves the current state of a managed agent session.

        See
        [managing sessions](https://developers.openai.com/api/docs/guides/agents-api/sessions/manage).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get(
            path_template("/agents/sessions/{session_id}", session_id=session_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=AgentSession,
        )

    def update(
        self,
        session_id: str,
        *,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AgentSession:
        """Updates session metadata.

        Omitted fields are unchanged. See
        [managing sessions](https://developers.openai.com/api/docs/guides/agents-api/sessions/manage).

        Args:
          metadata: Replaces all metadata. Omit to leave unchanged, or pass null or {} to clear it.
              Up to 16 string key-value pairs, with keys up to 64 and values up to 512
              characters.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._post(
            path_template("/agents/sessions/{session_id}", session_id=session_id),
            body=maybe_transform({"metadata": metadata}, session_update_params.SessionUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=AgentSession,
        )

    def list(
        self,
        *,
        after: str | Omit = omit,
        agent_id: str | Omit = omit,
        limit: Optional[int] | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPage[AgentSession]:
        """
        Lists managed agent sessions using ID-based pagination and the requested sort
        order. See
        [managing sessions](https://developers.openai.com/api/docs/guides/agents-api/sessions/manage).

        Args:
          after: Return resources after this resource ID in the selected order.

          agent_id: Only return sessions whose root agent has this ID. Omit to return sessions for
              all agents.

          limit: The maximum number of resources to return.

          order: Sort order by the `created_at` timestamp. Use `asc` for ascending order or
              `desc` for descending order. Defaults to `desc`.

              - `asc` - Returns resources in ascending order.
              - `desc` - Returns resources in descending order.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get_api_list(
            "/agents/sessions",
            page=SyncCursorPage[AgentSession],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "agent_id": agent_id,
                        "limit": limit,
                        "order": order,
                    },
                    session_list_params.SessionListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=AgentSession,
        )

    def delete(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AgentSessionDeleted:
        """
        Removes a managed agent session from the public API and returns a deletion
        confirmation. Physical cleanup may continue asynchronously. See
        [managing sessions](https://developers.openai.com/api/docs/guides/agents-api/sessions/manage).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._delete(
            path_template("/agents/sessions/{session_id}", session_id=session_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=AgentSessionDeleted,
        )


class AsyncSessions(AsyncAPIResource):
    def stream(
        self,
        session_id: str,
        *,
        input: str | Iterable[AgentSessionInputMessageParam],
        tool_handlers: Mapping[str, AsyncToolHandler] | None = None,
        idempotency_key: str | Omit = omit,
        extra_headers: Headers | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AsyncAgentSessionStream:
        """Stream one turn of an idle session, subscribing before submitting input.

        Use as an async context manager. Only one caller may submit input to the session
        while this helper runs. Optional tool handlers receive an arguments dict;
        their results are submitted automatically. See AsyncAgentSessionStream for details.
        """
        return AsyncAgentSessionStream(
            self,
            session_id,
            input=input,
            tool_handlers=tool_handlers,
            idempotency_key=idempotency_key,
            extra_headers=extra_headers,
            timeout=timeout,
        )

    @cached_property
    def subagents(self) -> AsyncSubagents:
        return AsyncSubagents(self._client)

    @cached_property
    def artifacts(self) -> AsyncArtifacts:
        return AsyncArtifacts(self._client)

    @cached_property
    def items(self) -> AsyncItems:
        return AsyncItems(self._client)

    @cached_property
    def events(self) -> AsyncEvents:
        return AsyncEvents(self._client)

    @cached_property
    def turns(self) -> AsyncTurns:
        return AsyncTurns(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncSessionsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSessionsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSessionsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncSessionsWithStreamingResponse(self)

    @overload
    async def create(
        self,
        *,
        environment: EnvironmentParam,
        agent: session_create_params.Agent | Omit = omit,
        agent_id: str | Omit = omit,
        input: Union[str, Iterable[AgentSessionInputMessageParam], None] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        stream: Literal[False] | Omit = omit,
        vault_ids: Optional[SequenceNotStr[str]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AgentSession:
        """
        Creates a managed agent session, optionally submits initial input, and returns
        the session or streams its events when stream is true. See
        [running sessions](https://developers.openai.com/api/docs/guides/agents-api/sessions).

        Args:
          environment: An inline execution environment or a reference to an environment template.

          agent: Agent configuration. With `agent_id`, supplied fields override the saved agent
              for this session. Without `agent_id`, `model` is required.

          agent_id: The ID of a saved reusable agent. Omit `agent` to use its configuration
              unchanged.

          input: Initial input submitted when creating a session.

          metadata: Up to 16 string key-value pairs, with keys up to 64 and values up to 512
              characters. Omission or null defaults to an empty map.

          stream: Whether to stream session events as server-sent events. Defaults to `false`.

          vault_ids: The IDs of vaults made available to the session.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        *,
        environment: EnvironmentParam,
        stream: Literal[True],
        agent: session_create_params.Agent | Omit = omit,
        agent_id: str | Omit = omit,
        input: Union[str, Iterable[AgentSessionInputMessageParam], None] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        vault_ids: Optional[SequenceNotStr[str]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AsyncStream[AgentSessionEvent]:
        """
        Creates a managed agent session, optionally submits initial input, and returns
        the session or streams its events when stream is true. See
        [running sessions](https://developers.openai.com/api/docs/guides/agents-api/sessions).

        Args:
          environment: An inline execution environment or a reference to an environment template.

          stream: Whether to stream session events as server-sent events. Defaults to `false`.

          agent: Agent configuration. With `agent_id`, supplied fields override the saved agent
              for this session. Without `agent_id`, `model` is required.

          agent_id: The ID of a saved reusable agent. Omit `agent` to use its configuration
              unchanged.

          input: Initial input submitted when creating a session.

          metadata: Up to 16 string key-value pairs, with keys up to 64 and values up to 512
              characters. Omission or null defaults to an empty map.

          vault_ids: The IDs of vaults made available to the session.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        *,
        environment: EnvironmentParam,
        stream: bool,
        agent: session_create_params.Agent | Omit = omit,
        agent_id: str | Omit = omit,
        input: Union[str, Iterable[AgentSessionInputMessageParam], None] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        vault_ids: Optional[SequenceNotStr[str]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AgentSession | AsyncStream[AgentSessionEvent]:
        """
        Creates a managed agent session, optionally submits initial input, and returns
        the session or streams its events when stream is true. See
        [running sessions](https://developers.openai.com/api/docs/guides/agents-api/sessions).

        Args:
          environment: An inline execution environment or a reference to an environment template.

          stream: Whether to stream session events as server-sent events. Defaults to `false`.

          agent: Agent configuration. With `agent_id`, supplied fields override the saved agent
              for this session. Without `agent_id`, `model` is required.

          agent_id: The ID of a saved reusable agent. Omit `agent` to use its configuration
              unchanged.

          input: Initial input submitted when creating a session.

          metadata: Up to 16 string key-value pairs, with keys up to 64 and values up to 512
              characters. Omission or null defaults to an empty map.

          vault_ids: The IDs of vaults made available to the session.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["environment"], ["environment", "stream"])
    async def create(
        self,
        *,
        environment: EnvironmentParam,
        agent: session_create_params.Agent | Omit = omit,
        agent_id: str | Omit = omit,
        input: Union[str, Iterable[AgentSessionInputMessageParam], None] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        stream: Literal[False] | Literal[True] | Omit = omit,
        vault_ids: Optional[SequenceNotStr[str]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AgentSession | AsyncStream[AgentSessionEvent]:
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._post(
            "/agents/sessions",
            body=await async_maybe_transform(
                {
                    "environment": environment,
                    "agent": agent,
                    "agent_id": agent_id,
                    "input": input,
                    "metadata": metadata,
                    "stream": stream,
                    "vault_ids": vault_ids,
                },
                session_create_params.SessionCreateParamsStreaming
                if stream
                else session_create_params.SessionCreateParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=AgentSession,
            stream=stream or False,
            stream_cls=AsyncStream[AgentSessionEvent],
        )

    async def retrieve(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AgentSession:
        """Retrieves the current state of a managed agent session.

        See
        [managing sessions](https://developers.openai.com/api/docs/guides/agents-api/sessions/manage).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._get(
            path_template("/agents/sessions/{session_id}", session_id=session_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=AgentSession,
        )

    async def update(
        self,
        session_id: str,
        *,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AgentSession:
        """Updates session metadata.

        Omitted fields are unchanged. See
        [managing sessions](https://developers.openai.com/api/docs/guides/agents-api/sessions/manage).

        Args:
          metadata: Replaces all metadata. Omit to leave unchanged, or pass null or {} to clear it.
              Up to 16 string key-value pairs, with keys up to 64 and values up to 512
              characters.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._post(
            path_template("/agents/sessions/{session_id}", session_id=session_id),
            body=await async_maybe_transform({"metadata": metadata}, session_update_params.SessionUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=AgentSession,
        )

    def list(
        self,
        *,
        after: str | Omit = omit,
        agent_id: str | Omit = omit,
        limit: Optional[int] | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[AgentSession, AsyncCursorPage[AgentSession]]:
        """
        Lists managed agent sessions using ID-based pagination and the requested sort
        order. See
        [managing sessions](https://developers.openai.com/api/docs/guides/agents-api/sessions/manage).

        Args:
          after: Return resources after this resource ID in the selected order.

          agent_id: Only return sessions whose root agent has this ID. Omit to return sessions for
              all agents.

          limit: The maximum number of resources to return.

          order: Sort order by the `created_at` timestamp. Use `asc` for ascending order or
              `desc` for descending order. Defaults to `desc`.

              - `asc` - Returns resources in ascending order.
              - `desc` - Returns resources in descending order.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get_api_list(
            "/agents/sessions",
            page=AsyncCursorPage[AgentSession],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "agent_id": agent_id,
                        "limit": limit,
                        "order": order,
                    },
                    session_list_params.SessionListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=AgentSession,
        )

    async def delete(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AgentSessionDeleted:
        """
        Removes a managed agent session from the public API and returns a deletion
        confirmation. Physical cleanup may continue asynchronously. See
        [managing sessions](https://developers.openai.com/api/docs/guides/agents-api/sessions/manage).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._delete(
            path_template("/agents/sessions/{session_id}", session_id=session_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=AgentSessionDeleted,
        )


class SessionsWithRawResponse:
    def __init__(self, sessions: Sessions) -> None:
        self._sessions = sessions

        self.create = _legacy_response.to_raw_response_wrapper(
            sessions.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            sessions.retrieve,
        )
        self.update = _legacy_response.to_raw_response_wrapper(
            sessions.update,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            sessions.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            sessions.delete,
        )

    @cached_property
    def subagents(self) -> SubagentsWithRawResponse:
        return SubagentsWithRawResponse(self._sessions.subagents)

    @cached_property
    def artifacts(self) -> ArtifactsWithRawResponse:
        return ArtifactsWithRawResponse(self._sessions.artifacts)

    @cached_property
    def items(self) -> ItemsWithRawResponse:
        return ItemsWithRawResponse(self._sessions.items)

    @cached_property
    def events(self) -> EventsWithRawResponse:
        return EventsWithRawResponse(self._sessions.events)

    @cached_property
    def turns(self) -> TurnsWithRawResponse:
        return TurnsWithRawResponse(self._sessions.turns)


class AsyncSessionsWithRawResponse:
    def __init__(self, sessions: AsyncSessions) -> None:
        self._sessions = sessions

        self.create = _legacy_response.async_to_raw_response_wrapper(
            sessions.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            sessions.retrieve,
        )
        self.update = _legacy_response.async_to_raw_response_wrapper(
            sessions.update,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            sessions.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            sessions.delete,
        )

    @cached_property
    def subagents(self) -> AsyncSubagentsWithRawResponse:
        return AsyncSubagentsWithRawResponse(self._sessions.subagents)

    @cached_property
    def artifacts(self) -> AsyncArtifactsWithRawResponse:
        return AsyncArtifactsWithRawResponse(self._sessions.artifacts)

    @cached_property
    def items(self) -> AsyncItemsWithRawResponse:
        return AsyncItemsWithRawResponse(self._sessions.items)

    @cached_property
    def events(self) -> AsyncEventsWithRawResponse:
        return AsyncEventsWithRawResponse(self._sessions.events)

    @cached_property
    def turns(self) -> AsyncTurnsWithRawResponse:
        return AsyncTurnsWithRawResponse(self._sessions.turns)


class SessionsWithStreamingResponse:
    def __init__(self, sessions: Sessions) -> None:
        self._sessions = sessions

        self.create = to_streamed_response_wrapper(
            sessions.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            sessions.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            sessions.update,
        )
        self.list = to_streamed_response_wrapper(
            sessions.list,
        )
        self.delete = to_streamed_response_wrapper(
            sessions.delete,
        )

    @cached_property
    def subagents(self) -> SubagentsWithStreamingResponse:
        return SubagentsWithStreamingResponse(self._sessions.subagents)

    @cached_property
    def artifacts(self) -> ArtifactsWithStreamingResponse:
        return ArtifactsWithStreamingResponse(self._sessions.artifacts)

    @cached_property
    def items(self) -> ItemsWithStreamingResponse:
        return ItemsWithStreamingResponse(self._sessions.items)

    @cached_property
    def events(self) -> EventsWithStreamingResponse:
        return EventsWithStreamingResponse(self._sessions.events)

    @cached_property
    def turns(self) -> TurnsWithStreamingResponse:
        return TurnsWithStreamingResponse(self._sessions.turns)


class AsyncSessionsWithStreamingResponse:
    def __init__(self, sessions: AsyncSessions) -> None:
        self._sessions = sessions

        self.create = async_to_streamed_response_wrapper(
            sessions.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            sessions.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            sessions.update,
        )
        self.list = async_to_streamed_response_wrapper(
            sessions.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            sessions.delete,
        )

    @cached_property
    def subagents(self) -> AsyncSubagentsWithStreamingResponse:
        return AsyncSubagentsWithStreamingResponse(self._sessions.subagents)

    @cached_property
    def artifacts(self) -> AsyncArtifactsWithStreamingResponse:
        return AsyncArtifactsWithStreamingResponse(self._sessions.artifacts)

    @cached_property
    def items(self) -> AsyncItemsWithStreamingResponse:
        return AsyncItemsWithStreamingResponse(self._sessions.items)

    @cached_property
    def events(self) -> AsyncEventsWithStreamingResponse:
        return AsyncEventsWithStreamingResponse(self._sessions.events)

    @cached_property
    def turns(self) -> AsyncTurnsWithStreamingResponse:
        return AsyncTurnsWithStreamingResponse(self._sessions.turns)
