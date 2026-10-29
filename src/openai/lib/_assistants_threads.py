"""Handwritten Assistants helper behavior behind generated public facades."""

from __future__ import annotations

from typing import TYPE_CHECKING, Union, Iterable, Optional
from functools import partial

import httpx2

from openai._types import NOT_GIVEN, Body, Omit, Query, Headers, NotGiven, omit
from openai._utils import maybe_transform
from openai._streaming import Stream, AsyncStream
from openai.types.beta import thread_create_and_run_params
from openai._base_client import make_request_options
from openai.lib.streaming import (
    AssistantEventHandler,
    AssistantEventHandlerT,
    AssistantStreamManager,
    AsyncAssistantEventHandler,
    AsyncAssistantEventHandlerT,
    AsyncAssistantStreamManager,
)
from openai.types.beta.threads.run import Run
from openai.types.shared.chat_model import ChatModel
from openai.types.shared_params.metadata import Metadata
from openai.types.beta.assistant_tool_param import AssistantToolParam
from openai.types.beta.assistant_stream_event import AssistantStreamEvent
from openai.types.beta.assistant_tool_choice_option_param import AssistantToolChoiceOptionParam
from openai.types.beta.assistant_response_format_option_param import AssistantResponseFormatOptionParam

if TYPE_CHECKING:
    from openai.resources.beta.threads.threads import Threads, AsyncThreads


def threads_create_and_run_poll(
    self: Threads,
    *,
    assistant_id: str,
    instructions: Optional[str] | Omit = omit,
    max_completion_tokens: Optional[int] | Omit = omit,
    max_prompt_tokens: Optional[int] | Omit = omit,
    metadata: Optional[Metadata] | Omit = omit,
    model: Union[str, ChatModel, None] | Omit = omit,
    parallel_tool_calls: bool | Omit = omit,
    response_format: Optional[AssistantResponseFormatOptionParam] | Omit = omit,
    temperature: Optional[float] | Omit = omit,
    thread: thread_create_and_run_params.Thread | Omit = omit,
    tool_choice: Optional[AssistantToolChoiceOptionParam] | Omit = omit,
    tool_resources: Optional[thread_create_and_run_params.ToolResources] | Omit = omit,
    tools: Optional[Iterable[AssistantToolParam]] | Omit = omit,
    top_p: Optional[float] | Omit = omit,
    truncation_strategy: Optional[thread_create_and_run_params.TruncationStrategy] | Omit = omit,
    poll_interval_ms: int | Omit = omit,
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx2.Timeout | None | NotGiven = NOT_GIVEN,
) -> Run:
    """
    A helper to create a thread, start a run and then poll for a terminal state.
    More information on Run lifecycles can be found here:
    https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps
    """
    run = self.create_and_run(
        assistant_id=assistant_id,
        instructions=instructions,
        max_completion_tokens=max_completion_tokens,
        max_prompt_tokens=max_prompt_tokens,
        metadata=metadata,
        model=model,
        parallel_tool_calls=parallel_tool_calls,
        response_format=response_format,
        temperature=temperature,
        stream=False,
        thread=thread,
        tool_resources=tool_resources,
        tool_choice=tool_choice,
        truncation_strategy=truncation_strategy,
        top_p=top_p,
        tools=tools,
        extra_headers=extra_headers,
        extra_query=extra_query,
        extra_body=extra_body,
        timeout=timeout,
    )
    return self.runs.poll(run.id, run.thread_id, extra_headers, extra_query, extra_body, timeout, poll_interval_ms)


