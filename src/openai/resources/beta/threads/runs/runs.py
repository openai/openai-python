# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import typing_extensions
from typing import List, Union, Iterable, Optional
from functools import partial
from typing_extensions import Literal, overload

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
from ....._base_client import AsyncPaginator, make_request_options
from .....lib.streaming import (
    AssistantEventHandler,
    AssistantEventHandlerT,
    AssistantStreamManager,
    AsyncAssistantEventHandler,
    AsyncAssistantEventHandlerT,
    AsyncAssistantStreamManager,
)
from .....types.chat_model import ChatModel
from .....types.beta.threads import (
    run_list_params,
    run_create_params,
    run_update_params,
    run_submit_tool_outputs_params,
)
from .....types.beta.threads.run import Run
from .....types.beta.assistant_tool_param import AssistantToolParam
from .....types.beta.assistant_stream_event import AssistantStreamEvent
from .....types.beta.threads.runs.run_step_include import RunStepInclude
from .....types.beta.assistant_tool_choice_option_param import AssistantToolChoiceOptionParam
from .....types.beta.assistant_response_format_option_param import AssistantResponseFormatOptionParam

__all__ = ["Runs", "AsyncRuns"]


class Runs(SyncAPIResource):
    @cached_property
    def steps(self) -> Steps:
        return Steps(self._client)

    @cached_property
    def with_raw_response(self) -> RunsWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return RunsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RunsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return RunsWithStreamingResponse(self)

    @overload
    def create(
        self,
        thread_id: str,
        *,
        assistant_id: str,
        include: List[RunStepInclude] | NotGiven = NOT_GIVEN,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        stream: Optional[Literal[False]] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[run_create_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
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

          include: A list of additional fields to include in the response. Currently the only
              supported value is `step_details.tool_calls[*].file_search.results[*].content`
              to fetch the file search result content.

              See the
              [file search tool documentation](https://platform.openai.com/docs/assistants/tools/file-search#customizing-file-search-settings)
              for more information.

          additional_instructions: Appends additional instructions at the end of the instructions for the run. This
              is useful for modifying the behavior on a per-run basis without overriding other
              instructions.

          additional_messages: Adds additional messages to the thread before creating the run.

          instructions: Overrides the
              [instructions](https://platform.openai.com/docs/api-reference/assistants/createAssistant)
              of the assistant. This is useful for modifying the behavior on a per-run basis.

          max_completion_tokens: The maximum number of completion tokens that may be used over the course of the
              run. The run will make a best effort to use only the number of completion tokens
              specified, across multiple turns of the run. If the run exceeds the number of
              completion tokens specified, the run will end with status `incomplete`. See
              `incomplete_details` for more info.

          max_prompt_tokens: The maximum number of prompt tokens that may be used over the course of the run.
              The run will make a best effort to use only the number of prompt tokens
              specified, across multiple turns of the run. If the run exceeds the number of
              prompt tokens specified, the run will end with status `incomplete`. See
              `incomplete_details` for more info.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format. Keys
              can be a maximum of 64 characters long and values can be a maximum of 512
              characters long.

          model: The ID of the [Model](https://platform.openai.com/docs/api-reference/models) to
              be used to execute this run. If a value is provided here, it will override the
              model associated with the assistant. If not, the model associated with the
              assistant will be used.

          parallel_tool_calls: Whether to enable
              [parallel function calling](https://platform.openai.com/docs/guides/function-calling#configuring-parallel-function-calling)
              during tool use.

          response_format: Specifies the format that the model must output. Compatible with
              [GPT-4o](https://platform.openai.com/docs/models#gpt-4o),
              [GPT-4 Turbo](https://platform.openai.com/docs/models#gpt-4-turbo-and-gpt-4),
              and all GPT-3.5 Turbo models since `gpt-3.5-turbo-1106`.

              Setting to `{ "type": "json_schema", "json_schema": {...} }` enables Structured
              Outputs which ensures the model will match your supplied JSON schema. Learn more
              in the
              [Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs).

              Setting to `{ "type": "json_object" }` enables JSON mode, which ensures the
              message the model generates is valid JSON.

              **Important:** when using JSON mode, you **must** also instruct the model to
              produce JSON yourself via a system or user message. Without this, the model may
              generate an unending stream of whitespace until the generation reaches the token
              limit, resulting in a long-running and seemingly "stuck" request. Also note that
              the message content may be partially cut off if `finish_reason="length"`, which
              indicates the generation exceeded `max_tokens` or the conversation exceeded the
              max context length.

          stream: If `true`, returns a stream of events that happen during the Run as server-sent
              events, terminating when the Run enters a terminal state with a `data: [DONE]`
              message.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic.

          tool_choice: Controls which (if any) tool is called by the model. `none` means the model will
              not call any tools and instead generates a message. `auto` is the default value
              and means the model can pick between generating a message or calling one or more
              tools. `required` means the model must call one or more tools before responding
              to the user. Specifying a particular tool like `{"type": "file_search"}` or
              `{"type": "function", "function": {"name": "my_function"}}` forces the model to
              call that tool.

          tools: Override the tools the assistant can use for this run. This is useful for
              modifying the behavior on a per-run basis.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or temperature but not both.

          truncation_strategy: Controls for how a thread will be truncated prior to the run. Use this to
              control the intial context window of the run.

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
        include: List[RunStepInclude] | NotGiven = NOT_GIVEN,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[run_create_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
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

          include: A list of additional fields to include in the response. Currently the only
              supported value is `step_details.tool_calls[*].file_search.results[*].content`
              to fetch the file search result content.

              See the
              [file search tool documentation](https://platform.openai.com/docs/assistants/tools/file-search#customizing-file-search-settings)
              for more information.

          additional_instructions: Appends additional instructions at the end of the instructions for the run. This
              is useful for modifying the behavior on a per-run basis without overriding other
              instructions.

          additional_messages: Adds additional messages to the thread before creating the run.

          instructions: Overrides the
              [instructions](https://platform.openai.com/docs/api-reference/assistants/createAssistant)
              of the assistant. This is useful for modifying the behavior on a per-run basis.

          max_completion_tokens: The maximum number of completion tokens that may be used over the course of the
              run. The run will make a best effort to use only the number of completion tokens
              specified, across multiple turns of the run. If the run exceeds the number of
              completion tokens specified, the run will end with status `incomplete`. See
              `incomplete_details` for more info.

          max_prompt_tokens: The maximum number of prompt tokens that may be used over the course of the run.
              The run will make a best effort to use only the number of prompt tokens
              specified, across multiple turns of the run. If the run exceeds the number of
              prompt tokens specified, the run will end with status `incomplete`. See
              `incomplete_details` for more info.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format. Keys
              can be a maximum of 64 characters long and values can be a maximum of 512
              characters long.

          model: The ID of the [Model](https://platform.openai.com/docs/api-reference/models) to
              be used to execute this run. If a value is provided here, it will override the
              model associated with the assistant. If not, the model associated with the
              assistant will be used.

          parallel_tool_calls: Whether to enable
              [parallel function calling](https://platform.openai.com/docs/guides/function-calling#configuring-parallel-function-calling)
              during tool use.

          response_format: Specifies the format that the model must output. Compatible with
              [GPT-4o](https://platform.openai.com/docs/models#gpt-4o),
              [GPT-4 Turbo](https://platform.openai.com/docs/models#gpt-4-turbo-and-gpt-4),
              and all GPT-3.5 Turbo models since `gpt-3.5-turbo-1106`.

              Setting to `{ "type": "json_schema", "json_schema": {...} }` enables Structured
              Outputs which ensures the model will match your supplied JSON schema. Learn more
              in the
              [Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs).

              Setting to `{ "type": "json_object" }` enables JSON mode, which ensures the
              message the model generates is valid JSON.

              **Important:** when using JSON mode, you **must** also instruct the model to
              produce JSON yourself via a system or user message. Without this, the model may
              generate an unending stream of whitespace until the generation reaches the token
              limit, resulting in a long-running and seemingly "stuck" request. Also note that
              the message content may be partially cut off if `finish_reason="length"`, which
              indicates the generation exceeded `max_tokens` or the conversation exceeded the
              max context length.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic.

          tool_choice: Controls which (if any) tool is called by the model. `none` means the model will
              not call any tools and instead generates a message. `auto` is the default value
              and means the model can pick between generating a message or calling one or more
              tools. `required` means the model must call one or more tools before responding
              to the user. Specifying a particular tool like `{"type": "file_search"}` or
              `{"type": "function", "function": {"name": "my_function"}}` forces the model to
              call that tool.

          tools: Override the tools the assistant can use for this run. This is useful for
              modifying the behavior on a per-run basis.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or temperature but not both.

          truncation_strategy: Controls for how a thread will be truncated prior to the run. Use this to
              control the intial context window of the run.

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
        include: List[RunStepInclude] | NotGiven = NOT_GIVEN,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[run_create_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
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

          include: A list of additional fields to include in the response. Currently the only
              supported value is `step_details.tool_calls[*].file_search.results[*].content`
              to fetch the file search result content.

              See the
              [file search tool documentation](https://platform.openai.com/docs/assistants/tools/file-search#customizing-file-search-settings)
              for more information.

          additional_instructions: Appends additional instructions at the end of the instructions for the run. This
              is useful for modifying the behavior on a per-run basis without overriding other
              instructions.

          additional_messages: Adds additional messages to the thread before creating the run.

          instructions: Overrides the
              [instructions](https://platform.openai.com/docs/api-reference/assistants/createAssistant)
              of the assistant. This is useful for modifying the behavior on a per-run basis.

          max_completion_tokens: The maximum number of completion tokens that may be used over the course of the
              run. The run will make a best effort to use only the number of completion tokens
              specified, across multiple turns of the run. If the run exceeds the number of
              completion tokens specified, the run will end with status `incomplete`. See
              `incomplete_details` for more info.

          max_prompt_tokens: The maximum number of prompt tokens that may be used over the course of the run.
              The run will make a best effort to use only the number of prompt tokens
              specified, across multiple turns of the run. If the run exceeds the number of
              prompt tokens specified, the run will end with status `incomplete`. See
              `incomplete_details` for more info.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format. Keys
              can be a maximum of 64 characters long and values can be a maximum of 512
              characters long.

          model: The ID of the [Model](https://platform.openai.com/docs/api-reference/models) to
              be used to execute this run. If a value is provided here, it will override the
              model associated with the assistant. If not, the model associated with the
              assistant will be used.

          parallel_tool_calls: Whether to enable
              [parallel function calling](https://platform.openai.com/docs/guides/function-calling#configuring-parallel-function-calling)
              during tool use.

          response_format: Specifies the format that the model must output. Compatible with
              [GPT-4o](https://platform.openai.com/docs/models#gpt-4o),
              [GPT-4 Turbo](https://platform.openai.com/docs/models#gpt-4-turbo-and-gpt-4),
              and all GPT-3.5 Turbo models since `gpt-3.5-turbo-1106`.

              Setting to `{ "type": "json_schema", "json_schema": {...} }` enables Structured
              Outputs which ensures the model will match your supplied JSON schema. Learn more
              in the
              [Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs).

              Setting to `{ "type": "json_object" }` enables JSON mode, which ensures the
              message the model generates is valid JSON.

              **Important:** when using JSON mode, you **must** also instruct the model to
              produce JSON yourself via a system or user message. Without this, the model may
              generate an unending stream of whitespace until the generation reaches the token
              limit, resulting in a long-running and seemingly "stuck" request. Also note that
              the message content may be partially cut off if `finish_reason="length"`, which
              indicates the generation exceeded `max_tokens` or the conversation exceeded the
              max context length.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic.

          tool_choice: Controls which (if any) tool is called by the model. `none` means the model will
              not call any tools and instead generates a message. `auto` is the default value
              and means the model can pick between generating a message or calling one or more
              tools. `required` means the model must call one or more tools before responding
              to the user. Specifying a particular tool like `{"type": "file_search"}` or
              `{"type": "function", "function": {"name": "my_function"}}` forces the model to
              call that tool.

          tools: Override the tools the assistant can use for this run. This is useful for
              modifying the behavior on a per-run basis.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or temperature but not both.

          truncation_strategy: Controls for how a thread will be truncated prior to the run. Use this to
              control the intial context window of the run.

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
        include: List[RunStepInclude] | NotGiven = NOT_GIVEN,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[run_create_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run | Stream[AssistantStreamEvent]:
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return self._post(
            f"/threads/{thread_id}/runs",
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
                    "parallel_tool_calls": parallel_tool_calls,
                    "response_format": response_format,
                    "stream": stream,
                    "temperature": temperature,
                    "tool_choice": tool_choice,
                    "tools": tools,
                    "top_p": top_p,
                    "truncation_strategy": truncation_strategy,
                },
                run_create_params.RunCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"include": include}, run_create_params.RunCreateParams),
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
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
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
              can be a maximum of 64 characters long and values can be a maximum of 512
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
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
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
              starting with obj_foo, your subsequent call can include before=obj_foo in order
              to fetch the previous page of the list.

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
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
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
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
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
        include: List[RunStepInclude] | NotGiven = NOT_GIVEN,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[run_create_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
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
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[run_create_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
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
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[run_create_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
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
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[run_create_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
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
            "OpenAI-Beta": "assistants=v2",
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
                    "top_p": top_p,
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

        terminal_states = {"requires_action", "cancelled", "completed", "failed", "expired", "incomplete"}
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

            self._sleep(poll_interval_ms / 1000)

    @overload
    def stream(
        self,
        *,
        assistant_id: str,
        include: List[RunStepInclude] | NotGiven = NOT_GIVEN,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[run_create_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
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
        include: List[RunStepInclude] | NotGiven = NOT_GIVEN,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[run_create_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
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
        include: List[RunStepInclude] | NotGiven = NOT_GIVEN,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[run_create_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
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
            "OpenAI-Beta": "assistants=v2",
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
                    "include": include,
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
                    "truncation_strategy": truncation_strategy,
                    "top_p": top_p,
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
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
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
            "OpenAI-Beta": "assistants=v2",
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
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRunsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRunsWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncRunsWithStreamingResponse(self)

    @overload
    async def create(
        self,
        thread_id: str,
        *,
        assistant_id: str,
        include: List[RunStepInclude] | NotGiven = NOT_GIVEN,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        stream: Optional[Literal[False]] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[run_create_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
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

          include: A list of additional fields to include in the response. Currently the only
              supported value is `step_details.tool_calls[*].file_search.results[*].content`
              to fetch the file search result content.

              See the
              [file search tool documentation](https://platform.openai.com/docs/assistants/tools/file-search#customizing-file-search-settings)
              for more information.

          additional_instructions: Appends additional instructions at the end of the instructions for the run. This
              is useful for modifying the behavior on a per-run basis without overriding other
              instructions.

          additional_messages: Adds additional messages to the thread before creating the run.

          instructions: Overrides the
              [instructions](https://platform.openai.com/docs/api-reference/assistants/createAssistant)
              of the assistant. This is useful for modifying the behavior on a per-run basis.

          max_completion_tokens: The maximum number of completion tokens that may be used over the course of the
              run. The run will make a best effort to use only the number of completion tokens
              specified, across multiple turns of the run. If the run exceeds the number of
              completion tokens specified, the run will end with status `incomplete`. See
              `incomplete_details` for more info.

          max_prompt_tokens: The maximum number of prompt tokens that may be used over the course of the run.
              The run will make a best effort to use only the number of prompt tokens
              specified, across multiple turns of the run. If the run exceeds the number of
              prompt tokens specified, the run will end with status `incomplete`. See
              `incomplete_details` for more info.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format. Keys
              can be a maximum of 64 characters long and values can be a maximum of 512
              characters long.

          model: The ID of the [Model](https://platform.openai.com/docs/api-reference/models) to
              be used to execute this run. If a value is provided here, it will override the
              model associated with the assistant. If not, the model associated with the
              assistant will be used.

          parallel_tool_calls: Whether to enable
              [parallel function calling](https://platform.openai.com/docs/guides/function-calling#configuring-parallel-function-calling)
              during tool use.

          response_format: Specifies the format that the model must output. Compatible with
              [GPT-4o](https://platform.openai.com/docs/models#gpt-4o),
              [GPT-4 Turbo](https://platform.openai.com/docs/models#gpt-4-turbo-and-gpt-4),
              and all GPT-3.5 Turbo models since `gpt-3.5-turbo-1106`.

              Setting to `{ "type": "json_schema", "json_schema": {...} }` enables Structured
              Outputs which ensures the model will match your supplied JSON schema. Learn more
              in the
              [Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs).

              Setting to `{ "type": "json_object" }` enables JSON mode, which ensures the
              message the model generates is valid JSON.

              **Important:** when using JSON mode, you **must** also instruct the model to
              produce JSON yourself via a system or user message. Without this, the model may
              generate an unending stream of whitespace until the generation reaches the token
              limit, resulting in a long-running and seemingly "stuck" request. Also note that
              the message content may be partially cut off if `finish_reason="length"`, which
              indicates the generation exceeded `max_tokens` or the conversation exceeded the
              max context length.

          stream: If `true`, returns a stream of events that happen during the Run as server-sent
              events, terminating when the Run enters a terminal state with a `data: [DONE]`
              message.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic.

          tool_choice: Controls which (if any) tool is called by the model. `none` means the model will
              not call any tools and instead generates a message. `auto` is the default value
              and means the model can pick between generating a message or calling one or more
              tools. `required` means the model must call one or more tools before responding
              to the user. Specifying a particular tool like `{"type": "file_search"}` or
              `{"type": "function", "function": {"name": "my_function"}}` forces the model to
              call that tool.

          tools: Override the tools the assistant can use for this run. This is useful for
              modifying the behavior on a per-run basis.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or temperature but not both.

          truncation_strategy: Controls for how a thread will be truncated prior to the run. Use this to
              control the intial context window of the run.

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
        include: List[RunStepInclude] | NotGiven = NOT_GIVEN,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[run_create_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
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

          include: A list of additional fields to include in the response. Currently the only
              supported value is `step_details.tool_calls[*].file_search.results[*].content`
              to fetch the file search result content.

              See the
              [file search tool documentation](https://platform.openai.com/docs/assistants/tools/file-search#customizing-file-search-settings)
              for more information.

          additional_instructions: Appends additional instructions at the end of the instructions for the run. This
              is useful for modifying the behavior on a per-run basis without overriding other
              instructions.

          additional_messages: Adds additional messages to the thread before creating the run.

          instructions: Overrides the
              [instructions](https://platform.openai.com/docs/api-reference/assistants/createAssistant)
              of the assistant. This is useful for modifying the behavior on a per-run basis.

          max_completion_tokens: The maximum number of completion tokens that may be used over the course of the
              run. The run will make a best effort to use only the number of completion tokens
              specified, across multiple turns of the run. If the run exceeds the number of
              completion tokens specified, the run will end with status `incomplete`. See
              `incomplete_details` for more info.

          max_prompt_tokens: The maximum number of prompt tokens that may be used over the course of the run.
              The run will make a best effort to use only the number of prompt tokens
              specified, across multiple turns of the run. If the run exceeds the number of
              prompt tokens specified, the run will end with status `incomplete`. See
              `incomplete_details` for more info.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format. Keys
              can be a maximum of 64 characters long and values can be a maximum of 512
              characters long.

          model: The ID of the [Model](https://platform.openai.com/docs/api-reference/models) to
              be used to execute this run. If a value is provided here, it will override the
              model associated with the assistant. If not, the model associated with the
              assistant will be used.

          parallel_tool_calls: Whether to enable
              [parallel function calling](https://platform.openai.com/docs/guides/function-calling#configuring-parallel-function-calling)
              during tool use.

          response_format: Specifies the format that the model must output. Compatible with
              [GPT-4o](https://platform.openai.com/docs/models#gpt-4o),
              [GPT-4 Turbo](https://platform.openai.com/docs/models#gpt-4-turbo-and-gpt-4),
              and all GPT-3.5 Turbo models since `gpt-3.5-turbo-1106`.

              Setting to `{ "type": "json_schema", "json_schema": {...} }` enables Structured
              Outputs which ensures the model will match your supplied JSON schema. Learn more
              in the
              [Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs).

              Setting to `{ "type": "json_object" }` enables JSON mode, which ensures the
              message the model generates is valid JSON.

              **Important:** when using JSON mode, you **must** also instruct the model to
              produce JSON yourself via a system or user message. Without this, the model may
              generate an unending stream of whitespace until the generation reaches the token
              limit, resulting in a long-running and seemingly "stuck" request. Also note that
              the message content may be partially cut off if `finish_reason="length"`, which
              indicates the generation exceeded `max_tokens` or the conversation exceeded the
              max context length.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic.

          tool_choice: Controls which (if any) tool is called by the model. `none` means the model will
              not call any tools and instead generates a message. `auto` is the default value
              and means the model can pick between generating a message or calling one or more
              tools. `required` means the model must call one or more tools before responding
              to the user. Specifying a particular tool like `{"type": "file_search"}` or
              `{"type": "function", "function": {"name": "my_function"}}` forces the model to
              call that tool.

          tools: Override the tools the assistant can use for this run. This is useful for
              modifying the behavior on a per-run basis.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or temperature but not both.

          truncation_strategy: Controls for how a thread will be truncated prior to the run. Use this to
              control the intial context window of the run.

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
        include: List[RunStepInclude] | NotGiven = NOT_GIVEN,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[run_create_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
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

          include: A list of additional fields to include in the response. Currently the only
              supported value is `step_details.tool_calls[*].file_search.results[*].content`
              to fetch the file search result content.

              See the
              [file search tool documentation](https://platform.openai.com/docs/assistants/tools/file-search#customizing-file-search-settings)
              for more information.

          additional_instructions: Appends additional instructions at the end of the instructions for the run. This
              is useful for modifying the behavior on a per-run basis without overriding other
              instructions.

          additional_messages: Adds additional messages to the thread before creating the run.

          instructions: Overrides the
              [instructions](https://platform.openai.com/docs/api-reference/assistants/createAssistant)
              of the assistant. This is useful for modifying the behavior on a per-run basis.

          max_completion_tokens: The maximum number of completion tokens that may be used over the course of the
              run. The run will make a best effort to use only the number of completion tokens
              specified, across multiple turns of the run. If the run exceeds the number of
              completion tokens specified, the run will end with status `incomplete`. See
              `incomplete_details` for more info.

          max_prompt_tokens: The maximum number of prompt tokens that may be used over the course of the run.
              The run will make a best effort to use only the number of prompt tokens
              specified, across multiple turns of the run. If the run exceeds the number of
              prompt tokens specified, the run will end with status `incomplete`. See
              `incomplete_details` for more info.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format. Keys
              can be a maximum of 64 characters long and values can be a maximum of 512
              characters long.

          model: The ID of the [Model](https://platform.openai.com/docs/api-reference/models) to
              be used to execute this run. If a value is provided here, it will override the
              model associated with the assistant. If not, the model associated with the
              assistant will be used.

          parallel_tool_calls: Whether to enable
              [parallel function calling](https://platform.openai.com/docs/guides/function-calling#configuring-parallel-function-calling)
              during tool use.

          response_format: Specifies the format that the model must output. Compatible with
              [GPT-4o](https://platform.openai.com/docs/models#gpt-4o),
              [GPT-4 Turbo](https://platform.openai.com/docs/models#gpt-4-turbo-and-gpt-4),
              and all GPT-3.5 Turbo models since `gpt-3.5-turbo-1106`.

              Setting to `{ "type": "json_schema", "json_schema": {...} }` enables Structured
              Outputs which ensures the model will match your supplied JSON schema. Learn more
              in the
              [Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs).

              Setting to `{ "type": "json_object" }` enables JSON mode, which ensures the
              message the model generates is valid JSON.

              **Important:** when using JSON mode, you **must** also instruct the model to
              produce JSON yourself via a system or user message. Without this, the model may
              generate an unending stream of whitespace until the generation reaches the token
              limit, resulting in a long-running and seemingly "stuck" request. Also note that
              the message content may be partially cut off if `finish_reason="length"`, which
              indicates the generation exceeded `max_tokens` or the conversation exceeded the
              max context length.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic.

          tool_choice: Controls which (if any) tool is called by the model. `none` means the model will
              not call any tools and instead generates a message. `auto` is the default value
              and means the model can pick between generating a message or calling one or more
              tools. `required` means the model must call one or more tools before responding
              to the user. Specifying a particular tool like `{"type": "file_search"}` or
              `{"type": "function", "function": {"name": "my_function"}}` forces the model to
              call that tool.

          tools: Override the tools the assistant can use for this run. This is useful for
              modifying the behavior on a per-run basis.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or temperature but not both.

          truncation_strategy: Controls for how a thread will be truncated prior to the run. Use this to
              control the intial context window of the run.

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
        include: List[RunStepInclude] | NotGiven = NOT_GIVEN,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[run_create_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run | AsyncStream[AssistantStreamEvent]:
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return await self._post(
            f"/threads/{thread_id}/runs",
            body=await async_maybe_transform(
                {
                    "assistant_id": assistant_id,
                    "include": include,
                    "additional_instructions": additional_instructions,
                    "additional_messages": additional_messages,
                    "instructions": instructions,
                    "max_completion_tokens": max_completion_tokens,
                    "max_prompt_tokens": max_prompt_tokens,
                    "metadata": metadata,
                    "model": model,
                    "parallel_tool_calls": parallel_tool_calls,
                    "response_format": response_format,
                    "stream": stream,
                    "temperature": temperature,
                    "tool_choice": tool_choice,
                    "tools": tools,
                    "top_p": top_p,
                    "truncation_strategy": truncation_strategy,
                },
                run_create_params.RunCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"include": include}, run_create_params.RunCreateParams),
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
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
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
              can be a maximum of 64 characters long and values can be a maximum of 512
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
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
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
              starting with obj_foo, your subsequent call can include before=obj_foo in order
              to fetch the previous page of the list.

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
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
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
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
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
        include: List[RunStepInclude] | NotGiven = NOT_GIVEN,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[run_create_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
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
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[run_create_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
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
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[run_create_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
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
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[run_create_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
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
            "OpenAI-Beta": "assistants=v2",
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

        terminal_states = {"requires_action", "cancelled", "completed", "failed", "expired", "incomplete"}
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

            await self._sleep(poll_interval_ms / 1000)

    @overload
    def stream(
        self,
        *,
        assistant_id: str,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[run_create_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
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
        include: List[RunStepInclude] | NotGiven = NOT_GIVEN,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[run_create_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
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
        include: List[RunStepInclude] | NotGiven = NOT_GIVEN,
        additional_instructions: Optional[str] | NotGiven = NOT_GIVEN,
        additional_messages: Optional[Iterable[run_create_params.AdditionalMessage]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[AssistantToolParam]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[run_create_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
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
            "OpenAI-Beta": "assistants=v2",
            "X-Stainless-Stream-Helper": "threads.runs.create_and_stream",
            "X-Stainless-Custom-Event-Handler": "true" if event_handler else "false",
            **(extra_headers or {}),
        }
        request = self._post(
            f"/threads/{thread_id}/runs",
            body=maybe_transform(
                {
                    "assistant_id": assistant_id,
                    "include": include,
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
                    "truncation_strategy": truncation_strategy,
                    "top_p": top_p,
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
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
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
            "OpenAI-Beta": "assistants=v2",
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
