# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import time
import typing_extensions
from typing import Iterable, Optional, overload
from functools import partial
from typing_extensions import Literal

import httpx

from ..... import _legacy_response
from .steps import (
    Steps,
    AsyncSteps,
    StepsWithRawResponse,
    AsyncStepsWithRawResponse,
    StepsWithStreamingResponse,
    AsyncStepsWithStreamingResponse,
)
from ....._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ....._utils import (
    is_given,
    required_args,
    maybe_transform,
    async_maybe_transform,
)
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ....._streaming import Stream, AsyncStream
from .....pagination import SyncCursorPage, AsyncCursorPage
from .....types.beta import AssistantToolParam, AssistantStreamEvent
from ....._base_client import (
    AsyncPaginator,
    make_request_options,
)
from .....lib.streaming import (
    AssistantEventHandler,
    AssistantEventHandlerT,
    AssistantStreamManager,
    AsyncAssistantEventHandler,
    AsyncAssistantEventHandlerT,
    AsyncAssistantStreamManager,
)
from .....types.beta.threads import (
    Run,
    run_list_params,
    run_create_params,
    run_update_params,
    run_submit_tool_outputs_params,
)

__all__ = ["Runs", "AsyncRuns"]


class Runs(SyncAPIResource):
    @cached_property
    def steps(self) -> Steps:
        return Steps(self._client)

    @cached_property
    def with_raw_response(self) -> RunsWithRawResponse:
        return RunsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RunsWithStreamingResponse:
        return RunsWithStreamingResponse(self)

    @overload
    def create(
        self,
        thread_id: str,
        *,
        assistant_id: str,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Optional[str] | NotGiven = NOT_GIVEN,
        stream: Optional[Literal[False]] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run:
        """
        Create a run.

        Args:
          assistant_id: The ID of the
              [assistant](https://platform.openai.com/docs/api-reference/assistants) to use to
              execute this run.

          additional_instructions: Appends additional instructions at the end of the instructions for the run. This
              is useful for modifying the behavior on a per-run basis without overriding other
              instructions.

          additional_messages: Adds additional messages to the thread before creating the run.

          instructions: Overrides the
              [instructions](https://platform.openai.com/docs/api-reference/assistants/createAssistant)
              of the assistant. This is useful for modifying the behavior on a per-run basis.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format. Keys
              can be a maximum of 64 characters long and values can be a maxium of 512
              characters long.

          model: The ID of the [Model](https://platform.openai.com/docs/api-reference/models) to
              be used to execute this run. If a value is provided here, it will override the
              model associated with the assistant. If not, the model associated with the
              assistant will be used.

          stream: If `true`, returns a stream of events that happen during the Run as server-sent
              events, terminating when the Run enters a terminal state with a `data: [DONE]`
              message.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic.

          tools: Override the tools the assistant can use for this run. This is useful for
              modifying the behavior on a per-run basis.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        thread_id: str,
        *,
        assistant_id: str,
        stream: Literal[True],
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Optional[str] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Stream[AssistantStreamEvent]:
        """
        Create a run.

        Args:
          assistant_id: The ID of the
              [assistant](https://platform.openai.com/docs/api-reference/assistants) to use to
              execute this run.

          stream: If `true`, returns a stream of events that happen during the Run as server-sent
              events, terminating when the Run enters a terminal state with a `data: [DONE]`
              message.

          additional_instructions: Appends additional instructions at the end of the instructions for the run. This
              is useful for modifying the behavior on a per-run basis without overriding other
              instructions.

          additional_messages: Adds additional messages to the thread before creating the run.

          instructions: Overrides the
              [instructions](https://platform.openai.com/docs/api-reference/assistants/createAssistant)
              of the assistant. This is useful for modifying the behavior on a per-run basis.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format. Keys
              can be a maximum of 64 characters long and values can be a maxium of 512
              characters long.

          model: The ID of the [Model](https://platform.openai.com/docs/api-reference/models) to
              be used to execute this run. If a value is provided here, it will override the
              model associated with the assistant. If not, the model associated with the
              assistant will be used.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic.

          tools: Override the tools the assistant can use for this run. This is useful for
              modifying the behavior on a per-run basis.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        thread_id: str,
        *,
        assistant_id: str,
        stream: bool,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Optional[str] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run | Stream[AssistantStreamEvent]:
        """
        Create a run.

        Args:
          assistant_id: The ID of the
              [assistant](https://platform.openai.com/docs/api-reference/assistants) to use to
              execute this run.

          stream: If `true`, returns a stream of events that happen during the Run as server-sent
              events, terminating when the Run enters a terminal state with a `data: [DONE]`
              message.

          additional_instructions: Appends additional instructions at the end of the instructions for the run. This
              is useful for modifying the behavior on a per-run basis without overriding other
              instructions.

          additional_messages: Adds additional messages to the thread before creating the run.

          instructions: Overrides the
              [instructions](https://platform.openai.com/docs/api-reference/assistants/createAssistant)
              of the assistant. This is useful for modifying the behavior on a per-run basis.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format. Keys
              can be a maximum of 64 characters long and values can be a maxium of 512
              characters long.

          model: The ID of the [Model](https://platform.openai.com/docs/api-reference/models) to
              be used to execute this run. If a value is provided here, it will override the
              model associated with the assistant. If not, the model associated with the
              assistant will be used.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic.

          tools: Override the tools the assistant can use for this run. This is useful for
              modifying the behavior on a per-run basis.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["assistant_id"], ["assistant_id", "stream"])
    def create(
        self,
        thread_id: str,
        *,
        assistant_id: str,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Optional[str] | NotGiven = NOT_GIVEN,
        stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run | Stream[AssistantStreamEvent]:
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v1", **(extra_headers or {})}
        return self._post(
            f"/threads/{thread_id}/runs",
            body=maybe_transform(
                {
                    "assistant_id": assistant_id,
                    "additional_instructions": additional_instructions,
                    "additional_messages": additional_messages,
                    "instructions": instructions,
                    "metadata": metadata,
                    "model": model,
                    "stream": stream,
                    "temperature": temperature,
                    "tools": tools,
                },
                run_create_params.RunCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Run,
            stream=stream or False,
            stream_cls=Stream[AssistantStreamEvent],
        )

    def retrieve(
        self,
        run_id: str,
        *,
        thread_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run:
        """
        Retrieves a run.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v1", **(extra_headers or {})}
        return self._get(
            f"/threads/{thread_id}/runs/{run_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Run,
        )

    def update(
        self,
        run_id: str,
        *,
        thread_id: str,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run:
        """
        Modifies a run.

        Args:
          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format. Keys
              can be a maximum of 64 characters long and values can be a maxium of 512
              characters long.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v1", **(extra_headers or {})}
        return self._post(
            f"/threads/{thread_id}/runs/{run_id}",
            body=maybe_transform({"metadata": metadata}, run_update_params.RunUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Run,
        )

    def list(
        self,
        thread_id: str,
        *,
        after: str | NotGiven = NOT_GIVEN,
        before: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncCursorPage[Run]:
        """
        Returns a list of runs belonging to a thread.

        Args:
          after: A cursor for use in pagination. `after` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include after=obj_foo in order to
              fetch the next page of the list.

          before: A cursor for use in pagination. `before` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include before=obj_foo in order to
              fetch the previous page of the list.

          limit: A limit on the number of objects to be returned. Limit can range between 1 and
              100, and the default is 20.

          order: Sort order by the `created_at` timestamp of the objects. `asc` for ascending
              order and `desc` for descending order.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v1", **(extra_headers or {})}
        return self._get_api_list(
            f"/threads/{thread_id}/runs",
            page=SyncCursorPage[Run],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "before": before,
                        "limit": limit,
                        "order": order,
                    },
                    run_list_params.RunListParams,
                ),
            ),
            model=Run,
        )

    def cancel(
        self,
        run_id: str,
        *,
        thread_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run:
        """
        Cancels a run that is `in_progress`.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v1", **(extra_headers or {})}
        return self._post(
            f"/threads/{thread_id}/runs/{run_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Run,
        )

    def create_and_poll(
        self,
        *,
        assistant_id: str,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Optional[str] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        poll_interval_ms: int | NotGiven = NOT_GIVEN,
        thread_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run:
        """
        A helper to create a run an poll for a terminal state. More information on Run
        lifecycles can be found here:
        https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps
        """
        run = self.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            additional_instructions=additional_instructions,
            additional_messages=additional_messages,
            instructions=instructions,
            metadata=metadata,
            model=model,
            temperature=temperature,
            # We assume we are not streaming when polling
            stream=False,
            tools=tools,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )
        return self.poll(
            run.id,
            thread_id=thread_id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            poll_interval_ms=poll_interval_ms,
            timeout=timeout,
        )

    @overload
    @typing_extensions.deprecated("use `stream` instead")
    def create_and_stream(
        self,
        *,
        assistant_id: str,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Optional[str] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        thread_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssistantStreamManager[AssistantEventHandler]:
        """Create a Run stream"""
        ...

    @overload
    @typing_extensions.deprecated("use `stream` instead")
    def create_and_stream(
        self,
        *,
        assistant_id: str,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Optional[str] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        thread_id: str,
        event_handler: AssistantEventHandlerT,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssistantStreamManager[AssistantEventHandlerT]:
        """Create a Run stream"""
        ...

    @typing_extensions.deprecated("use `stream` instead")
    def create_and_stream(
        self,
        *,
        assistant_id: str,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Optional[str] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        thread_id: str,
        event_handler: AssistantEventHandlerT | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssistantStreamManager[AssistantEventHandler] | AssistantStreamManager[AssistantEventHandlerT]:
        """Create a Run stream"""
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")

        extra_headers = {
            "OpenAI-Beta": "assistants=v1",
            "X-Stainless-Stream-Helper": "threads.runs.create_and_stream",
            "X-Stainless-Custom-Event-Handler": "true" if event_handler else "false",
            **(extra_headers or {}),
        }
        make_request = partial(
            self._post,
            f"/threads/{thread_id}/runs",
            body=maybe_transform(
                {
                    "assistant_id": assistant_id,
                    "additional_instructions": additional_instructions,
                    "additional_messages": additional_messages,
                    "instructions": instructions,
                    "metadata": metadata,
                    "model": model,
                    "temperature": temperature,
                    "stream": True,
                    "tools": tools,
                },
                run_create_params.RunCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Run,
            stream=True,
            stream_cls=Stream[AssistantStreamEvent],
        )
        return AssistantStreamManager(make_request, event_handler=event_handler or AssistantEventHandler())

    def poll(
        self,
        run_id: str,
        thread_id: str,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        poll_interval_ms: int | NotGiven = NOT_GIVEN,
    ) -> Run:
        """
        A helper to poll a run status until it reaches a terminal state. More
        information on Run lifecycles can be found here:
        https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps
        """
        extra_headers = {"X-Stainless-Poll-Helper": "true", **(extra_headers or {})}

        if is_given(poll_interval_ms):
            extra_headers["X-Stainless-Custom-Poll-Interval"] = str(poll_interval_ms)

        terminal_states = {"requires_action", "cancelled", "completed", "failed", "expired"}
        while True:
            response = self.with_raw_response.retrieve(
                thread_id=thread_id,
                run_id=run_id,
                extra_headers=extra_headers,
                extra_body=extra_body,
                extra_query=extra_query,
                timeout=timeout,
            )

            run = response.parse()
            # Return if we reached a terminal state
            if run.status in terminal_states:
                return run

            if not is_given(poll_interval_ms):
                from_header = response.headers.get("openai-poll-after-ms")
                if from_header is not None:
                    poll_interval_ms = int(from_header)
                else:
                    poll_interval_ms = 1000

            time.sleep(poll_interval_ms / 1000)

    @overload
    def stream(
        self,
        *,
        assistant_id: str,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Optional[str] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        thread_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssistantStreamManager[AssistantEventHandler]:
        """Create a Run stream"""
        ...

    @overload
    def stream(
        self,
        *,
        assistant_id: str,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Optional[str] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        thread_id: str,
        event_handler: AssistantEventHandlerT,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssistantStreamManager[AssistantEventHandlerT]:
        """Create a Run stream"""
        ...

    def stream(
        self,
        *,
        assistant_id: str,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Optional[str] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        thread_id: str,
        event_handler: AssistantEventHandlerT | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssistantStreamManager[AssistantEventHandler] | AssistantStreamManager[AssistantEventHandlerT]:
        """Create a Run stream"""
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")

        extra_headers = {
            "OpenAI-Beta": "assistants=v1",
            "X-Stainless-Stream-Helper": "threads.runs.create_and_stream",
            "X-Stainless-Custom-Event-Handler": "true" if event_handler else "false",
            **(extra_headers or {}),
        }
        make_request = partial(
            self._post,
            f"/threads/{thread_id}/runs",
            body=maybe_transform(
                {
                    "assistant_id": assistant_id,
                    "additional_instructions": additional_instructions,
                    "additional_messages": additional_messages,
                    "instructions": instructions,
                    "metadata": metadata,
                    "model": model,
                    "temperature": temperature,
                    "stream": True,
                    "tools": tools,
                },
                run_create_params.RunCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Run,
            stream=True,
            stream_cls=Stream[AssistantStreamEvent],
        )
        return AssistantStreamManager(make_request, event_handler=event_handler or AssistantEventHandler())

    @overload
    def submit_tool_outputs(
        self,
        run_id: str,
        *,
        thread_id: str,
        tool_outputs: Iterable[run_submit_tool_outputs_params.ToolOutput],
        stream: Optional[Literal[False]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run:
        """
        When a run has the `status: "requires_action"` and `required_action.type` is
        `submit_tool_outputs`, this endpoint can be used to submit the outputs from the
        tool calls once they're all completed. All outputs must be submitted in a single
        request.

        Args:
          tool_outputs: A list of tools for which the outputs are being submitted.

          stream: If `true`, returns a stream of events that happen during the Run as server-sent
              events, terminating when the Run enters a terminal state with a `data: [DONE]`
              message.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def submit_tool_outputs(
        self,
        run_id: str,
        *,
        thread_id: str,
        stream: Literal[True],
        tool_outputs: Iterable[run_submit_tool_outputs_params.ToolOutput],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Stream[AssistantStreamEvent]:
        """
        When a run has the `status: "requires_action"` and `required_action.type` is
        `submit_tool_outputs`, this endpoint can be used to submit the outputs from the
        tool calls once they're all completed. All outputs must be submitted in a single
        request.

        Args:
          stream: If `true`, returns a stream of events that happen during the Run as server-sent
              events, terminating when the Run enters a terminal state with a `data: [DONE]`
              message.

          tool_outputs: A list of tools for which the outputs are being submitted.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def submit_tool_outputs(
        self,
        run_id: str,
        *,
        thread_id: str,
        stream: bool,
        tool_outputs: Iterable[run_submit_tool_outputs_params.ToolOutput],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run | Stream[AssistantStreamEvent]:
        """
        When a run has the `status: "requires_action"` and `required_action.type` is
        `submit_tool_outputs`, this endpoint can be used to submit the outputs from the
        tool calls once they're all completed. All outputs must be submitted in a single
        request.

        Args:
          stream: If `true`, returns a stream of events that happen during the Run as server-sent
              events, terminating when the Run enters a terminal state with a `data: [DONE]`
              message.

          tool_outputs: A list of tools for which the outputs are being submitted.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["thread_id", "tool_outputs"], ["thread_id", "stream", "tool_outputs"])
    def submit_tool_outputs(
        self,
        run_id: str,
        *,
        thread_id: str,
        tool_outputs: Iterable[run_submit_tool_outputs_params.ToolOutput],
        stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run | Stream[AssistantStreamEvent]:
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v1", **(extra_headers or {})}
        return self._post(
            f"/threads/{thread_id}/runs/{run_id}/submit_tool_outputs",
            body=maybe_transform(
                {
                    "tool_outputs": tool_outputs,
                    "stream": stream,
                },
                run_submit_tool_outputs_params.RunSubmitToolOutputsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Run,
            stream=stream or False,
            stream_cls=Stream[AssistantStreamEvent],
        )

    def submit_tool_outputs_and_poll(
        self,
        *,
        tool_outputs: Iterable[run_submit_tool_outputs_params.ToolOutput],
        run_id: str,
        thread_id: str,
        poll_interval_ms: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run:
        """
        A helper to submit a tool output to a run and poll for a terminal run state.
        More information on Run lifecycles can be found here:
        https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps
        """
        run = self.submit_tool_outputs(
            run_id=run_id,
            thread_id=thread_id,
            tool_outputs=tool_outputs,
            stream=False,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )
        return self.poll(
            run_id=run.id,
            thread_id=thread_id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            poll_interval_ms=poll_interval_ms,
        )

    @overload
    def submit_tool_outputs_stream(
        self,
        *,
        tool_outputs: Iterable[run_submit_tool_outputs_params.ToolOutput],
        run_id: str,
        thread_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssistantStreamManager[AssistantEventHandler]:
        """
        Submit the tool outputs from a previous run and stream the run to a terminal
        state. More information on Run lifecycles can be found here:
        https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps
        """
        ...

    @overload
    def submit_tool_outputs_stream(
        self,
        *,
        tool_outputs: Iterable[run_submit_tool_outputs_params.ToolOutput],
        run_id: str,
        thread_id: str,
        event_handler: AssistantEventHandlerT,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssistantStreamManager[AssistantEventHandlerT]:
        """
        Submit the tool outputs from a previous run and stream the run to a terminal
        state. More information on Run lifecycles can be found here:
        https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps
        """
        ...

    def submit_tool_outputs_stream(
        self,
        *,
        tool_outputs: Iterable[run_submit_tool_outputs_params.ToolOutput],
        run_id: str,
        thread_id: str,
        event_handler: AssistantEventHandlerT | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssistantStreamManager[AssistantEventHandler] | AssistantStreamManager[AssistantEventHandlerT]:
        """
        Submit the tool outputs from a previous run and stream the run to a terminal
        state. More information on Run lifecycles can be found here:
        https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps
        """
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")

        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")

        extra_headers = {
            "OpenAI-Beta": "assistants=v1",
            "X-Stainless-Stream-Helper": "threads.runs.submit_tool_outputs_stream",
            "X-Stainless-Custom-Event-Handler": "true" if event_handler else "false",
            **(extra_headers or {}),
        }
        request = partial(
            self._post,
            f"/threads/{thread_id}/runs/{run_id}/submit_tool_outputs",
            body=maybe_transform(
                {
                    "tool_outputs": tool_outputs,
                    "stream": True,
                },
                run_submit_tool_outputs_params.RunSubmitToolOutputsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Run,
            stream=True,
            stream_cls=Stream[AssistantStreamEvent],
        )
        return AssistantStreamManager(request, event_handler=event_handler or AssistantEventHandler())


class AsyncRuns(AsyncAPIResource):
    @cached_property
    def steps(self) -> AsyncSteps:
        return AsyncSteps(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncRunsWithRawResponse:
        return AsyncRunsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRunsWithStreamingResponse:
        return AsyncRunsWithStreamingResponse(self)

    @overload
    async def create(
        self,
        thread_id: str,
        *,
        assistant_id: str,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Optional[str] | NotGiven = NOT_GIVEN,
        stream: Optional[Literal[False]] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run:
        """
        Create a run.

        Args:
          assistant_id: The ID of the
              [assistant](https://platform.openai.com/docs/api-reference/assistants) to use to
              execute this run.

          additional_instructions: Appends additional instructions at the end of the instructions for the run. This
              is useful for modifying the behavior on a per-run basis without overriding other
              instructions.

          additional_messages: Adds additional messages to the thread before creating the run.

          instructions: Overrides the
              [instructions](https://platform.openai.com/docs/api-reference/assistants/createAssistant)
              of the assistant. This is useful for modifying the behavior on a per-run basis.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format. Keys
              can be a maximum of 64 characters long and values can be a maxium of 512
              characters long.

          model: The ID of the [Model](https://platform.openai.com/docs/api-reference/models) to
              be used to execute this run. If a value is provided here, it will override the
              model associated with the assistant. If not, the model associated with the
              assistant will be used.

          stream: If `true`, returns a stream of events that happen during the Run as server-sent
              events, terminating when the Run enters a terminal state with a `data: [DONE]`
              message.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic.

          tools: Override the tools the assistant can use for this run. This is useful for
              modifying the behavior on a per-run basis.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        thread_id: str,
        *,
        assistant_id: str,
        stream: Literal[True],
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Optional[str] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncStream[AssistantStreamEvent]:
        """
        Create a run.

        Args:
          assistant_id: The ID of the
              [assistant](https://platform.openai.com/docs/api-reference/assistants) to use to
              execute this run.

          stream: If `true`, returns a stream of events that happen during the Run as server-sent
              events, terminating when the Run enters a terminal state with a `data: [DONE]`
              message.

          additional_instructions: Appends additional instructions at the end of the instructions for the run. This
              is useful for modifying the behavior on a per-run basis without overriding other
              instructions.

          additional_messages: Adds additional messages to the thread before creating the run.

          instructions: Overrides the
              [instructions](https://platform.openai.com/docs/api-reference/assistants/createAssistant)
              of the assistant. This is useful for modifying the behavior on a per-run basis.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format. Keys
              can be a maximum of 64 characters long and values can be a maxium of 512
              characters long.

          model: The ID of the [Model](https://platform.openai.com/docs/api-reference/models) to
              be used to execute this run. If a value is provided here, it will override the
              model associated with the assistant. If not, the model associated with the
              assistant will be used.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic.

          tools: Override the tools the assistant can use for this run. This is useful for
              modifying the behavior on a per-run basis.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        thread_id: str,
        *,
        assistant_id: str,
        stream: bool,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Optional[str] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run | AsyncStream[AssistantStreamEvent]:
        """
        Create a run.

        Args:
          assistant_id: The ID of the
              [assistant](https://platform.openai.com/docs/api-reference/assistants) to use to
              execute this run.

          stream: If `true`, returns a stream of events that happen during the Run as server-sent
              events, terminating when the Run enters a terminal state with a `data: [DONE]`
              message.

          additional_instructions: Appends additional instructions at the end of the instructions for the run. This
              is useful for modifying the behavior on a per-run basis without overriding other
              instructions.

          additional_messages: Adds additional messages to the thread before creating the run.

          instructions: Overrides the
              [instructions](https://platform.openai.com/docs/api-reference/assistants/createAssistant)
              of the assistant. This is useful for modifying the behavior on a per-run basis.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format. Keys
              can be a maximum of 64 characters long and values can be a maxium of 512
              characters long.

          model: The ID of the [Model](https://platform.openai.com/docs/api-reference/models) to
              be used to execute this run. If a value is provided here, it will override the
              model associated with the assistant. If not, the model associated with the
              assistant will be used.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic.

          tools: Override the tools the assistant can use for this run. This is useful for
              modifying the behavior on a per-run basis.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["assistant_id"], ["assistant_id", "stream"])
    async def create(
        self,
        thread_id: str,
        *,
        assistant_id: str,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Optional[str] | NotGiven = NOT_GIVEN,
        stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run | AsyncStream[AssistantStreamEvent]:
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v1", **(extra_headers or {})}
        return await self._post(
            f"/threads/{thread_id}/runs",
            body=await async_maybe_transform(
                {
                    "assistant_id": assistant_id,
                    "additional_instructions": additional_instructions,
                    "additional_messages": additional_messages,
                    "instructions": instructions,
                    "metadata": metadata,
                    "model": model,
                    "stream": stream,
                    "temperature": temperature,
                    "tools": tools,
                },
                run_create_params.RunCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Run,
            stream=stream or False,
            stream_cls=AsyncStream[AssistantStreamEvent],
        )

    async def retrieve(
        self,
        run_id: str,
        *,
        thread_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run:
        """
        Retrieves a run.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v1", **(extra_headers or {})}
        return await self._get(
            f"/threads/{thread_id}/runs/{run_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Run,
        )

    async def update(
        self,
        run_id: str,
        *,
        thread_id: str,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run:
        """
        Modifies a run.

        Args:
          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format. Keys
              can be a maximum of 64 characters long and values can be a maxium of 512
              characters long.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v1", **(extra_headers or {})}
        return await self._post(
            f"/threads/{thread_id}/runs/{run_id}",
            body=await async_maybe_transform({"metadata": metadata}, run_update_params.RunUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Run,
        )

    def list(
        self,
        thread_id: str,
        *,
        after: str | NotGiven = NOT_GIVEN,
        before: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[Run, AsyncCursorPage[Run]]:
        """
        Returns a list of runs belonging to a thread.

        Args:
          after: A cursor for use in pagination. `after` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include after=obj_foo in order to
              fetch the next page of the list.

          before: A cursor for use in pagination. `before` is an object ID that defines your place
              in the list. For instance, if you make a list request and receive 100 objects,
              ending with obj_foo, your subsequent call can include before=obj_foo in order to
              fetch the previous page of the list.

          limit: A limit on the number of objects to be returned. Limit can range between 1 and
              100, and the default is 20.

          order: Sort order by the `created_at` timestamp of the objects. `asc` for ascending
              order and `desc` for descending order.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v1", **(extra_headers or {})}
        return self._get_api_list(
            f"/threads/{thread_id}/runs",
            page=AsyncCursorPage[Run],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "after": after,
                        "before": before,
                        "limit": limit,
                        "order": order,
                    },
                    run_list_params.RunListParams,
                ),
            ),
            model=Run,
        )

    async def cancel(
        self,
        run_id: str,
        *,
        thread_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run:
        """
        Cancels a run that is `in_progress`.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v1", **(extra_headers or {})}
        return await self._post(
            f"/threads/{thread_id}/runs/{run_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Run,
        )

    async def create_and_poll(
        self,
        *,
        assistant_id: str,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Optional[str] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        poll_interval_ms: int | NotGiven = NOT_GIVEN,
        thread_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run:
        """
        A helper to create a run an poll for a terminal state. More information on Run
        lifecycles can be found here:
        https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps
        """
        run = await self.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            additional_instructions=additional_instructions,
            additional_messages=additional_messages,
            instructions=instructions,
            metadata=metadata,
            model=model,
            temperature=temperature,
            # We assume we are not streaming when polling
            stream=False,
            tools=tools,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )
        return await self.poll(
            run.id,
            thread_id=thread_id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            poll_interval_ms=poll_interval_ms,
            timeout=timeout,
        )

    @overload
    @typing_extensions.deprecated("use `stream` instead")
    def create_and_stream(
        self,
        *,
        assistant_id: str,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Optional[str] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        thread_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncAssistantStreamManager[AsyncAssistantEventHandler]:
        """Create a Run stream"""
        ...

    @overload
    @typing_extensions.deprecated("use `stream` instead")
    def create_and_stream(
        self,
        *,
        assistant_id: str,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Optional[str] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        thread_id: str,
        event_handler: AsyncAssistantEventHandlerT,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncAssistantStreamManager[AsyncAssistantEventHandlerT]:
        """Create a Run stream"""
        ...

    @typing_extensions.deprecated("use `stream` instead")
    def create_and_stream(
        self,
        *,
        assistant_id: str,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Optional[str] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        thread_id: str,
        event_handler: AsyncAssistantEventHandlerT | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> (
        AsyncAssistantStreamManager[AsyncAssistantEventHandler]
        | AsyncAssistantStreamManager[AsyncAssistantEventHandlerT]
    ):
        """Create a Run stream"""
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")

        extra_headers = {
            "OpenAI-Beta": "assistants=v1",
            "X-Stainless-Stream-Helper": "threads.runs.create_and_stream",
            "X-Stainless-Custom-Event-Handler": "true" if event_handler else "false",
            **(extra_headers or {}),
        }
        request = self._post(
            f"/threads/{thread_id}/runs",
            body=maybe_transform(
                {
                    "assistant_id": assistant_id,
                    "additional_instructions": additional_instructions,
                    "additional_messages": additional_messages,
                    "instructions": instructions,
                    "metadata": metadata,
                    "model": model,
                    "temperature": temperature,
                    "stream": True,
                    "tools": tools,
                },
                run_create_params.RunCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Run,
            stream=True,
            stream_cls=AsyncStream[AssistantStreamEvent],
        )
        return AsyncAssistantStreamManager(request, event_handler=event_handler or AsyncAssistantEventHandler())

    async def poll(
        self,
        run_id: str,
        thread_id: str,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        poll_interval_ms: int | NotGiven = NOT_GIVEN,
    ) -> Run:
        """
        A helper to poll a run status until it reaches a terminal state. More
        information on Run lifecycles can be found here:
        https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps
        """
        extra_headers = {"X-Stainless-Poll-Helper": "true", **(extra_headers or {})}

        if is_given(poll_interval_ms):
            extra_headers["X-Stainless-Custom-Poll-Interval"] = str(poll_interval_ms)

        terminal_states = {"requires_action", "cancelled", "completed", "failed", "expired"}
        while True:
            response = await self.with_raw_response.retrieve(
                thread_id=thread_id,
                run_id=run_id,
                extra_headers=extra_headers,
                extra_body=extra_body,
                extra_query=extra_query,
                timeout=timeout,
            )

            run = response.parse()
            # Return if we reached a terminal state
            if run.status in terminal_states:
                return run

            if not is_given(poll_interval_ms):
                from_header = response.headers.get("openai-poll-after-ms")
                if from_header is not None:
                    poll_interval_ms = int(from_header)
                else:
                    poll_interval_ms = 1000

            time.sleep(poll_interval_ms / 1000)

    @overload
    def stream(
        self,
        *,
        assistant_id: str,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Optional[str] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        thread_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncAssistantStreamManager[AsyncAssistantEventHandler]:
        """Create a Run stream"""
        ...

    @overload
    def stream(
        self,
        *,
        assistant_id: str,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Optional[str] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        thread_id: str,
        event_handler: AsyncAssistantEventHandlerT,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncAssistantStreamManager[AsyncAssistantEventHandlerT]:
        """Create a Run stream"""
        ...

    def stream(
        self,
        *,
        assistant_id: str,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Optional[str] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        thread_id: str,
        event_handler: AsyncAssistantEventHandlerT | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> (
        AsyncAssistantStreamManager[AsyncAssistantEventHandler]
        | AsyncAssistantStreamManager[AsyncAssistantEventHandlerT]
    ):
        """Create a Run stream"""
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")

        extra_headers = {
            "OpenAI-Beta": "assistants=v1",
            "X-Stainless-Stream-Helper": "threads.runs.create_and_stream",
            "X-Stainless-Custom-Event-Handler": "true" if event_handler else "false",
            **(extra_headers or {}),
        }
        request = self._post(
            f"/threads/{thread_id}/runs",
            body=maybe_transform(
                {
                    "assistant_id": assistant_id,
                    "additional_instructions": additional_instructions,
                    "additional_messages": additional_messages,
                    "instructions": instructions,
                    "metadata": metadata,
                    "model": model,
                    "temperature": temperature,
                    "stream": True,
                    "tools": tools,
                },
                run_create_params.RunCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Run,
            stream=True,
            stream_cls=AsyncStream[AssistantStreamEvent],
        )
        return AsyncAssistantStreamManager(request, event_handler=event_handler or AsyncAssistantEventHandler())

    @overload
    async def submit_tool_outputs(
        self,
        run_id: str,
        *,
        thread_id: str,
        tool_outputs: Iterable[run_submit_tool_outputs_params.ToolOutput],
        stream: Optional[Literal[False]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run:
        """
        When a run has the `status: "requires_action"` and `required_action.type` is
        `submit_tool_outputs`, this endpoint can be used to submit the outputs from the
        tool calls once they're all completed. All outputs must be submitted in a single
        request.

        Args:
          tool_outputs: A list of tools for which the outputs are being submitted.

          stream: If `true`, returns a stream of events that happen during the Run as server-sent
              events, terminating when the Run enters a terminal state with a `data: [DONE]`
              message.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def submit_tool_outputs(
        self,
        run_id: str,
        *,
        thread_id: str,
        stream: Literal[True],
        tool_outputs: Iterable[run_submit_tool_outputs_params.ToolOutput],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncStream[AssistantStreamEvent]:
        """
        When a run has the `status: "requires_action"` and `required_action.type` is
        `submit_tool_outputs`, this endpoint can be used to submit the outputs from the
        tool calls once they're all completed. All outputs must be submitted in a single
        request.

        Args:
          stream: If `true`, returns a stream of events that happen during the Run as server-sent
              events, terminating when the Run enters a terminal state with a `data: [DONE]`
              message.

          tool_outputs: A list of tools for which the outputs are being submitted.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def submit_tool_outputs(
        self,
        run_id: str,
        *,
        thread_id: str,
        stream: bool,
        tool_outputs: Iterable[run_submit_tool_outputs_params.ToolOutput],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run | AsyncStream[AssistantStreamEvent]:
        """
        When a run has the `status: "requires_action"` and `required_action.type` is
        `submit_tool_outputs`, this endpoint can be used to submit the outputs from the
        tool calls once they're all completed. All outputs must be submitted in a single
        request.

        Args:
          stream: If `true`, returns a stream of events that happen during the Run as server-sent
              events, terminating when the Run enters a terminal state with a `data: [DONE]`
              message.

          tool_outputs: A list of tools for which the outputs are being submitted.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["thread_id", "tool_outputs"], ["thread_id", "stream", "tool_outputs"])
    async def submit_tool_outputs(
        self,
        run_id: str,
        *,
        thread_id: str,
        tool_outputs: Iterable[run_submit_tool_outputs_params.ToolOutput],
        stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run | AsyncStream[AssistantStreamEvent]:
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v1", **(extra_headers or {})}
        return await self._post(
            f"/threads/{thread_id}/runs/{run_id}/submit_tool_outputs",
            body=await async_maybe_transform(
                {
                    "tool_outputs": tool_outputs,
                    "stream": stream,
                },
                run_submit_tool_outputs_params.RunSubmitToolOutputsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Run,
            stream=stream or False,
            stream_cls=AsyncStream[AssistantStreamEvent],
        )

    async def submit_tool_outputs_and_poll(
        self,
        *,
        tool_outputs: Iterable[run_submit_tool_outputs_params.ToolOutput],
        run_id: str,
        thread_id: str,
        poll_interval_ms: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run:
        """
        A helper to submit a tool output to a run and poll for a terminal run state.
        More information on Run lifecycles can be found here:
        https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps
        """
        run = await self.submit_tool_outputs(
            run_id=run_id,
            thread_id=thread_id,
            tool_outputs=tool_outputs,
            stream=False,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )
        return await self.poll(
            run_id=run.id,
            thread_id=thread_id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            poll_interval_ms=poll_interval_ms,
        )

    @overload
    def submit_tool_outputs_stream(
        self,
        *,
        tool_outputs: Iterable[run_submit_tool_outputs_params.ToolOutput],
        run_id: str,
        thread_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncAssistantStreamManager[AsyncAssistantEventHandler]:
        """
        Submit the tool outputs from a previous run and stream the run to a terminal
        state. More information on Run lifecycles can be found here:
        https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps
        """
        ...

    @overload
    def submit_tool_outputs_stream(
        self,
        *,
        tool_outputs: Iterable[run_submit_tool_outputs_params.ToolOutput],
        run_id: str,
        thread_id: str,
        event_handler: AsyncAssistantEventHandlerT,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncAssistantStreamManager[AsyncAssistantEventHandlerT]:
        """
        Submit the tool outputs from a previous run and stream the run to a terminal
        state. More information on Run lifecycles can be found here:
        https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps
        """
        ...

    def submit_tool_outputs_stream(
        self,
        *,
        tool_outputs: Iterable[run_submit_tool_outputs_params.ToolOutput],
        run_id: str,
        thread_id: str,
        event_handler: AsyncAssistantEventHandlerT | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> (
        AsyncAssistantStreamManager[AsyncAssistantEventHandler]
        | AsyncAssistantStreamManager[AsyncAssistantEventHandlerT]
    ):
        """
        Submit the tool outputs from a previous run and stream the run to a terminal
        state. More information on Run lifecycles can be found here:
        https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps
        """
        if not run_id:
            raise ValueError(f"Expected a non-empty value for `run_id` but received {run_id!r}")

        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")

        extra_headers = {
            "OpenAI-Beta": "assistants=v1",
            "X-Stainless-Stream-Helper": "threads.runs.submit_tool_outputs_stream",
            "X-Stainless-Custom-Event-Handler": "true" if event_handler else "false",
            **(extra_headers or {}),
        }
        request = self._post(
            f"/threads/{thread_id}/runs/{run_id}/submit_tool_outputs",
            body=maybe_transform(
                {
                    "tool_outputs": tool_outputs,
                    "stream": True,
                },
                run_submit_tool_outputs_params.RunSubmitToolOutputsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Run,
            stream=True,
            stream_cls=AsyncStream[AssistantStreamEvent],
        )
        return AsyncAssistantStreamManager(request, event_handler=event_handler or AsyncAssistantEventHandler())


class RunsWithRawResponse:
    def __init__(self, runs: Runs) -> None:
        self._runs = runs

        self.create = _legacy_response.to_raw_response_wrapper(
            runs.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            runs.retrieve,
        )
        self.update = _legacy_response.to_raw_response_wrapper(
            runs.update,
        )
        self.list = _legacy_response.to_raw_response_wrapper(
            runs.list,
        )
        self.cancel = _legacy_response.to_raw_response_wrapper(
            runs.cancel,
        )
        self.submit_tool_outputs = _legacy_response.to_raw_response_wrapper(
            runs.submit_tool_outputs,
        )

    @cached_property
    def steps(self) -> StepsWithRawResponse:
        return StepsWithRawResponse(self._runs.steps)


class AsyncRunsWithRawResponse:
    def __init__(self, runs: AsyncRuns) -> None:
        self._runs = runs

        self.create = _legacy_response.async_to_raw_response_wrapper(
            runs.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            runs.retrieve,
        )
        self.update = _legacy_response.async_to_raw_response_wrapper(
            runs.update,
        )
        self.list = _legacy_response.async_to_raw_response_wrapper(
            runs.list,
        )
        self.cancel = _legacy_response.async_to_raw_response_wrapper(
            runs.cancel,
        )
        self.submit_tool_outputs = _legacy_response.async_to_raw_response_wrapper(
            runs.submit_tool_outputs,
        )

    @cached_property
    def steps(self) -> AsyncStepsWithRawResponse:
        return AsyncStepsWithRawResponse(self._runs.steps)


class RunsWithStreamingResponse:
    def __init__(self, runs: Runs) -> None:
        self._runs = runs

        self.create = to_streamed_response_wrapper(
            runs.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            runs.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            runs.update,
        )
        self.list = to_streamed_response_wrapper(
            runs.list,
        )
        self.cancel = to_streamed_response_wrapper(
            runs.cancel,
        )
        self.submit_tool_outputs = to_streamed_response_wrapper(
            runs.submit_tool_outputs,
        )

    @cached_property
    def steps(self) -> StepsWithStreamingResponse:
        return StepsWithStreamingResponse(self._runs.steps)


class AsyncRunsWithStreamingResponse:
    def __init__(self, runs: AsyncRuns) -> None:
        self._runs = runs

        self.create = async_to_streamed_response_wrapper(
            runs.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            runs.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            runs.update,
        )
        self.list = async_to_streamed_response_wrapper(
            runs.list,
        )
        self.cancel = async_to_streamed_response_wrapper(
            runs.cancel,
        )
        self.submit_tool_outputs = async_to_streamed_response_wrapper(
            runs.submit_tool_outputs,
        )

    @cached_property
    def steps(self) -> AsyncStepsWithStreamingResponse:
        return AsyncStepsWithStreamingResponse(self._runs.steps)
