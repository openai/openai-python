# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable, Optional
from typing_extensions import Literal

import httpx2

from ..... import _legacy_response
from ....._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from ....._utils import path_template, maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from .....pagination import SyncCursorPage, AsyncCursorPage
from ....._base_client import AsyncPaginator, make_request_options
from .....types.beta.hosted_skill_param import HostedSkillParam
from .....types.beta.agents.environments import template_list_params, template_create_params, template_update_params
from .....types.beta.hosted_plugin_param import HostedPluginParam
from .....types.beta.setup_command_param import SetupCommandParam
from .....types.beta.hosted_environment_file_param import HostedEnvironmentFileParam
from .....types.beta.agents.environments.environment_template import EnvironmentTemplate
from .....types.beta.agents.environments.environment_template_deleted import EnvironmentTemplateDeleted

__all__ = ["Templates", "AsyncTemplates"]


class Templates(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TemplatesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return TemplatesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TemplatesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return TemplatesWithStreamingResponse(self)

    def create(
        self,
        *,
        capability_directories: Optional[SequenceNotStr[str]] | Omit = omit,
        env: Optional[Dict[str, str]] | Omit = omit,
        files: Optional[Iterable[HostedEnvironmentFileParam]] | Omit = omit,
        name: Optional[str] | Omit = omit,
        network: Optional[template_create_params.Network] | Omit = omit,
        packages: Optional[template_create_params.Packages] | Omit = omit,
        plugins: Optional[Iterable[HostedPluginParam]] | Omit = omit,
        setup_commands: Optional[Iterable[SetupCommandParam]] | Omit = omit,
        skills: Optional[Iterable[HostedSkillParam]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentTemplate:
        """
        Creates reusable environment configuration without returning confidential setup
        commands or environment values. See
        [reusing a hosted setup](https://developers.openai.com/api/docs/guides/agents-api/tools#reuse-a-hosted-plugin-setup).

        Args:
          capability_directories: Directories that contain capabilities exposed to the agent. Defaults to an empty
              list.

          env: Environment variables made available to the agent.

          files: Files available before the agent starts. Defaults to an empty list.

          name: An optional human-readable display name for the template.

          network: Network access for an OpenAI-hosted environment.

          packages: Packages to install in an OpenAI-hosted environment.

          plugins: Plugins provided as inline ZIP archives. Defaults to an empty list.

          setup_commands: Ordered, confidential setup commands. Command bodies are never returned.

          skills: Skills referenced by ID or provided as inline ZIP archives. Defaults to an empty
              list.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._post(
            "/agents/environments/templates",
            body=maybe_transform(
                {
                    "capability_directories": capability_directories,
                    "env": env,
                    "files": files,
                    "name": name,
                    "network": network,
                    "packages": packages,
                    "plugins": plugins,
                    "setup_commands": setup_commands,
                    "skills": skills,
                },
                template_create_params.TemplateCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=EnvironmentTemplate,
        )

    def retrieve(
        self,
        environment_template_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentTemplate:
        """
        Retrieves reusable environment configuration without returning confidential
        values. See
        [reusing a hosted setup](https://developers.openai.com/api/docs/guides/agents-api/tools#reuse-a-hosted-plugin-setup).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not environment_template_id:
            raise ValueError(
                f"Expected a non-empty value for `environment_template_id` but received {environment_template_id!r}"
            )
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get(
            path_template(
                "/agents/environments/templates/{environment_template_id}",
                environment_template_id=environment_template_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=EnvironmentTemplate,
        )

    def update(
        self,
        environment_template_id: str,
        *,
        capability_directories: Optional[SequenceNotStr[str]] | Omit = omit,
        env: Optional[Dict[str, str]] | Omit = omit,
        files: Optional[Iterable[HostedEnvironmentFileParam]] | Omit = omit,
        name: Optional[str] | Omit = omit,
        network: Optional[template_update_params.Network] | Omit = omit,
        packages: Optional[template_update_params.Packages] | Omit = omit,
        plugins: Optional[Iterable[HostedPluginParam]] | Omit = omit,
        setup_commands: Optional[Iterable[SetupCommandParam]] | Omit = omit,
        skills: Optional[Iterable[HostedSkillParam]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentTemplate:
        """
        Updates reusable environment configuration without returning confidential
        values. See
        [reusing a hosted setup](https://developers.openai.com/api/docs/guides/agents-api/tools#reuse-a-hosted-plugin-setup).

        Args:
          capability_directories: Directories that expose capabilities to the agent.

          env: Replacement confidential environment values.

          files: Replacement file configuration materialized for each new session.

          name: A replacement human-readable display name, or `null` to clear the name.

          network: Network access for an OpenAI-hosted environment.

          packages: Packages to install in an OpenAI-hosted environment.

          plugins: Replacement plugin configuration installed for each new session.

          setup_commands: Replacement confidential setup commands, never included in returned resources.

          skills: Replacement skill configuration installed for each new session.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not environment_template_id:
            raise ValueError(
                f"Expected a non-empty value for `environment_template_id` but received {environment_template_id!r}"
            )
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._post(
            path_template(
                "/agents/environments/templates/{environment_template_id}",
                environment_template_id=environment_template_id,
            ),
            body=maybe_transform(
                {
                    "capability_directories": capability_directories,
                    "env": env,
                    "files": files,
                    "name": name,
                    "network": network,
                    "packages": packages,
                    "plugins": plugins,
                    "setup_commands": setup_commands,
                    "skills": skills,
                },
                template_update_params.TemplateUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=EnvironmentTemplate,
        )

    def list(
        self,
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
    ) -> SyncCursorPage[EnvironmentTemplate]:
        """Lists reusable environment templates without returning confidential values.

        See
        [reusing a hosted setup](https://developers.openai.com/api/docs/guides/agents-api/tools#reuse-a-hosted-plugin-setup).

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
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get_api_list(
            "/agents/environments/templates",
            page=SyncCursorPage[EnvironmentTemplate],
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
                    template_list_params.TemplateListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=EnvironmentTemplate,
        )

    def delete(
        self,
        environment_template_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentTemplateDeleted:
        """
        Deletes reusable environment configuration and all confidential template inputs.
        See
        [reusing a hosted setup](https://developers.openai.com/api/docs/guides/agents-api/tools#reuse-a-hosted-plugin-setup).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not environment_template_id:
            raise ValueError(
                f"Expected a non-empty value for `environment_template_id` but received {environment_template_id!r}"
            )
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._delete(
            path_template(
                "/agents/environments/templates/{environment_template_id}",
                environment_template_id=environment_template_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=EnvironmentTemplateDeleted,
        )


class AsyncTemplates(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTemplatesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTemplatesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTemplatesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncTemplatesWithStreamingResponse(self)

    async def create(
        self,
        *,
        capability_directories: Optional[SequenceNotStr[str]] | Omit = omit,
        env: Optional[Dict[str, str]] | Omit = omit,
        files: Optional[Iterable[HostedEnvironmentFileParam]] | Omit = omit,
        name: Optional[str] | Omit = omit,
        network: Optional[template_create_params.Network] | Omit = omit,
        packages: Optional[template_create_params.Packages] | Omit = omit,
        plugins: Optional[Iterable[HostedPluginParam]] | Omit = omit,
        setup_commands: Optional[Iterable[SetupCommandParam]] | Omit = omit,
        skills: Optional[Iterable[HostedSkillParam]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentTemplate:
        """
        Creates reusable environment configuration without returning confidential setup
        commands or environment values. See
        [reusing a hosted setup](https://developers.openai.com/api/docs/guides/agents-api/tools#reuse-a-hosted-plugin-setup).

        Args:
          capability_directories: Directories that contain capabilities exposed to the agent. Defaults to an empty
              list.

          env: Environment variables made available to the agent.

          files: Files available before the agent starts. Defaults to an empty list.

          name: An optional human-readable display name for the template.

          network: Network access for an OpenAI-hosted environment.

          packages: Packages to install in an OpenAI-hosted environment.

          plugins: Plugins provided as inline ZIP archives. Defaults to an empty list.

          setup_commands: Ordered, confidential setup commands. Command bodies are never returned.

          skills: Skills referenced by ID or provided as inline ZIP archives. Defaults to an empty
              list.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._post(
            "/agents/environments/templates",
            body=await async_maybe_transform(
                {
                    "capability_directories": capability_directories,
                    "env": env,
                    "files": files,
                    "name": name,
                    "network": network,
                    "packages": packages,
                    "plugins": plugins,
                    "setup_commands": setup_commands,
                    "skills": skills,
                },
                template_create_params.TemplateCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=EnvironmentTemplate,
        )

    async def retrieve(
        self,
        environment_template_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentTemplate:
        """
        Retrieves reusable environment configuration without returning confidential
        values. See
        [reusing a hosted setup](https://developers.openai.com/api/docs/guides/agents-api/tools#reuse-a-hosted-plugin-setup).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not environment_template_id:
            raise ValueError(
                f"Expected a non-empty value for `environment_template_id` but received {environment_template_id!r}"
            )
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._get(
            path_template(
                "/agents/environments/templates/{environment_template_id}",
                environment_template_id=environment_template_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=EnvironmentTemplate,
        )

    async def update(
        self,
        environment_template_id: str,
        *,
        capability_directories: Optional[SequenceNotStr[str]] | Omit = omit,
        env: Optional[Dict[str, str]] | Omit = omit,
        files: Optional[Iterable[HostedEnvironmentFileParam]] | Omit = omit,
        name: Optional[str] | Omit = omit,
        network: Optional[template_update_params.Network] | Omit = omit,
        packages: Optional[template_update_params.Packages] | Omit = omit,
        plugins: Optional[Iterable[HostedPluginParam]] | Omit = omit,
        setup_commands: Optional[Iterable[SetupCommandParam]] | Omit = omit,
        skills: Optional[Iterable[HostedSkillParam]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentTemplate:
        """
        Updates reusable environment configuration without returning confidential
        values. See
        [reusing a hosted setup](https://developers.openai.com/api/docs/guides/agents-api/tools#reuse-a-hosted-plugin-setup).

        Args:
          capability_directories: Directories that expose capabilities to the agent.

          env: Replacement confidential environment values.

          files: Replacement file configuration materialized for each new session.

          name: A replacement human-readable display name, or `null` to clear the name.

          network: Network access for an OpenAI-hosted environment.

          packages: Packages to install in an OpenAI-hosted environment.

          plugins: Replacement plugin configuration installed for each new session.

          setup_commands: Replacement confidential setup commands, never included in returned resources.

          skills: Replacement skill configuration installed for each new session.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not environment_template_id:
            raise ValueError(
                f"Expected a non-empty value for `environment_template_id` but received {environment_template_id!r}"
            )
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._post(
            path_template(
                "/agents/environments/templates/{environment_template_id}",
                environment_template_id=environment_template_id,
            ),
            body=await async_maybe_transform(
                {
                    "capability_directories": capability_directories,
                    "env": env,
                    "files": files,
                    "name": name,
                    "network": network,
                    "packages": packages,
                    "plugins": plugins,
                    "setup_commands": setup_commands,
                    "skills": skills,
                },
                template_update_params.TemplateUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=EnvironmentTemplate,
        )

    def list(
        self,
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
    ) -> AsyncPaginator[EnvironmentTemplate, AsyncCursorPage[EnvironmentTemplate]]:
        """Lists reusable environment templates without returning confidential values.

        See
        [reusing a hosted setup](https://developers.openai.com/api/docs/guides/agents-api/tools#reuse-a-hosted-plugin-setup).

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
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get_api_list(
            "/agents/environments/templates",
            page=AsyncCursorPage[EnvironmentTemplate],
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
                    template_list_params.TemplateListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=EnvironmentTemplate,
        )

    async def delete(
        self,
        environment_template_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> EnvironmentTemplateDeleted:
        """
        Deletes reusable environment configuration and all confidential template inputs.
        See
        [reusing a hosted setup](https://developers.openai.com/api/docs/guides/agents-api/tools#reuse-a-hosted-plugin-setup).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not environment_template_id:
            raise ValueError(
                f"Expected a non-empty value for `environment_template_id` but received {environment_template_id!r}"
            )
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._delete(
            path_template(
                "/agents/environments/templates/{environment_template_id}",
                environment_template_id=environment_template_id,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=EnvironmentTemplateDeleted,
        )


class TemplatesWithRawResponse:
    def __init__(self, templates: Templates) -> None:
        self._templates = templates

        self.create = _legacy_response.to_raw_response_wrapper(
            templates.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            templates.retrieve,
        )
        self.update = _legacy_response.to_raw_response_wrapper(
            templates.update,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            templates.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            templates.delete,
        )


class AsyncTemplatesWithRawResponse:
    def __init__(self, templates: AsyncTemplates) -> None:
        self._templates = templates

        self.create = _legacy_response.async_to_raw_response_wrapper(
            templates.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            templates.retrieve,
        )
        self.update = _legacy_response.async_to_raw_response_wrapper(
            templates.update,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            templates.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            templates.delete,
        )


class TemplatesWithStreamingResponse:
    def __init__(self, templates: Templates) -> None:
        self._templates = templates

        self.create = to_streamed_response_wrapper(
            templates.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            templates.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            templates.update,
        )
        self.list = to_streamed_response_wrapper(
            templates.list,
        )
        self.delete = to_streamed_response_wrapper(
            templates.delete,
        )


class AsyncTemplatesWithStreamingResponse:
    def __init__(self, templates: AsyncTemplates) -> None:
        self._templates = templates

        self.create = async_to_streamed_response_wrapper(
            templates.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            templates.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            templates.update,
        )
        self.list = async_to_streamed_response_wrapper(
            templates.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            templates.delete,
        )
