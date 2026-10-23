# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, Dict, cast
from typing_extensions import Literal, overload

import httpx2

from ..... import _legacy_response
from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ....._utils import path_template, required_args, maybe_transform, async_maybe_transform
from ....._compat import cached_property
from .invocations import (
    Invocations,
    AsyncInvocations,
    InvocationsWithRawResponse,
    AsyncInvocationsWithRawResponse,
    InvocationsWithStreamingResponse,
    AsyncInvocationsWithStreamingResponse,
)
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from .....pagination import SyncCursorPage, AsyncCursorPage
from ....._base_client import AsyncPaginator, make_request_options
from .....types.beta.agents import (
    automation_list_params,
    automation_create_params,
    automation_update_params,
)
from .....types.beta.agents.automation import Automation
from .....types.beta.agents.automation_deleted import AutomationDeleted
from .....types.beta.agents.automation_target_param import AutomationTargetParam
from .....types.beta.agents.automation_metadata_param import AutomationMetadataParam

__all__ = ["Automations", "AsyncAutomations"]


class Automations(SyncAPIResource):
    @cached_property
    def invocations(self) -> Invocations:
        return Invocations(self._client)

    @cached_property
    def with_raw_response(self) -> AutomationsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AutomationsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AutomationsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AutomationsWithStreamingResponse(self)

    @overload
    def create(
        self,
        *,
        expression: str,
        name: str,
        target: AutomationTargetParam,
        timezone: str,
        type: Literal["periodic"],
        metadata: AutomationMetadataParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Automation:
        """
        Saves an active automation without invoking it immediately.

        Args:
          expression: A standard five-field cron expression defining scheduled occurrences.

          name: A human-readable name for the automation.

          target: The session an automation invocation targets.

          timezone: The IANA timezone used to interpret the cron expression.

          type: The type of the object. Always `periodic`.

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
        name: str,
        run_at: int,
        target: AutomationTargetParam,
        type: Literal["once"],
        metadata: AutomationMetadataParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Automation:
        """
        Saves an active automation without invoking it immediately.

        Args:
          name: A human-readable name for the automation.

          run_at: A future Unix timestamp in seconds.

          target: The session an automation invocation targets.

          type: The type of the object. Always `once`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["expression", "name", "target", "timezone", "type"], ["name", "run_at", "target", "type"])
    def create(
        self,
        *,
        expression: str | Omit = omit,
        name: str,
        target: AutomationTargetParam,
        timezone: str | Omit = omit,
        type: Literal["periodic"] | Literal["once"],
        metadata: AutomationMetadataParam | Omit = omit,
        run_at: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Automation:
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return cast(
            Automation,
            self._post(
                "/agents/automations",
                body=maybe_transform(
                    {
                        "expression": expression,
                        "name": name,
                        "target": target,
                        "timezone": timezone,
                        "type": type,
                        "metadata": metadata,
                        "run_at": run_at,
                    },
                    automation_create_params.AutomationCreateParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    security={"bearer_auth": True},
                ),
                cast_to=cast(Any, Automation),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def retrieve(
        self,
        automation_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Automation:
        """
        Retrieves a project-owned automation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not automation_id:
            raise ValueError(f"Expected a non-empty value for `automation_id` but received {automation_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return cast(
            Automation,
            self._get(
                path_template("/agents/automations/{automation_id}", automation_id=automation_id),
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    security={"bearer_auth": True},
                ),
                cast_to=cast(Any, Automation),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def update(
        self,
        automation_id: str,
        *,
        expression: str | Omit = omit,
        metadata: Dict[str, str] | Omit = omit,
        name: str | Omit = omit,
        run_at: int | Omit = omit,
        target: AutomationTargetParam | Omit = omit,
        timezone: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Automation:
        """
        Updates supplied fields; target and metadata replace the whole field.

        Args:
          expression: Only accepted for periodic automations.

          metadata: Replaces all metadata; omit to leave unchanged.

          run_at: A future Unix timestamp in seconds; accepted only before a one-time scheduled
              invocation exists.

          target: Replaces the complete target, retaining its type and any creator session.

          timezone: Only accepted for periodic automations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not automation_id:
            raise ValueError(f"Expected a non-empty value for `automation_id` but received {automation_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return cast(
            Automation,
            self._post(
                path_template("/agents/automations/{automation_id}", automation_id=automation_id),
                body=maybe_transform(
                    {
                        "expression": expression,
                        "metadata": metadata,
                        "name": name,
                        "run_at": run_at,
                        "target": target,
                        "timezone": timezone,
                    },
                    automation_update_params.AutomationUpdateParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    security={"bearer_auth": True},
                ),
                cast_to=cast(Any, Automation),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def list(
        self,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        session_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SyncCursorPage[Automation]:
        """
        Lists project-owned automations, optionally filtered by target session.

        Args:
          after: Return resources after this resource ID in the selected order.

          limit: The maximum number of resources to return, between 1 and 100. Defaults to 20.

          order: The order in which resources are returned. Defaults to `desc`.

              - `asc` - Returns resources in ascending order.
              - `desc` - Returns resources in descending order.

          session_id: Matches existing-session targets, including agent-created automations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get_api_list(
            "/agents/automations",
            page=SyncCursorPage[Automation],
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
                        "session_id": session_id,
                    },
                    automation_list_params.AutomationListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=cast(Any, Automation),  # Union types cannot be passed in as arguments in the type system
        )

    def delete(
        self,
        automation_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AutomationDeleted:
        """
        Deletes the automation and prevents future invocations without deleting its
        target session.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not automation_id:
            raise ValueError(f"Expected a non-empty value for `automation_id` but received {automation_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._delete(
            path_template("/agents/automations/{automation_id}", automation_id=automation_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=AutomationDeleted,
        )

    def pause(
        self,
        automation_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Automation:
        """
        Pauses future scheduled delivery without stopping an active session.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not automation_id:
            raise ValueError(f"Expected a non-empty value for `automation_id` but received {automation_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return cast(
            Automation,
            self._post(
                path_template("/agents/automations/{automation_id}/pause", automation_id=automation_id),
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    security={"bearer_auth": True},
                ),
                cast_to=cast(Any, Automation),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def resume(
        self,
        automation_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Automation:
        """
        Resumes scheduled delivery; one-time automations without a pending invocation
        require a future run_at.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not automation_id:
            raise ValueError(f"Expected a non-empty value for `automation_id` but received {automation_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return cast(
            Automation,
            self._post(
                path_template("/agents/automations/{automation_id}/resume", automation_id=automation_id),
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    security={"bearer_auth": True},
                ),
                cast_to=cast(Any, Automation),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class AsyncAutomations(AsyncAPIResource):
    @cached_property
    def invocations(self) -> AsyncInvocations:
        return AsyncInvocations(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncAutomationsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAutomationsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAutomationsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncAutomationsWithStreamingResponse(self)

    @overload
    async def create(
        self,
        *,
        expression: str,
        name: str,
        target: AutomationTargetParam,
        timezone: str,
        type: Literal["periodic"],
        metadata: AutomationMetadataParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Automation:
        """
        Saves an active automation without invoking it immediately.

        Args:
          expression: A standard five-field cron expression defining scheduled occurrences.

          name: A human-readable name for the automation.

          target: The session an automation invocation targets.

          timezone: The IANA timezone used to interpret the cron expression.

          type: The type of the object. Always `periodic`.

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
        name: str,
        run_at: int,
        target: AutomationTargetParam,
        type: Literal["once"],
        metadata: AutomationMetadataParam | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Automation:
        """
        Saves an active automation without invoking it immediately.

        Args:
          name: A human-readable name for the automation.

          run_at: A future Unix timestamp in seconds.

          target: The session an automation invocation targets.

          type: The type of the object. Always `once`.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["expression", "name", "target", "timezone", "type"], ["name", "run_at", "target", "type"])
    async def create(
        self,
        *,
        expression: str | Omit = omit,
        name: str,
        target: AutomationTargetParam,
        timezone: str | Omit = omit,
        type: Literal["periodic"] | Literal["once"],
        metadata: AutomationMetadataParam | Omit = omit,
        run_at: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Automation:
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return cast(
            Automation,
            await self._post(
                "/agents/automations",
                body=await async_maybe_transform(
                    {
                        "expression": expression,
                        "name": name,
                        "target": target,
                        "timezone": timezone,
                        "type": type,
                        "metadata": metadata,
                        "run_at": run_at,
                    },
                    automation_create_params.AutomationCreateParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    security={"bearer_auth": True},
                ),
                cast_to=cast(Any, Automation),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def retrieve(
        self,
        automation_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Automation:
        """
        Retrieves a project-owned automation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not automation_id:
            raise ValueError(f"Expected a non-empty value for `automation_id` but received {automation_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return cast(
            Automation,
            await self._get(
                path_template("/agents/automations/{automation_id}", automation_id=automation_id),
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    security={"bearer_auth": True},
                ),
                cast_to=cast(Any, Automation),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def update(
        self,
        automation_id: str,
        *,
        expression: str | Omit = omit,
        metadata: Dict[str, str] | Omit = omit,
        name: str | Omit = omit,
        run_at: int | Omit = omit,
        target: AutomationTargetParam | Omit = omit,
        timezone: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Automation:
        """
        Updates supplied fields; target and metadata replace the whole field.

        Args:
          expression: Only accepted for periodic automations.

          metadata: Replaces all metadata; omit to leave unchanged.

          run_at: A future Unix timestamp in seconds; accepted only before a one-time scheduled
              invocation exists.

          target: Replaces the complete target, retaining its type and any creator session.

          timezone: Only accepted for periodic automations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not automation_id:
            raise ValueError(f"Expected a non-empty value for `automation_id` but received {automation_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return cast(
            Automation,
            await self._post(
                path_template("/agents/automations/{automation_id}", automation_id=automation_id),
                body=await async_maybe_transform(
                    {
                        "expression": expression,
                        "metadata": metadata,
                        "name": name,
                        "run_at": run_at,
                        "target": target,
                        "timezone": timezone,
                    },
                    automation_update_params.AutomationUpdateParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    security={"bearer_auth": True},
                ),
                cast_to=cast(Any, Automation),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def list(
        self,
        *,
        after: str | Omit = omit,
        limit: int | Omit = omit,
        order: Literal["asc", "desc"] | Omit = omit,
        session_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AsyncPaginator[Automation, AsyncCursorPage[Automation]]:
        """
        Lists project-owned automations, optionally filtered by target session.

        Args:
          after: Return resources after this resource ID in the selected order.

          limit: The maximum number of resources to return, between 1 and 100. Defaults to 20.

          order: The order in which resources are returned. Defaults to `desc`.

              - `asc` - Returns resources in ascending order.
              - `desc` - Returns resources in descending order.

          session_id: Matches existing-session targets, including agent-created automations.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return self._get_api_list(
            "/agents/automations",
            page=AsyncCursorPage[Automation],
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
                        "session_id": session_id,
                    },
                    automation_list_params.AutomationListParams,
                ),
                security={"bearer_auth": True},
            ),
            model=cast(Any, Automation),  # Union types cannot be passed in as arguments in the type system
        )

    async def delete(
        self,
        automation_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> AutomationDeleted:
        """
        Deletes the automation and prevents future invocations without deleting its
        target session.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not automation_id:
            raise ValueError(f"Expected a non-empty value for `automation_id` but received {automation_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return await self._delete(
            path_template("/agents/automations/{automation_id}", automation_id=automation_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                security={"bearer_auth": True},
            ),
            cast_to=AutomationDeleted,
        )

    async def pause(
        self,
        automation_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Automation:
        """
        Pauses future scheduled delivery without stopping an active session.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not automation_id:
            raise ValueError(f"Expected a non-empty value for `automation_id` but received {automation_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return cast(
            Automation,
            await self._post(
                path_template("/agents/automations/{automation_id}/pause", automation_id=automation_id),
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    security={"bearer_auth": True},
                ),
                cast_to=cast(Any, Automation),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def resume(
        self,
        automation_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> Automation:
        """
        Resumes scheduled delivery; one-time automations without a pending invocation
        require a future run_at.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not automation_id:
            raise ValueError(f"Expected a non-empty value for `automation_id` but received {automation_id!r}")
        extra_headers = {"OpenAI-Beta": "agents=v1", **(extra_headers or {})}
        return cast(
            Automation,
            await self._post(
                path_template("/agents/automations/{automation_id}/resume", automation_id=automation_id),
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    security={"bearer_auth": True},
                ),
                cast_to=cast(Any, Automation),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class AutomationsWithRawResponse:
    def __init__(self, automations: Automations) -> None:
        self._automations = automations

        self.create = _legacy_response.to_raw_response_wrapper(
            automations.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            automations.retrieve,
        )
        self.update = _legacy_response.to_raw_response_wrapper(
            automations.update,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            automations.list,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            automations.delete,
        )
        self.pause = _legacy_response.to_raw_response_wrapper(
            automations.pause,
        )
        self.resume = _legacy_response.to_raw_response_wrapper(
            automations.resume,
        )

    @cached_property
    def invocations(self) -> InvocationsWithRawResponse:
        return InvocationsWithRawResponse(self._automations.invocations)


class AsyncAutomationsWithRawResponse:
    def __init__(self, automations: AsyncAutomations) -> None:
        self._automations = automations

        self.create = _legacy_response.async_to_raw_response_wrapper(
            automations.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            automations.retrieve,
        )
        self.update = _legacy_response.async_to_raw_response_wrapper(
            automations.update,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            automations.list,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            automations.delete,
        )
        self.pause = _legacy_response.async_to_raw_response_wrapper(
            automations.pause,
        )
        self.resume = _legacy_response.async_to_raw_response_wrapper(
            automations.resume,
        )

    @cached_property
    def invocations(self) -> AsyncInvocationsWithRawResponse:
        return AsyncInvocationsWithRawResponse(self._automations.invocations)


class AutomationsWithStreamingResponse:
    def __init__(self, automations: Automations) -> None:
        self._automations = automations

        self.create = to_streamed_response_wrapper(
            automations.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            automations.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            automations.update,
        )
        self.list = to_streamed_response_wrapper(
            automations.list,
        )
        self.delete = to_streamed_response_wrapper(
            automations.delete,
        )
        self.pause = to_streamed_response_wrapper(
            automations.pause,
        )
        self.resume = to_streamed_response_wrapper(
            automations.resume,
        )

    @cached_property
    def invocations(self) -> InvocationsWithStreamingResponse:
        return InvocationsWithStreamingResponse(self._automations.invocations)


class AsyncAutomationsWithStreamingResponse:
    def __init__(self, automations: AsyncAutomations) -> None:
        self._automations = automations

        self.create = async_to_streamed_response_wrapper(
            automations.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            automations.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            automations.update,
        )
        self.list = async_to_streamed_response_wrapper(
            automations.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            automations.delete,
        )
        self.pause = async_to_streamed_response_wrapper(
            automations.pause,
        )
        self.resume = async_to_streamed_response_wrapper(
            automations.resume,
        )

    @cached_property
    def invocations(self) -> AsyncInvocationsWithStreamingResponse:
        return AsyncInvocationsWithStreamingResponse(self._automations.invocations)