def threads_create_and_run_stream(
    self: Threads,
    *,
    assistant_id: str,
    instructions: Optional[str] | Omit = omit,
    max_completion_tokens: Optional[int] | Omit = omit,
    max_prompt_tokens: Optional[int] | Omit = omit,
    metadata: Optional[Metadata] | Omit = omit,
    model: Union[str, ChatModel, None] | Omit = omit,
    parallel_tool_calls: bool | Omit = omit,
    response_format: Optional[AssistantResponseFormatOptionParam] | Omit = omit,
    temperature: Optional[float] | Omit = omit,
    thread: thread_create_and_run_params.Thread | Omit = omit,
    tool_choice: Optional[AssistantToolChoiceOptionParam] | Omit = omit,
    tool_resources: Optional[thread_create_and_run_params.ToolResources] | Omit = omit,
    tools: Optional[Iterable[AssistantToolParam]] | Omit = omit,
    top_p: Optional[float] | Omit = omit,
    truncation_strategy: Optional[thread_create_and_run_params.TruncationStrategy] | Omit = omit,
    event_handler: AssistantEventHandlerT | None = None,
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx2.Timeout | None | NotGiven = NOT_GIVEN,
) -> AssistantStreamManager[AssistantEventHandler] | AssistantStreamManager[AssistantEventHandlerT]:
    """Create a thread and stream the run back"""
    extra_headers = {
        "OpenAI-Beta": "assistants=v2",
        "X-Stainless-Stream-Helper": "threads.create_and_run_stream",
        "X-Stainless-Custom-Event-Handler": "true" if event_handler else "false",
        **(extra_headers or {}),
    }
    make_request = partial(
        self._post,
        "/threads/runs",
        body=maybe_transform(
            {
                "assistant_id": assistant_id,
                "instructions": instructions,
                "max_completion_tokens": max_completion_tokens,
                "max_prompt_tokens": max_prompt_tokens,
                "metadata": metadata,
                "model": model,
                "parallel_tool_calls": parallel_tool_calls,
                "response_format": response_format,
                "temperature": temperature,
                "tool_choice": tool_choice,
                "stream": True,
                "thread": thread,
                "tools": tools,
                "tool_resources": tool_resources,
                "truncation_strategy": truncation_strategy,
                "top_p": top_p,
            },
            thread_create_and_run_params.ThreadCreateAndRunParams,
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


async def async_threads_create_and_run_poll(
    self: AsyncThreads,
    *,
    assistant_id: str,
    instructions: Optional[str] | Omit = omit,
    max_completion_tokens: Optional[int] | Omit = omit,
    max_prompt_tokens: Optional[int] | Omit = omit,
    metadata: Optional[Metadata] | Omit = omit,
    model: Union[str, ChatModel, None] | Omit = omit,
    parallel_tool_calls: bool | Omit = omit,
    response_format: Optional[AssistantResponseFormatOptionParam] | Omit = omit,
    temperature: Optional[float] | Omit = omit,
    thread: thread_create_and_run_params.Thread | Omit = omit,
    tool_choice: Optional[AssistantToolChoiceOptionParam] | Omit = omit,
    tool_resources: Optional[thread_create_and_run_params.ToolResources] | Omit = omit,
    tools: Optional[Iterable[AssistantToolParam]] | Omit = omit,
    top_p: Optional[float] | Omit = omit,
    truncation_strategy: Optional[thread_create_and_run_params.TruncationStrategy] | Omit = omit,
    poll_interval_ms: int | Omit = omit,
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx2.Timeout | None | NotGiven = NOT_GIVEN,
) -> Run:
    """
    A helper to create a thread, start a run and then poll for a terminal state.
    More information on Run lifecycles can be found here:
    https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps
    """
    run = await self.create_and_run(
        assistant_id=assistant_id,
        instructions=instructions,
        max_completion_tokens=max_completion_tokens,
        max_prompt_tokens=max_prompt_tokens,
        metadata=metadata,
        model=model,
        parallel_tool_calls=parallel_tool_calls,
        response_format=response_format,
        temperature=temperature,
        stream=False,
        thread=thread,
        tool_resources=tool_resources,
        tool_choice=tool_choice,
        truncation_strategy=truncation_strategy,
        top_p=top_p,
        tools=tools,
        extra_headers=extra_headers,
        extra_query=extra_query,
        extra_body=extra_body,
        timeout=timeout,
    )
    return await self.runs.poll(
        run.id, run.thread_id, extra_headers, extra_query, extra_body, timeout, poll_interval_ms
    )


def async_threads_create_and_run_stream(
    self: AsyncThreads,
    *,
    assistant_id: str,
    instructions: Optional[str] | Omit = omit,
    max_completion_tokens: Optional[int] | Omit = omit,
    max_prompt_tokens: Optional[int] | Omit = omit,
    metadata: Optional[Metadata] | Omit = omit,
    model: Union[str, ChatModel, None] | Omit = omit,
    parallel_tool_calls: bool | Omit = omit,
    response_format: Optional[AssistantResponseFormatOptionParam] | Omit = omit,
    temperature: Optional[float] | Omit = omit,
    thread: thread_create_and_run_params.Thread | Omit = omit,
    tool_choice: Optional[AssistantToolChoiceOptionParam] | Omit = omit,
    tool_resources: Optional[thread_create_and_run_params.ToolResources] | Omit = omit,
    tools: Optional[Iterable[AssistantToolParam]] | Omit = omit,
    top_p: Optional[float] | Omit = omit,
    truncation_strategy: Optional[thread_create_and_run_params.TruncationStrategy] | Omit = omit,
    event_handler: AsyncAssistantEventHandlerT | None = None,
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx2.Timeout | None | NotGiven = NOT_GIVEN,
) -> AsyncAssistantStreamManager[AsyncAssistantEventHandler] | AsyncAssistantStreamManager[AsyncAssistantEventHandlerT]:
    """Create a thread and stream the run back"""
    extra_headers = {
        "OpenAI-Beta": "assistants=v2",
        "X-Stainless-Stream-Helper": "threads.create_and_run_stream",
        "X-Stainless-Custom-Event-Handler": "true" if event_handler else "false",
        **(extra_headers or {}),
    }
    request = self._post(
        "/threads/runs",
        body=maybe_transform(
            {
                "assistant_id": assistant_id,
                "instructions": instructions,
                "max_completion_tokens": max_completion_tokens,
                "max_prompt_tokens": max_prompt_tokens,
                "metadata": metadata,
                "model": model,
                "parallel_tool_calls": parallel_tool_calls,
                "response_format": response_format,
                "temperature": temperature,
                "tool_choice": tool_choice,
                "stream": True,
                "thread": thread,
                "tools": tools,
                "tool_resources": tool_resources,
                "truncation_strategy": truncation_strategy,
                "top_p": top_p,
            },
            thread_create_and_run_params.ThreadCreateAndRunParams,
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
