# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable, Optional
from typing_extensions import Literal

import httpx2

from .... import _legacy_response
from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ...._utils import path_template, maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ....pagination import SyncCursorPage, AsyncCursorPage
from ....types.beta import agent_list_params, agent_create_params, agent_update_params
from .vaults.vaults import (
    Vaults,
    AsyncVaults,
    VaultsWithRawResponse,
    AsyncVaultsWithRawResponse,
    VaultsWithStreamingResponse,
    AsyncVaultsWithStreamingResponse,
)
from ...._base_client import AsyncPaginator, make_request_options
from .sessions.sessions import (
    Sessions,
    AsyncSessions,
    SessionsWithRawResponse,
    AsyncSessionsWithRawResponse,
    SessionsWithStreamingResponse,
    AsyncSessionsWithStreamingResponse,
)
from ....types.beta.agent import Agent
from .environments.environments import (
    Environments,
    AsyncEnvironments,
    EnvironmentsWithRawResponse,
    AsyncEnvironmentsWithRawResponse,
    EnvironmentsWithStreamingResponse,
    AsyncEnvironmentsWithStreamingResponse,
)
from ....types.beta.agent_deleted import AgentDeleted
from ....types.beta.agent_text_param import AgentTextParam
from ....types.beta.agent_reasoning_param import AgentReasoningParam
from ....types.beta.multi_agent_config_param import MultiAgentConfigParam
from ....types.beta.persisted_agent_tool_param import PersistedAgentToolParam

__all__ = ["Agents", "AsyncAgents"]


