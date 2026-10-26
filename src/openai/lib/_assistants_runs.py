"""Handwritten Assistants helper behavior behind generated public facades."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Union, Iterable, Optional
from functools import partial

import httpx2

from openai._types import NOT_GIVEN, Body, Omit, Query, Headers, NotGiven, omit, not_given
from openai._utils import is_given, path_template, maybe_transform
from openai._streaming import Stream, AsyncStream
from openai._base_client import make_request_options
from openai.lib.streaming import (
    AssistantEventHandler,
    AssistantEventHandlerT,
    AssistantStreamManager,
    AsyncAssistantEventHandler,
    AsyncAssistantEventHandlerT,
    AsyncAssistantStreamManager,
)
from openai.types.beta.threads import (
    run_create_params,
    run_submit_tool_outputs_params,
)
from openai.types.beta.threads.run import Run
from openai.types.shared.chat_model import ChatModel
from openai.types.shared_params.metadata import Metadata
from openai.types.shared.reasoning_effort import ReasoningEffort
from openai.types.beta.assistant_tool_param import AssistantToolParam
from openai.types.beta.assistant_stream_event import AssistantStreamEvent
from openai.types.beta.threads.runs.run_step_include import RunStepInclude
from openai.types.beta.assistant_tool_choice_option_param import AssistantToolChoiceOptionParam
from openai.types.beta.assistant_response_format_option_param import AssistantResponseFormatOptionParam

if TYPE_CHECKING:
    from openai.resources.beta.threads.runs.runs import Runs, AsyncRuns


def runs_create_and_poll(
    self: Runs,
    *,
    assistant_id: str,
    include: List[RunStepInclude] | Omit = omit,
    additional_instructions: Optional[str] | Omit = omit,
    additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | Omit = omit,
    instructions: Optional[str] | Omit = omit,
    max_completion_tokens: Optional[int] | Omit = omit,
    max_prompt_tokens: Optional[int] | Omit = omit,
    metadata: Optional[Metadata] | Omit = omit,
    model: Union[str, ChatModel, None] | Omit = omit,
    parallel_tool_calls: bool | Omit = omit,
    reasoning_effort: Optional[ReasoningEffort] | Omit = omit,
    response_format: Optional[AssistantResponseFormatOptionParam] | Omit = omit,
    temperature: Optional[float] | Omit = omit,
    tool_choice: Optional[AssistantToolChoiceOptionParam] | Omit = omit,
    tools: Optional[Iterable[AssistantToolParam]] | Omit = omit,
    top_p: Optional[float] | Omit = omit,
    truncation_strategy: Optional[run_create_params.TruncationStrategy] | Omit = omit,
    poll_interval_ms: int | Omit = omit,
    thread_id: str,
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx2.Timeout | None | NotGiven = NOT_GIVEN,
) -> Run:
    """
    A helper to create a run an poll for a terminal state. More information on Run
    lifecycles can be found here:
    https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps
    """
    run = self.create(  # pyright: ignore[reportDeprecated]
        thread_id=thread_id,
        assistant_id=assistant_id,
        include=include,
        additional_instructions=additional_instructions,
        additional_messages=additional_messages,
        instructions=instructions,
        max_completion_tokens=max_completion_tokens,
        max_prompt_tokens=max_prompt_tokens,
        metadata=metadata,
        model=model,
        response_format=response_format,
        temperature=temperature,
        tool_choice=tool_choice,
        parallel_tool_calls=parallel_tool_calls,
        reasoning_effort=reasoning_effort,
        # We assume we are not streaming when polling
        stream=False,
        tools=tools,
        truncation_strategy=truncation_strategy,
        top_p=top_p,
        extra_headers=extra_headers,
        extra_query=extra_query,
        extra_body=extra_body,
        timeout=timeout,
    )
    return self.poll(  # pyright: ignore[reportDeprecated]
        run.id,
        thread_id=thread_id,
        extra_headers=extra_headers,
        extra_query=extra_query,
        extra_body=extra_body,
        poll_interval_ms=poll_interval_ms,
        timeout=timeout,
    )


def runs_create_and_stream(
    self: Runs,
    *,
    assistant_id: str,
    additional_instructions: Optional[str] | Omit = omit,
    additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | Omit = omit,
    instructions: Optional[str] | Omit = omit,
    max_completion_tokens: Optional[int] | Omit = omit,
    max_prompt_tokens: Optional[int] | Omit = omit,
    metadata: Optional[Metadata] | Omit = omit,
    model: Union[str, ChatModel, None] | Omit = omit,
    parallel_tool_calls: bool | Omit = omit,
    reasoning_effort: Optional[ReasoningEffort] | Omit = omit,
    response_format: Optional[AssistantResponseFormatOptionParam] | Omit = omit,
    temperature: Optional[float] | Omit = omit,
    tool_choice: Optional[AssistantToolChoiceOptionParam] | Omit = omit,
    tools: Optional[Iterable[AssistantToolParam]] | Omit = omit,
    top_p: Optional[float] | Omit = omit,
    truncation_strategy: Optional[run_create_params.TruncationStrategy] | Omit = omit,
    thread_id: str,
    event_handler: AssistantEventHandlerT | None = None,
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx2.Timeout | None | NotGiven = NOT_GIVEN,
) -> AssistantStreamManager[AssistantEventHandler] | AssistantStreamManager[AssistantEventHandlerT]:
    """Create a Run stream"""
    if not thread_id:
        raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")

    extra_headers = {
        "OpenAI-Beta": "assistants=v2",
        "X-Stainless-Stream-Helper": "threads.runs.create_and_stream",
        "X-Stainless-Custom-Event-Handler": "true" if event_handler else "false",
        **(extra_headers or {}),
    }
    make_request = partial(
        self._post,
        path_template("/threads/{thread_id}/runs", thread_id=thread_id),
        body=maybe_transform(
            {
                "assistant_id": assistant_id,
                "additional_instructions": additional_instructions,
                "additional_messages": additional_messages,
                "instructions": instructions,
                "max_completion_tokens": max_completion_tokens,
                "max_prompt_tokens": max_prompt_tokens,
                "metadata": metadata,
                "model": model,
                "response_format": response_format,
                "temperature": temperature,
                "tool_choice": tool_choice,
                "stream": True,
                "tools": tools,
                "truncation_strategy": truncation_strategy,
                "parallel_tool_calls": parallel_tool_calls,
                "reasoning_effort": reasoning_effort,
                "top_p": top_p,
            },
            run_create_params.RunCreateParams,
        ),
        options=make_request_options(
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            security={"bearer_auth": True},
        ),
        cast_to=Run,
        stream=True,
        stream_cls=Stream[AssistantStreamEvent],
    )
    return AssistantStreamManager(make_request, event_handler=event_handler or AssistantEventHandler())


def runs_poll(
    self: Runs,
    run_id: str,
    thread_id: str,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    poll_interval_ms: int | Omit = omit,
) -> Run:
    """
    A helper to poll a run status until it reaches a terminal state. More
    information on Run lifecycles can be found here:
    https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps
    """
    extra_headers = {"X-Stainless-Poll-Helper": "true", **(extra_headers or {})}

    if is_given(poll_interval_ms):
        extra_headers["X-Stainless-Custom-Poll-Interval"] = str(poll_interval_ms)

    terminal_states = {"requires_action", "cancelled", "completed", "failed", "expired", "incomplete"}
    while True:
        response = self.with_raw_response.retrieve(  # pyright: ignore[reportDeprecated]
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

        self._sleep(poll_interval_ms / 1000)


def runs_stream(
    self: Runs,
    *,
    assistant_id: str,
    include: List[RunStepInclude] | Omit = omit,
    additional_instructions: Optional[str] | Omit = omit,
    additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | Omit = omit,
    instructions: Optional[str] | Omit = omit,
    max_completion_tokens: Optional[int] | Omit = omit,
    max_prompt_tokens: Optional[int] | Omit = omit,
    metadata: Optional[Metadata] | Omit = omit,
    model: Union[str, ChatModel, None] | Omit = omit,
    parallel_tool_calls: bool | Omit = omit,
    reasoning_effort: Optional[ReasoningEffort] | Omit = omit,
    response_format: Optional[AssistantResponseFormatOptionParam] | Omit = omit,
    temperature: Optional[float] | Omit = omit,
    tool_choice: Optional[AssistantToolChoiceOptionParam] | Omit = omit,
    tools: Optional[Iterable[AssistantToolParam]] | Omit = omit,
    top_p: Optional[float] | Omit = omit,
    truncation_strategy: Optional[run_create_params.TruncationStrategy] | Omit = omit,
    thread_id: str,
    event_handler: AssistantEventHandlerT | None = None,
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx2.Timeout | None | NotGiven = NOT_GIVEN,
) -> AssistantStreamManager[AssistantEventHandler] | AssistantStreamManager[AssistantEventHandlerT]:
    """Create a Run stream"""
    if not thread_id:
        raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")

    extra_headers = {
        "OpenAI-Beta": "assistants=v2",
        "X-Stainless-Stream-Helper": "threads.runs.create_and_stream",
        "X-Stainless-Custom-Event-Handler": "true" if event_handler else "false",
        **(extra_headers or {}),
    }
    make_request = partial(
        self._post,
        path_template("/threads/{thread_id}/runs", thread_id=thread_id),
        body=maybe_transform(
            {
                "assistant_id": assistant_id,
                "additional_instructions": additional_instructions,
                "additional_messages": additional_messages,
                "instructions": instructions,
                "max_completion_tokens": max_completion_tokens,
                "max_prompt_tokens": max_prompt_tokens,
                "metadata": metadata,
                "model": model,
                "response_format": response_format,
                "temperature": temperature,
                "tool_choice": tool_choice,
                "stream": True,
                "tools": tools,
                "parallel_tool_calls": parallel_tool_calls,
                "reasoning_effort": reasoning_effort,
                "truncation_strategy": truncation_strategy,
                "top_p": top_p,
            },
            run_create_params.RunCreateParams,
        ),
        options=make_request_options(
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            query=maybe_transform({"include": include}, run_create_params.RunCreateParams),
            security={"bearer_auth": True},
        ),
        cast_to=Run,
        stream=True,
        stream_cls=Stream[AssistantStreamEvent],
    )
    return AssistantStreamManager(make_request, event_handler=event_handler or AssistantEventHandler())


def runs_submit_tool_outputs_and_poll(
    self: Runs,
    *,
    tool_outputs: Iterable[run_submit_tool_outputs_params.ToolOutput],
    run_id: str,
    thread_id: str,
    poll_interval_ms: int | Omit = omit,
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx2.Timeout | None | NotGiven = NOT_GIVEN,
) -> Run:
    """
    A helper to submit a tool output to a run and poll for a terminal run state.
    More information on Run lifecycles can be found here:
    https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps
    """
    run = self.submit_tool_outputs(  # pyright: ignore[reportDeprecated]
        run_id=run_id,
        thread_id=thread_id,
        tool_outputs=tool_outputs,
        stream=False,
        extra_headers=extra_headers,
        extra_query=extra_query,
        extra_body=extra_body,
        timeout=timeout,
    )
    return self.poll(  # pyright: ignore[reportDeprecated]
        run_id=run.id,
        thread_id=thread_id,
        extra_headers=extra_headers,
        extra_query=extra_query,
        extra_body=extra_body,
        timeout=timeout,
        poll_interval_ms=poll_interval_ms,
    )


def runs_submit_tool_outputs_stream(
    self: Runs,
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
    timeout: float | httpx2.Timeout | None | NotGiven = NOT_GIVEN,
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
        "OpenAI-Beta": "assistants=v2",
        "X-Stainless-Stream-Helper": "threads.runs.submit_tool_outputs_stream",
        "X-Stainless-Custom-Event-Handler": "true" if event_handler else "false",
        **(extra_headers or {}),
    }
    request = partial(
        self._post,
        path_template("/threads/{thread_id}/runs/{run_id}/submit_tool_outputs", thread_id=thread_id, run_id=run_id),
        body=maybe_transform(
            {
                "tool_outputs": tool_outputs,
                "stream": True,
            },
            run_submit_tool_outputs_params.RunSubmitToolOutputsParams,
        ),
        options=make_request_options(
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            security={"bearer_auth": True},
        ),
        cast_to=Run,
        stream=True,
        stream_cls=Stream[AssistantStreamEvent],
    )
    return AssistantStreamManager(request, event_handler=event_handler or AssistantEventHandler())


async def async_runs_create_and_poll(
    self: AsyncRuns,
    *,
    assistant_id: str,
    include: List[RunStepInclude] | Omit = omit,
    additional_instructions: Optional[str] | Omit = omit,
    additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | Omit = omit,
    instructions: Optional[str] | Omit = omit,
    max_completion_tokens: Optional[int] | Omit = omit,
    max_prompt_tokens: Optional[int] | Omit = omit,
    metadata: Optional[Metadata] | Omit = omit,
    model: Union[str, ChatModel, None] | Omit = omit,
    parallel_tool_calls: bool | Omit = omit,
    reasoning_effort: Optional[ReasoningEffort] | Omit = omit,
    response_format: Optional[AssistantResponseFormatOptionParam] | Omit = omit,
    temperature: Optional[float] | Omit = omit,
    tool_choice: Optional[AssistantToolChoiceOptionParam] | Omit = omit,
    tools: Optional[Iterable[AssistantToolParam]] | Omit = omit,
    top_p: Optional[float] | Omit = omit,
    truncation_strategy: Optional[run_create_params.TruncationStrategy] | Omit = omit,
    poll_interval_ms: int | Omit = omit,
    thread_id: str,
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx2.Timeout | None | NotGiven = NOT_GIVEN,
) -> Run:
    """
    A helper to create a run an poll for a terminal state. More information on Run
    lifecycles can be found here:
    https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps
    """
    run = await self.create(  # pyright: ignore[reportDeprecated]
        thread_id=thread_id,
        assistant_id=assistant_id,
        include=include,
        additional_instructions=additional_instructions,
        additional_messages=additional_messages,
        instructions=instructions,
        max_completion_tokens=max_completion_tokens,
        max_prompt_tokens=max_prompt_tokens,
        metadata=metadata,
        model=model,
        response_format=response_format,
        temperature=temperature,
        tool_choice=tool_choice,
        parallel_tool_calls=parallel_tool_calls,
        reasoning_effort=reasoning_effort,
        # We assume we are not streaming when polling
        stream=False,
        tools=tools,
        truncation_strategy=truncation_strategy,
        top_p=top_p,
        extra_headers=extra_headers,
        extra_query=extra_query,
        extra_body=extra_body,
        timeout=timeout,
    )
    return await self.poll(  # pyright: ignore[reportDeprecated]
        run.id,
        thread_id=thread_id,
        extra_headers=extra_headers,
        extra_query=extra_query,
        extra_body=extra_body,
        poll_interval_ms=poll_interval_ms,
        timeout=timeout,
    )


def async_runs_create_and_stream(
    self: AsyncRuns,
    *,
    assistant_id: str,
    additional_instructions: Optional[str] | Omit = omit,
    additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | Omit = omit,
    instructions: Optional[str] | Omit = omit,
    max_completion_tokens: Optional[int] | Omit = omit,
    max_prompt_tokens: Optional[int] | Omit = omit,
    metadata: Optional[Metadata] | Omit = omit,
    model: Union[str, ChatModel, None] | Omit = omit,
    parallel_tool_calls: bool | Omit = omit,
    response_format: Optional[AssistantResponseFormatOptionParam] | Omit = omit,
    temperature: Optional[float] | Omit = omit,
    tool_choice: Optional[AssistantToolChoiceOptionParam] | Omit = omit,
    tools: Optional[Iterable[AssistantToolParam]] | Omit = omit,
    top_p: Optional[float] | Omit = omit,
    truncation_strategy: Optional[run_create_params.TruncationStrategy] | Omit = omit,
    thread_id: str,
    event_handler: AsyncAssistantEventHandlerT | None = None,
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx2.Timeout | None | NotGiven = NOT_GIVEN,
) -> AsyncAssistantStreamManager[AsyncAssistantEventHandler] | AsyncAssistantStreamManager[AsyncAssistantEventHandlerT]:
    """Create a Run stream"""
    if not thread_id:
        raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")

    extra_headers = {
        "OpenAI-Beta": "assistants=v2",
        "X-Stainless-Stream-Helper": "threads.runs.create_and_stream",
        "X-Stainless-Custom-Event-Handler": "true" if event_handler else "false",
        **(extra_headers or {}),
    }
    request = self._post(
        path_template("/threads/{thread_id}/runs", thread_id=thread_id),
        body=maybe_transform(
            {
                "assistant_id": assistant_id,
                "additional_instructions": additional_instructions,
                "additional_messages": additional_messages,
                "instructions": instructions,
                "max_completion_tokens": max_completion_tokens,
                "max_prompt_tokens": max_prompt_tokens,
                "metadata": metadata,
                "model": model,
                "response_format": response_format,
                "temperature": temperature,
                "tool_choice": tool_choice,
                "stream": True,
                "tools": tools,
                "truncation_strategy": truncation_strategy,
                "top_p": top_p,
                "parallel_tool_calls": parallel_tool_calls,
            },
            run_create_params.RunCreateParams,
        ),
        options=make_request_options(
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            security={"bearer_auth": True},
        ),
        cast_to=Run,
        stream=True,
        stream_cls=AsyncStream[AssistantStreamEvent],
    )
    return AsyncAssistantStreamManager(request, event_handler=event_handler or AsyncAssistantEventHandler())


async def async_runs_poll(
    self: AsyncRuns,
    run_id: str,
    thread_id: str,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    poll_interval_ms: int | Omit = omit,
) -> Run:
    """
    A helper to poll a run status until it reaches a terminal state. More
    information on Run lifecycles can be found here:
    https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps
    """
    extra_headers = {"X-Stainless-Poll-Helper": "true", **(extra_headers or {})}

    if is_given(poll_interval_ms):
        extra_headers["X-Stainless-Custom-Poll-Interval"] = str(poll_interval_ms)

    terminal_states = {"requires_action", "cancelled", "completed", "failed", "expired", "incomplete"}
    while True:
        response = await self.with_raw_response.retrieve(  # pyright: ignore[reportDeprecated]
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

        await self._sleep(poll_interval_ms / 1000)


def async_runs_stream(
    self: AsyncRuns,
    *,
    assistant_id: str,
    include: List[RunStepInclude] | Omit = omit,
    additional_instructions: Optional[str] | Omit = omit,
    additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | Omit = omit,
    instructions: Optional[str] | Omit = omit,
    max_completion_tokens: Optional[int] | Omit = omit,
    max_prompt_tokens: Optional[int] | Omit = omit,
    metadata: Optional[Metadata] | Omit = omit,
    model: Union[str, ChatModel, None] | Omit = omit,
    parallel_tool_calls: bool | Omit = omit,
    reasoning_effort: Optional[ReasoningEffort] | Omit = omit,
    response_format: Optional[AssistantResponseFormatOptionParam] | Omit = omit,
    temperature: Optional[float] | Omit = omit,
    tool_choice: Optional[AssistantToolChoiceOptionParam] | Omit = omit,
    tools: Optional[Iterable[AssistantToolParam]] | Omit = omit,
    top_p: Optional[float] | Omit = omit,
    truncation_strategy: Optional[run_create_params.TruncationStrategy] | Omit = omit,
    thread_id: str,
    event_handler: AsyncAssistantEventHandlerT | None = None,
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx2.Timeout | None | NotGiven = NOT_GIVEN,
) -> AsyncAssistantStreamManager[AsyncAssistantEventHandler] | AsyncAssistantStreamManager[AsyncAssistantEventHandlerT]:
    """Create a Run stream"""
    if not thread_id:
        raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")

    extra_headers = {
        "OpenAI-Beta": "assistants=v2",
        "X-Stainless-Stream-Helper": "threads.runs.create_and_stream",
        "X-Stainless-Custom-Event-Handler": "true" if event_handler else "false",
        **(extra_headers or {}),
    }
    request = self._post(
        path_template("/threads/{thread_id}/runs", thread_id=thread_id),
        body=maybe_transform(
            {
                "assistant_id": assistant_id,
                "additional_instructions": additional_instructions,
                "additional_messages": additional_messages,
                "instructions": instructions,
                "max_completion_tokens": max_completion_tokens,
                "max_prompt_tokens": max_prompt_tokens,
                "metadata": metadata,
                "model": model,
                "response_format": response_format,
                "temperature": temperature,
                "tool_choice": tool_choice,
                "stream": True,
                "tools": tools,
                "parallel_tool_calls": parallel_tool_calls,
                "reasoning_effort": reasoning_effort,
                "truncation_strategy": truncation_strategy,
                "top_p": top_p,
            },
            run_create_params.RunCreateParams,
        ),
        options=make_request_options(
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            query=maybe_transform({"include": include}, run_create_params.RunCreateParams),
            security={"bearer_auth": True},
        ),
        cast_to=Run,
        stream=True,
        stream_cls=AsyncStream[AssistantStreamEvent],
    )
    return AsyncAssistantStreamManager(request, event_handler=event_handler or AsyncAssistantEventHandler())


async def async_runs_submit_tool_outputs_and_poll(
    self: AsyncRuns,
    *,
    tool_outputs: Iterable[run_submit_tool_outputs_params.ToolOutput],
    run_id: str,
    thread_id: str,
    poll_interval_ms: int | Omit = omit,
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx2.Timeout | None | NotGiven = NOT_GIVEN,
) -> Run:
    """
    A helper to submit a tool output to a run and poll for a terminal run state.
    More information on Run lifecycles can be found here:
    https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps
    """
    run = await self.submit_tool_outputs(  # pyright: ignore[reportDeprecated]
        run_id=run_id,
        thread_id=thread_id,
        tool_outputs=tool_outputs,
        stream=False,
        extra_headers=extra_headers,
        extra_query=extra_query,
        extra_body=extra_body,
        timeout=timeout,
    )
    return await self.poll(  # pyright: ignore[reportDeprecated]
        run_id=run.id,
        thread_id=thread_id,
        extra_headers=extra_headers,
        extra_query=extra_query,
        extra_body=extra_body,
        timeout=timeout,
        poll_interval_ms=poll_interval_ms,
    )


def async_runs_submit_tool_outputs_stream(
    self: AsyncRuns,
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
    timeout: float | httpx2.Timeout | None | NotGiven = NOT_GIVEN,
) -> AsyncAssistantStreamManager[AsyncAssistantEventHandler] | AsyncAssistantStreamManager[AsyncAssistantEventHandlerT]:
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
        "OpenAI-Beta": "assistants=v2",
        "X-Stainless-Stream-Helper": "threads.runs.submit_tool_outputs_stream",
        "X-Stainless-Custom-Event-Handler": "true" if event_handler else "false",
        **(extra_headers or {}),
    }
    request = self._post(
        path_template("/threads/{thread_id}/runs/{run_id}/submit_tool_outputs", thread_id=thread_id, run_id=run_id),
        body=maybe_transform(
            {
                "tool_outputs": tool_outputs,
                "stream": True,
            },
            run_submit_tool_outputs_params.RunSubmitToolOutputsParams,
        ),
        options=make_request_options(
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            security={"bearer_auth": True},
        ),
        cast_to=Run,
        stream=True,
        stream_cls=AsyncStream[AssistantStreamEvent],
    )
    return AsyncAssistantStreamManager(request, event_handler=event_handler or AsyncAssistantEventHandler())