class Agents(SyncAPIResource):
    @cached_property
    def environments(self) -> Environments:
        return Environments(self._client)

    @cached_property
    def vaults(self) -> Vaults:
        return Vaults(self._client)

    @cached_property
    def sessions(self) -> Sessions:
        return Sessions(self._client)

    @cached_property
    def with_raw_response(self) -> AgentsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AgentsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AgentsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AgentsWithStreamingResponse(self)

    def create(
        self,
        *,
        model: str,
        instructions: Optional[str] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        multi_agent: Optional[MultiAgentConfigParam] | Omit = omit,
        name: Optional[str] | Omit = omit,
        reasoning: Optional[AgentReasoningParam] | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "priority", "fast"]] | Omit = omit,
        text: Optional[AgentTextParam] | Omit = omit,
        tools: Optional[Iterable[PersistedAgentToolParam]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Agent:
        """Creates a reusable agent without storing credentials.

        See
        [agent configuration](https://developers.openai.com/api/docs/guides/agents-api/configuration).

        Args:
          model: The model to use for the agent. The requested model name is preserved.

          instructions: Additional instructions appended to the agent's default base instructions. Omit
              or set to null to add no custom instructions.

          metadata: Up to 16 string key-value pairs, with keys up to 64 and values up to 512
              characters. Omission or null defaults to an empty map.

          multi_agent: Explicit configuration for creating and coordinating subagents.

          name: A human-readable name for the agent. Omission or null leaves the agent unnamed.

          reasoning: Reasoning configuration for the agent.

          service_tier: The service tier used for model requests.

              - `auto` - Selects the service tier automatically.
              - `default` - Uses the default service tier.
              - `flex` - Uses the flex service tier.
              - `priority` - Uses the priority service tier.
              - `fast` - Uses the fast service tier.

          text: Configuration for text generated by the agent.

          tools: Tools available to the agent. Defaults to an empty list.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._post(
            "/agents",
            body=maybe_transform(
                {
                    "model": model,
                    "instructions": instructions,
                    "metadata": metadata,
                    "multi_agent": multi_agent,
                    "name": name,
                    "reasoning": reasoning,
                    "service_tier": service_tier,
                    "text": text,
                    "tools": tools,
                },
                agent_create_params.AgentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Agent,
        )

    def retrieve(
        self,
        agent_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Agent:
        """Retrieves a reusable agent by ID.

        See
        [agent configuration](https://developers.openai.com/api/docs/guides/agents-api/configuration).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not agent_id:
            raise ValueError(f"Expected a non-empty value for `agent_id` but received {agent_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get(
            path_template("/agents/{agent_id}", agent_id=agent_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Agent,
        )

    def update(
        self,
        agent_id: str,
        *,
        instructions: Optional[str] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        model: str | Omit = omit,
        multi_agent: Optional[MultiAgentConfigParam] | Omit = omit,
        name: Optional[str] | Omit = omit,
        reasoning: Optional[AgentReasoningParam] | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "priority", "fast"]] | Omit = omit,
        text: Optional[AgentTextParam] | Omit = omit,
        tools: Optional[Iterable[PersistedAgentToolParam]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Agent:
        """Updates a reusable agent.

        See
        [agent configuration](https://developers.openai.com/api/docs/guides/agents-api/configuration).

        Args:
          instructions: Additional instructions appended to the agent's default base instructions. Omit
              to leave unchanged.

          metadata: Replaces all metadata. Omit to leave unchanged, or pass null or {} to clear it.
              Up to 16 string key-value pairs, with keys up to 64 and values up to 512
              characters.

          model: The model to use for the agent. The requested model name is preserved.

          multi_agent: Explicit configuration for creating and coordinating subagents.

          name: A replacement name. Omit to leave unchanged, or pass null to clear it.

          reasoning: Reasoning configuration for the agent.

          service_tier: The service tier used for model requests.

              - `auto` - Selects the service tier automatically.
              - `default` - Uses the default service tier.
              - `flex` - Uses the flex service tier.
              - `priority` - Uses the priority service tier.
              - `fast` - Uses the fast service tier.

          text: Configuration for text generated by the agent.

          tools: Tools available to the agent.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not agent_id:
            raise ValueError(f"Expected a non-empty value for `agent_id` but received {agent_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._post(
            path_template("/agents/{agent_id}", agent_id=agent_id),
            body=maybe_transform(
                {
                    "instructions": instructions,
                    "metadata": metadata,
                    "model": model,
                    "multi_agent": multi_agent,
                    "name": name,
                    "reasoning": reasoning,
                    "service_tier": service_tier,
                    "text": text,
                    "tools": tools,
                },
                agent_update_params.AgentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Agent,
        )

    def list(
        self,
        *,
        after: str | Omit = omit,
        limit: Optional[int] | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPage[Agent]:
        """Lists reusable agents in the current project.

        See
        [agent configuration](https://developers.openai.com/api/docs/guides/agents-api/configuration).

        Args:
          after: Return resources after this resource ID in the selected order.

          limit: The maximum number of resources to return.

          order: The order in which resources are returned. Defaults to `desc`.

              - `asc` - Returns resources in ascending order.
              - `desc` - Returns resources in descending order.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get_api_list(
            "/agents",
            page=SyncCursorPage[Agent],
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
                    agent_list_params.AgentListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=Agent,
        )

    def delete(
        self,
        agent_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AgentDeleted:
        """Deletes a reusable agent.

        See
        [agent configuration](https://developers.openai.com/api/docs/guides/agents-api/configuration).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not agent_id:
            raise ValueError(f"Expected a non-empty value for `agent_id` but received {agent_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._delete(
            path_template("/agents/{agent_id}", agent_id=agent_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=AgentDeleted,
        )


class AsyncAgents(AsyncAPIResource):
    @cached_property
    def environments(self) -> AsyncEnvironments:
        return AsyncEnvironments(self._client)

    @cached_property
    def vaults(self) -> AsyncVaults:
        return AsyncVaults(self._client)

    @cached_property
    def sessions(self) -> AsyncSessions:
        return AsyncSessions(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncAgentsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAgentsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAgentsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncAgentsWithStreamingResponse(self)

    async def create(
        self,
        *,
        model: str,
        instructions: Optional[str] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        multi_agent: Optional[MultiAgentConfigParam] | Omit = omit,
        name: Optional[str] | Omit = omit,
        reasoning: Optional[AgentReasoningParam] | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "priority", "fast"]] | Omit = omit,
        text: Optional[AgentTextParam] | Omit = omit,
        tools: Optional[Iterable[PersistedAgentToolParam]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Agent:
        """Creates a reusable agent without storing credentials.

        See
        [agent configuration](https://developers.openai.com/api/docs/guides/agents-api/configuration).

        Args:
          model: The model to use for the agent. The requested model name is preserved.

          instructions: Additional instructions appended to the agent's default base instructions. Omit
              or set to null to add no custom instructions.

          metadata: Up to 16 string key-value pairs, with keys up to 64 and values up to 512
              characters. Omission or null defaults to an empty map.

          multi_agent: Explicit configuration for creating and coordinating subagents.

          name: A human-readable name for the agent. Omission or null leaves the agent unnamed.

          reasoning: Reasoning configuration for the agent.

          service_tier: The service tier used for model requests.

              - `auto` - Selects the service tier automatically.
              - `default` - Uses the default service tier.
              - `flex` - Uses the flex service tier.
              - `priority` - Uses the priority service tier.
              - `fast` - Uses the fast service tier.

          text: Configuration for text generated by the agent.

          tools: Tools available to the agent. Defaults to an empty list.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._post(
            "/agents",
            body=await async_maybe_transform(
                {
                    "model": model,
                    "instructions": instructions,
                    "metadata": metadata,
                    "multi_agent": multi_agent,
                    "name": name,
                    "reasoning": reasoning,
                    "service_tier": service_tier,
                    "text": text,
                    "tools": tools,
                },
                agent_create_params.AgentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Agent,
        )

    async def retrieve(
        self,
        agent_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Agent:
        """Retrieves a reusable agent by ID.

        See
        [agent configuration](https://developers.openai.com/api/docs/guides/agents-api/configuration).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not agent_id:
            raise ValueError(f"Expected a non-empty value for `agent_id` but received {agent_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._get(
            path_template("/agents/{agent_id}", agent_id=agent_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Agent,
        )

    async def update(
        self,
        agent_id: str,
        *,
        instructions: Optional[str] | Omit = omit,
        metadata: Optional[Dict[str, str]] | Omit = omit,
        model: str | Omit = omit,
        multi_agent: Optional[MultiAgentConfigParam] | Omit = omit,
        name: Optional[str] | Omit = omit,
        reasoning: Optional[AgentReasoningParam] | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "priority", "fast"]] | Omit = omit,
        text: Optional[AgentTextParam] | Omit = omit,
        tools: Optional[Iterable[PersistedAgentToolParam]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Agent:
        """Updates a reusable agent.

        See
        [agent configuration](https://developers.openai.com/api/docs/guides/agents-api/configuration).

        Args:
          instructions: Additional instructions appended to the agent's default base instructions. Omit
              to leave unchanged.

          metadata: Replaces all metadata. Omit to leave unchanged, or pass null or {} to clear it.
              Up to 16 string key-value pairs, with keys up to 64 and values up to 512
              characters.

          model: The model to use for the agent. The requested model name is preserved.

          multi_agent: Explicit configuration for creating and coordinating subagents.

          name: A replacement name. Omit to leave unchanged, or pass null to clear it.

          reasoning: Reasoning configuration for the agent.

          service_tier: The service tier used for model requests.

              - `auto` - Selects the service tier automatically.
              - `default` - Uses the default service tier.
              - `flex` - Uses the flex service tier.
              - `priority` - Uses the priority service tier.
              - `fast` - Uses the fast service tier.

          text: Configuration for text generated by the agent.

          tools: Tools available to the agent.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not agent_id:
            raise ValueError(f"Expected a non-empty value for `agent_id` but received {agent_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._post(
            path_template("/agents/{agent_id}", agent_id=agent_id),
            body=await async_maybe_transform(
                {
                    "instructions": instructions,
                    "metadata": metadata,
                    "model": model,
                    "multi_agent": multi_agent,
                    "name": name,
                    "reasoning": reasoning,
                    "service_tier": service_tier,
                    "text": text,
                    "tools": tools,
                },
                agent_update_params.AgentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=Agent,
        )

    def list(
        self,
        *,
        after: str | Omit = omit,
        limit: Optional[int] | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[Agent, AsyncCursorPage[Agent]]:
        """Lists reusable agents in the current project.

        See
        [agent configuration](https://developers.openai.com/api/docs/guides/agents-api/configuration).

        Args:
          after: Return resources after this resource ID in the selected order.

          limit: The maximum number of resources to return.

          order: The order in which resources are returned. Defaults to `desc`.

              - `asc` - Returns resources in ascending order.
              - `desc` - Returns resources in descending order.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get_api_list(
            "/agents",
            page=AsyncCursorPage[Agent],
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
                    agent_list_params.AgentListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=Agent,
        )

    async def delete(
        self,
        agent_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AgentDeleted:
        """Deletes a reusable agent.

        See
        [agent configuration](https://developers.openai.com/api/docs/guides/agents-api/configuration).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not agent_id:
            raise ValueError(f"Expected a non-empty value for `agent_id` but received {agent_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._delete(
            path_template("/agents/{agent_id}", agent_id=agent_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=AgentDeleted,
        )


class AgentsWithRawResponse:
    def __init__(self, agents: Agents) -> None:
        self._agents = agents

        self.create = _legacy_response.to_raw_response_wrapper(
            agents.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            agents.retrieve,
        )
        self.update = _legacy_response.to_raw_response_wrapper(
            agents.update,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            agents.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            agents.delete,
        )

    @cached_property
    def environments(self) -> EnvironmentsWithRawResponse:
        return EnvironmentsWithRawResponse(self._agents.environments)

    @cached_property
    def vaults(self) -> VaultsWithRawResponse:
        return VaultsWithRawResponse(self._agents.vaults)

    @cached_property
    def sessions(self) -> SessionsWithRawResponse:
        return SessionsWithRawResponse(self._agents.sessions)


class AsyncAgentsWithRawResponse:
    def __init__(self, agents: AsyncAgents) -> None:
        self._agents = agents

        self.create = _legacy_response.async_to_raw_response_wrapper(
            agents.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            agents.retrieve,
        )
        self.update = _legacy_response.async_to_raw_response_wrapper(
            agents.update,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            agents.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            agents.delete,
        )

    @cached_property
    def environments(self) -> AsyncEnvironmentsWithRawResponse:
        return AsyncEnvironmentsWithRawResponse(self._agents.environments)

    @cached_property
    def vaults(self) -> AsyncVaultsWithRawResponse:
        return AsyncVaultsWithRawResponse(self._agents.vaults)

    @cached_property
    def sessions(self) -> AsyncSessionsWithRawResponse:
        return AsyncSessionsWithRawResponse(self._agents.sessions)


class AgentsWithStreamingResponse:
    def __init__(self, agents: Agents) -> None:
        self._agents = agents

        self.create = to_streamed_response_wrapper(
            agents.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            agents.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            agents.update,
        )
        self.list = to_streamed_response_wrapper(
            agents.list,
        )
        self.delete = to_streamed_response_wrapper(
            agents.delete,
        )

    @cached_property
    def environments(self) -> EnvironmentsWithStreamingResponse:
        return EnvironmentsWithStreamingResponse(self._agents.environments)

    @cached_property
    def vaults(self) -> VaultsWithStreamingResponse:
        return VaultsWithStreamingResponse(self._agents.vaults)

    @cached_property
    def sessions(self) -> SessionsWithStreamingResponse:
        return SessionsWithStreamingResponse(self._agents.sessions)


class AsyncAgentsWithStreamingResponse:
    def __init__(self, agents: AsyncAgents) -> None:
        self._agents = agents

        self.create = async_to_streamed_response_wrapper(
            agents.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            agents.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            agents.update,
        )
        self.list = async_to_streamed_response_wrapper(
            agents.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            agents.delete,
        )

    @cached_property
    def environments(self) -> AsyncEnvironmentsWithStreamingResponse:
        return AsyncEnvironmentsWithStreamingResponse(self._agents.environments)

    @cached_property
    def vaults(self) -> AsyncVaultsWithStreamingResponse:
        return AsyncVaultsWithStreamingResponse(self._agents.vaults)

    @cached_property
    def sessions(self) -> AsyncSessionsWithStreamingResponse:
        return AsyncSessionsWithStreamingResponse(self._agents.sessions)
