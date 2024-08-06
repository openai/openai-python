# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional, overload
from functools import partial
from typing_extensions import Literal

import httpx

from .... import _legacy_response
from .runs import (
    Runs,
    AsyncRuns,
    RunsWithRawResponse,
    AsyncRunsWithRawResponse,
    RunsWithStreamingResponse,
    AsyncRunsWithStreamingResponse,
)
from .messages import (
    Messages,
    AsyncMessages,
    MessagesWithRawResponse,
    AsyncMessagesWithRawResponse,
    MessagesWithStreamingResponse,
    AsyncMessagesWithStreamingResponse,
)
from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import (
    required_args,
    maybe_transform,
    async_maybe_transform,
)
from .runs.runs import Runs, AsyncRuns
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ...._streaming import Stream, AsyncStream
from ....types.beta import (
    thread_create_params,
    thread_update_params,
    thread_create_and_run_params,
)
from ...._base_client import make_request_options
from ....lib.streaming import (
    AssistantEventHandler,
    AssistantEventHandlerT,
    AssistantStreamManager,
    AsyncAssistantEventHandler,
    AsyncAssistantEventHandlerT,
    AsyncAssistantStreamManager,
)
from ....types.chat_model import ChatModel
from ....types.beta.thread import Thread
from ....types.beta.threads.run import Run
from ....types.beta.thread_deleted import ThreadDeleted
from ....types.beta.assistant_stream_event import AssistantStreamEvent
from ....types.beta.assistant_tool_choice_option_param import AssistantToolChoiceOptionParam
from ....types.beta.assistant_response_format_option_param import AssistantResponseFormatOptionParam

__all__ = ["Threads", "AsyncThreads"]


class Threads(SyncAPIResource):
    @cached_property
    def runs(self) -> Runs:
        return Runs(self._client)

    @cached_property
    def messages(self) -> Messages:
        return Messages(self._client)

    @cached_property
    def with_raw_response(self) -> ThreadsWithRawResponse:
        return ThreadsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ThreadsWithStreamingResponse:
        return ThreadsWithStreamingResponse(self)

    def create(
        self,
        *,
        messages: Iterable[thread_create_params.Message] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        tool_resources: Optional[thread_create_params.ToolResources] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Thread:
        """
        Create a thread.

        Args:
          messages: A list of [messages](https://platform.openai.com/docs/api-reference/messages) to
              start the thread with.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format. Keys
              can be a maximum of 64 characters long and values can be a maxium of 512
              characters long.

          tool_resources: A set of resources that are made available to the assistant's tools in this
              thread. The resources are specific to the type of tool. For example, the
              `code_interpreter` tool requires a list of file IDs, while the `file_search`
              tool requires a list of vector store IDs.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return self._post(
            "/threads",
            body=maybe_transform(
                {
                    "messages": messages,
                    "metadata": metadata,
                    "tool_resources": tool_resources,
                },
                thread_create_params.ThreadCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Thread,
        )

    def retrieve(
        self,
        thread_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Thread:
        """
        Retrieves a thread.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return self._get(
            f"/threads/{thread_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Thread,
        )

    def update(
        self,
        thread_id: str,
        *,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        tool_resources: Optional[thread_update_params.ToolResources] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Thread:
        """
        Modifies a thread.

        Args:
          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format. Keys
              can be a maximum of 64 characters long and values can be a maxium of 512
              characters long.

          tool_resources: A set of resources that are made available to the assistant's tools in this
              thread. The resources are specific to the type of tool. For example, the
              `code_interpreter` tool requires a list of file IDs, while the `file_search`
              tool requires a list of vector store IDs.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return self._post(
            f"/threads/{thread_id}",
            body=maybe_transform(
                {
                    "metadata": metadata,
                    "tool_resources": tool_resources,
                },
                thread_update_params.ThreadUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Thread,
        )

    def delete(
        self,
        thread_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ThreadDeleted:
        """
        Delete a thread.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return self._delete(
            f"/threads/{thread_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ThreadDeleted,
        )

    @overload
    def create_and_run(
        self,
        *,
        assistant_id: str,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        stream: Optional[Literal[False]] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        thread: thread_create_and_run_params.Thread | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tool_resources: Optional[thread_create_and_run_params.ToolResources] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[thread_create_and_run_params.Tool]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[thread_create_and_run_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run:
        """
        Create a thread and run it in one request.

        Args:
          assistant_id: The ID of the
              [assistant](https://platform.openai.com/docs/api-reference/assistants) to use to
              execute this run.

          instructions: Override the default system message of the assistant. This is useful for
              modifying the behavior on a per-run basis.

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
              can be a maximum of 64 characters long and values can be a maxium of 512
              characters long.

          model: The ID of the [Model](https://platform.openai.com/docs/api-reference/models) to
              be used to execute this run. If a value is provided here, it will override the
              model associated with the assistant. If not, the model associated with the
              assistant will be used.

          parallel_tool_calls: Whether to enable
              [parallel function calling](https://platform.openai.com/docs/guides/function-calling/parallel-function-calling)
              during tool use.

          response_format: Specifies the format that the model must output. Compatible with
              [GPT-4o](https://platform.openai.com/docs/models/gpt-4o),
              [GPT-4 Turbo](https://platform.openai.com/docs/models/gpt-4-turbo-and-gpt-4),
              and all GPT-3.5 Turbo models since `gpt-3.5-turbo-1106`.

              Setting to `{ "type": "json_schema", "json_schema": {...} }` enables Structured
              Outputs which guarantees the model will match your supplied JSON schema. Learn
              more in the
              [Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs).

              Setting to `{ "type": "json_object" }` enables JSON mode, which guarantees the
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

          thread: If no thread is provided, an empty thread will be created.

          tool_choice: Controls which (if any) tool is called by the model. `none` means the model will
              not call any tools and instead generates a message. `auto` is the default value
              and means the model can pick between generating a message or calling one or more
              tools. `required` means the model must call one or more tools before responding
              to the user. Specifying a particular tool like `{"type": "file_search"}` or
              `{"type": "function", "function": {"name": "my_function"}}` forces the model to
              call that tool.

          tool_resources: A set of resources that are used by the assistant's tools. The resources are
              specific to the type of tool. For example, the `code_interpreter` tool requires
              a list of file IDs, while the `file_search` tool requires a list of vector store
              IDs.

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
    def create_and_run(
        self,
        *,
        assistant_id: str,
        stream: Literal[True],
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        thread: thread_create_and_run_params.Thread | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tool_resources: Optional[thread_create_and_run_params.ToolResources] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[thread_create_and_run_params.Tool]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[thread_create_and_run_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Stream[AssistantStreamEvent]:
        """
        Create a thread and run it in one request.

        Args:
          assistant_id: The ID of the
              [assistant](https://platform.openai.com/docs/api-reference/assistants) to use to
              execute this run.

          stream: If `true`, returns a stream of events that happen during the Run as server-sent
              events, terminating when the Run enters a terminal state with a `data: [DONE]`
              message.

          instructions: Override the default system message of the assistant. This is useful for
              modifying the behavior on a per-run basis.

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
              can be a maximum of 64 characters long and values can be a maxium of 512
              characters long.

          model: The ID of the [Model](https://platform.openai.com/docs/api-reference/models) to
              be used to execute this run. If a value is provided here, it will override the
              model associated with the assistant. If not, the model associated with the
              assistant will be used.

          parallel_tool_calls: Whether to enable
              [parallel function calling](https://platform.openai.com/docs/guides/function-calling/parallel-function-calling)
              during tool use.

          response_format: Specifies the format that the model must output. Compatible with
              [GPT-4o](https://platform.openai.com/docs/models/gpt-4o),
              [GPT-4 Turbo](https://platform.openai.com/docs/models/gpt-4-turbo-and-gpt-4),
              and all GPT-3.5 Turbo models since `gpt-3.5-turbo-1106`.

              Setting to `{ "type": "json_schema", "json_schema": {...} }` enables Structured
              Outputs which guarantees the model will match your supplied JSON schema. Learn
              more in the
              [Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs).

              Setting to `{ "type": "json_object" }` enables JSON mode, which guarantees the
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

          thread: If no thread is provided, an empty thread will be created.

          tool_choice: Controls which (if any) tool is called by the model. `none` means the model will
              not call any tools and instead generates a message. `auto` is the default value
              and means the model can pick between generating a message or calling one or more
              tools. `required` means the model must call one or more tools before responding
              to the user. Specifying a particular tool like `{"type": "file_search"}` or
              `{"type": "function", "function": {"name": "my_function"}}` forces the model to
              call that tool.

          tool_resources: A set of resources that are used by the assistant's tools. The resources are
              specific to the type of tool. For example, the `code_interpreter` tool requires
              a list of file IDs, while the `file_search` tool requires a list of vector store
              IDs.

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
    def create_and_run(
        self,
        *,
        assistant_id: str,
        stream: bool,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        thread: thread_create_and_run_params.Thread | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tool_resources: Optional[thread_create_and_run_params.ToolResources] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[thread_create_and_run_params.Tool]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[thread_create_and_run_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run | Stream[AssistantStreamEvent]:
        """
        Create a thread and run it in one request.

        Args:
          assistant_id: The ID of the
              [assistant](https://platform.openai.com/docs/api-reference/assistants) to use to
              execute this run.

          stream: If `true`, returns a stream of events that happen during the Run as server-sent
              events, terminating when the Run enters a terminal state with a `data: [DONE]`
              message.

          instructions: Override the default system message of the assistant. This is useful for
              modifying the behavior on a per-run basis.

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
              can be a maximum of 64 characters long and values can be a maxium of 512
              characters long.

          model: The ID of the [Model](https://platform.openai.com/docs/api-reference/models) to
              be used to execute this run. If a value is provided here, it will override the
              model associated with the assistant. If not, the model associated with the
              assistant will be used.

          parallel_tool_calls: Whether to enable
              [parallel function calling](https://platform.openai.com/docs/guides/function-calling/parallel-function-calling)
              during tool use.

          response_format: Specifies the format that the model must output. Compatible with
              [GPT-4o](https://platform.openai.com/docs/models/gpt-4o),
              [GPT-4 Turbo](https://platform.openai.com/docs/models/gpt-4-turbo-and-gpt-4),
              and all GPT-3.5 Turbo models since `gpt-3.5-turbo-1106`.

              Setting to `{ "type": "json_schema", "json_schema": {...} }` enables Structured
              Outputs which guarantees the model will match your supplied JSON schema. Learn
              more in the
              [Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs).

              Setting to `{ "type": "json_object" }` enables JSON mode, which guarantees the
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

          thread: If no thread is provided, an empty thread will be created.

          tool_choice: Controls which (if any) tool is called by the model. `none` means the model will
              not call any tools and instead generates a message. `auto` is the default value
              and means the model can pick between generating a message or calling one or more
              tools. `required` means the model must call one or more tools before responding
              to the user. Specifying a particular tool like `{"type": "file_search"}` or
              `{"type": "function", "function": {"name": "my_function"}}` forces the model to
              call that tool.

          tool_resources: A set of resources that are used by the assistant's tools. The resources are
              specific to the type of tool. For example, the `code_interpreter` tool requires
              a list of file IDs, while the `file_search` tool requires a list of vector store
              IDs.

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
    def create_and_run(
        self,
        *,
        assistant_id: str,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        thread: thread_create_and_run_params.Thread | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tool_resources: Optional[thread_create_and_run_params.ToolResources] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[thread_create_and_run_params.Tool]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[thread_create_and_run_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run | Stream[AssistantStreamEvent]:
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return self._post(
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
                    "stream": stream,
                    "temperature": temperature,
                    "thread": thread,
                    "tool_choice": tool_choice,
                    "tool_resources": tool_resources,
                    "tools": tools,
                    "top_p": top_p,
                    "truncation_strategy": truncation_strategy,
                },
                thread_create_and_run_params.ThreadCreateAndRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Run,
            stream=stream or False,
            stream_cls=Stream[AssistantStreamEvent],
        )

    def create_and_run_poll(
        self,
        *,
        assistant_id: str,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        thread: thread_create_and_run_params.Thread | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tool_resources: Optional[thread_create_and_run_params.ToolResources] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[thread_create_and_run_params.Tool]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[thread_create_and_run_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
        poll_interval_ms: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
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

    @overload
    def create_and_run_stream(
        self,
        *,
        assistant_id: str,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        thread: thread_create_and_run_params.Thread | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tool_resources: Optional[thread_create_and_run_params.ToolResources] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[thread_create_and_run_params.Tool]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[thread_create_and_run_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssistantStreamManager[AssistantEventHandler]:
        """Create a thread and stream the run back"""
        ...

    @overload
    def create_and_run_stream(
        self,
        *,
        assistant_id: str,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        thread: thread_create_and_run_params.Thread | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tool_resources: Optional[thread_create_and_run_params.ToolResources] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[thread_create_and_run_params.Tool]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[thread_create_and_run_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
        event_handler: AssistantEventHandlerT,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssistantStreamManager[AssistantEventHandlerT]:
        """Create a thread and stream the run back"""
        ...

    def create_and_run_stream(
        self,
        *,
        assistant_id: str,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        thread: thread_create_and_run_params.Thread | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tool_resources: Optional[thread_create_and_run_params.ToolResources] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[thread_create_and_run_params.Tool]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[thread_create_and_run_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
        event_handler: AssistantEventHandlerT | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
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
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Run,
            stream=True,
            stream_cls=Stream[AssistantStreamEvent],
        )
        return AssistantStreamManager(make_request, event_handler=event_handler or AssistantEventHandler())


class AsyncThreads(AsyncAPIResource):
    @cached_property
    def runs(self) -> AsyncRuns:
        return AsyncRuns(self._client)

    @cached_property
    def messages(self) -> AsyncMessages:
        return AsyncMessages(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncThreadsWithRawResponse:
        return AsyncThreadsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncThreadsWithStreamingResponse:
        return AsyncThreadsWithStreamingResponse(self)

    async def create(
        self,
        *,
        messages: Iterable[thread_create_params.Message] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        tool_resources: Optional[thread_create_params.ToolResources] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Thread:
        """
        Create a thread.

        Args:
          messages: A list of [messages](https://platform.openai.com/docs/api-reference/messages) to
              start the thread with.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format. Keys
              can be a maximum of 64 characters long and values can be a maxium of 512
              characters long.

          tool_resources: A set of resources that are made available to the assistant's tools in this
              thread. The resources are specific to the type of tool. For example, the
              `code_interpreter` tool requires a list of file IDs, while the `file_search`
              tool requires a list of vector store IDs.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return await self._post(
            "/threads",
            body=await async_maybe_transform(
                {
                    "messages": messages,
                    "metadata": metadata,
                    "tool_resources": tool_resources,
                },
                thread_create_params.ThreadCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Thread,
        )

    async def retrieve(
        self,
        thread_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Thread:
        """
        Retrieves a thread.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return await self._get(
            f"/threads/{thread_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Thread,
        )

    async def update(
        self,
        thread_id: str,
        *,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        tool_resources: Optional[thread_update_params.ToolResources] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Thread:
        """
        Modifies a thread.

        Args:
          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format. Keys
              can be a maximum of 64 characters long and values can be a maxium of 512
              characters long.

          tool_resources: A set of resources that are made available to the assistant's tools in this
              thread. The resources are specific to the type of tool. For example, the
              `code_interpreter` tool requires a list of file IDs, while the `file_search`
              tool requires a list of vector store IDs.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return await self._post(
            f"/threads/{thread_id}",
            body=await async_maybe_transform(
                {
                    "metadata": metadata,
                    "tool_resources": tool_resources,
                },
                thread_update_params.ThreadUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Thread,
        )

    async def delete(
        self,
        thread_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ThreadDeleted:
        """
        Delete a thread.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not thread_id:
            raise ValueError(f"Expected a non-empty value for `thread_id` but received {thread_id!r}")
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return await self._delete(
            f"/threads/{thread_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ThreadDeleted,
        )

    @overload
    async def create_and_run(
        self,
        *,
        assistant_id: str,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        stream: Optional[Literal[False]] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        thread: thread_create_and_run_params.Thread | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tool_resources: Optional[thread_create_and_run_params.ToolResources] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[thread_create_and_run_params.Tool]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[thread_create_and_run_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run:
        """
        Create a thread and run it in one request.

        Args:
          assistant_id: The ID of the
              [assistant](https://platform.openai.com/docs/api-reference/assistants) to use to
              execute this run.

          instructions: Override the default system message of the assistant. This is useful for
              modifying the behavior on a per-run basis.

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
              can be a maximum of 64 characters long and values can be a maxium of 512
              characters long.

          model: The ID of the [Model](https://platform.openai.com/docs/api-reference/models) to
              be used to execute this run. If a value is provided here, it will override the
              model associated with the assistant. If not, the model associated with the
              assistant will be used.

          parallel_tool_calls: Whether to enable
              [parallel function calling](https://platform.openai.com/docs/guides/function-calling/parallel-function-calling)
              during tool use.

          response_format: Specifies the format that the model must output. Compatible with
              [GPT-4o](https://platform.openai.com/docs/models/gpt-4o),
              [GPT-4 Turbo](https://platform.openai.com/docs/models/gpt-4-turbo-and-gpt-4),
              and all GPT-3.5 Turbo models since `gpt-3.5-turbo-1106`.

              Setting to `{ "type": "json_schema", "json_schema": {...} }` enables Structured
              Outputs which guarantees the model will match your supplied JSON schema. Learn
              more in the
              [Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs).

              Setting to `{ "type": "json_object" }` enables JSON mode, which guarantees the
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

          thread: If no thread is provided, an empty thread will be created.

          tool_choice: Controls which (if any) tool is called by the model. `none` means the model will
              not call any tools and instead generates a message. `auto` is the default value
              and means the model can pick between generating a message or calling one or more
              tools. `required` means the model must call one or more tools before responding
              to the user. Specifying a particular tool like `{"type": "file_search"}` or
              `{"type": "function", "function": {"name": "my_function"}}` forces the model to
              call that tool.

          tool_resources: A set of resources that are used by the assistant's tools. The resources are
              specific to the type of tool. For example, the `code_interpreter` tool requires
              a list of file IDs, while the `file_search` tool requires a list of vector store
              IDs.

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
    async def create_and_run(
        self,
        *,
        assistant_id: str,
        stream: Literal[True],
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        thread: thread_create_and_run_params.Thread | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tool_resources: Optional[thread_create_and_run_params.ToolResources] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[thread_create_and_run_params.Tool]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[thread_create_and_run_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncStream[AssistantStreamEvent]:
        """
        Create a thread and run it in one request.

        Args:
          assistant_id: The ID of the
              [assistant](https://platform.openai.com/docs/api-reference/assistants) to use to
              execute this run.

          stream: If `true`, returns a stream of events that happen during the Run as server-sent
              events, terminating when the Run enters a terminal state with a `data: [DONE]`
              message.

          instructions: Override the default system message of the assistant. This is useful for
              modifying the behavior on a per-run basis.

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
              can be a maximum of 64 characters long and values can be a maxium of 512
              characters long.

          model: The ID of the [Model](https://platform.openai.com/docs/api-reference/models) to
              be used to execute this run. If a value is provided here, it will override the
              model associated with the assistant. If not, the model associated with the
              assistant will be used.

          parallel_tool_calls: Whether to enable
              [parallel function calling](https://platform.openai.com/docs/guides/function-calling/parallel-function-calling)
              during tool use.

          response_format: Specifies the format that the model must output. Compatible with
              [GPT-4o](https://platform.openai.com/docs/models/gpt-4o),
              [GPT-4 Turbo](https://platform.openai.com/docs/models/gpt-4-turbo-and-gpt-4),
              and all GPT-3.5 Turbo models since `gpt-3.5-turbo-1106`.

              Setting to `{ "type": "json_schema", "json_schema": {...} }` enables Structured
              Outputs which guarantees the model will match your supplied JSON schema. Learn
              more in the
              [Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs).

              Setting to `{ "type": "json_object" }` enables JSON mode, which guarantees the
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

          thread: If no thread is provided, an empty thread will be created.

          tool_choice: Controls which (if any) tool is called by the model. `none` means the model will
              not call any tools and instead generates a message. `auto` is the default value
              and means the model can pick between generating a message or calling one or more
              tools. `required` means the model must call one or more tools before responding
              to the user. Specifying a particular tool like `{"type": "file_search"}` or
              `{"type": "function", "function": {"name": "my_function"}}` forces the model to
              call that tool.

          tool_resources: A set of resources that are used by the assistant's tools. The resources are
              specific to the type of tool. For example, the `code_interpreter` tool requires
              a list of file IDs, while the `file_search` tool requires a list of vector store
              IDs.

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
    async def create_and_run(
        self,
        *,
        assistant_id: str,
        stream: bool,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        thread: thread_create_and_run_params.Thread | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tool_resources: Optional[thread_create_and_run_params.ToolResources] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[thread_create_and_run_params.Tool]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[thread_create_and_run_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run | AsyncStream[AssistantStreamEvent]:
        """
        Create a thread and run it in one request.

        Args:
          assistant_id: The ID of the
              [assistant](https://platform.openai.com/docs/api-reference/assistants) to use to
              execute this run.

          stream: If `true`, returns a stream of events that happen during the Run as server-sent
              events, terminating when the Run enters a terminal state with a `data: [DONE]`
              message.

          instructions: Override the default system message of the assistant. This is useful for
              modifying the behavior on a per-run basis.

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
              can be a maximum of 64 characters long and values can be a maxium of 512
              characters long.

          model: The ID of the [Model](https://platform.openai.com/docs/api-reference/models) to
              be used to execute this run. If a value is provided here, it will override the
              model associated with the assistant. If not, the model associated with the
              assistant will be used.

          parallel_tool_calls: Whether to enable
              [parallel function calling](https://platform.openai.com/docs/guides/function-calling/parallel-function-calling)
              during tool use.

          response_format: Specifies the format that the model must output. Compatible with
              [GPT-4o](https://platform.openai.com/docs/models/gpt-4o),
              [GPT-4 Turbo](https://platform.openai.com/docs/models/gpt-4-turbo-and-gpt-4),
              and all GPT-3.5 Turbo models since `gpt-3.5-turbo-1106`.

              Setting to `{ "type": "json_schema", "json_schema": {...} }` enables Structured
              Outputs which guarantees the model will match your supplied JSON schema. Learn
              more in the
              [Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs).

              Setting to `{ "type": "json_object" }` enables JSON mode, which guarantees the
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

          thread: If no thread is provided, an empty thread will be created.

          tool_choice: Controls which (if any) tool is called by the model. `none` means the model will
              not call any tools and instead generates a message. `auto` is the default value
              and means the model can pick between generating a message or calling one or more
              tools. `required` means the model must call one or more tools before responding
              to the user. Specifying a particular tool like `{"type": "file_search"}` or
              `{"type": "function", "function": {"name": "my_function"}}` forces the model to
              call that tool.

          tool_resources: A set of resources that are used by the assistant's tools. The resources are
              specific to the type of tool. For example, the `code_interpreter` tool requires
              a list of file IDs, while the `file_search` tool requires a list of vector store
              IDs.

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
    async def create_and_run(
        self,
        *,
        assistant_id: str,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        thread: thread_create_and_run_params.Thread | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tool_resources: Optional[thread_create_and_run_params.ToolResources] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[thread_create_and_run_params.Tool]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[thread_create_and_run_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Run | AsyncStream[AssistantStreamEvent]:
        extra_headers = {"OpenAI-Beta": "assistants=v2", **(extra_headers or {})}
        return await self._post(
            "/threads/runs",
            body=await async_maybe_transform(
                {
                    "assistant_id": assistant_id,
                    "instructions": instructions,
                    "max_completion_tokens": max_completion_tokens,
                    "max_prompt_tokens": max_prompt_tokens,
                    "metadata": metadata,
                    "model": model,
                    "parallel_tool_calls": parallel_tool_calls,
                    "response_format": response_format,
                    "stream": stream,
                    "temperature": temperature,
                    "thread": thread,
                    "tool_choice": tool_choice,
                    "tool_resources": tool_resources,
                    "tools": tools,
                    "top_p": top_p,
                    "truncation_strategy": truncation_strategy,
                },
                thread_create_and_run_params.ThreadCreateAndRunParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Run,
            stream=stream or False,
            stream_cls=AsyncStream[AssistantStreamEvent],
        )

    async def create_and_run_poll(
        self,
        *,
        assistant_id: str,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        thread: thread_create_and_run_params.Thread | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tool_resources: Optional[thread_create_and_run_params.ToolResources] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[thread_create_and_run_params.Tool]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[thread_create_and_run_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
        poll_interval_ms: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
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

    @overload
    def create_and_run_stream(
        self,
        *,
        assistant_id: str,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        thread: thread_create_and_run_params.Thread | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tool_resources: Optional[thread_create_and_run_params.ToolResources] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[thread_create_and_run_params.Tool]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[thread_create_and_run_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncAssistantStreamManager[AsyncAssistantEventHandler]:
        """Create a thread and stream the run back"""
        ...

    @overload
    def create_and_run_stream(
        self,
        *,
        assistant_id: str,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        thread: thread_create_and_run_params.Thread | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tool_resources: Optional[thread_create_and_run_params.ToolResources] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[thread_create_and_run_params.Tool]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[thread_create_and_run_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
        event_handler: AsyncAssistantEventHandlerT,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncAssistantStreamManager[AsyncAssistantEventHandlerT]:
        """Create a thread and stream the run back"""
        ...

    def create_and_run_stream(
        self,
        *,
        assistant_id: str,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_prompt_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[object] | NotGiven = NOT_GIVEN,
        model: Union[str, ChatModel, None] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        response_format: Optional[AssistantResponseFormatOptionParam] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        thread: thread_create_and_run_params.Thread | NotGiven = NOT_GIVEN,
        tool_choice: Optional[AssistantToolChoiceOptionParam] | NotGiven = NOT_GIVEN,
        tool_resources: Optional[thread_create_and_run_params.ToolResources] | NotGiven = NOT_GIVEN,
        tools: Optional[Iterable[thread_create_and_run_params.Tool]] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation_strategy: Optional[thread_create_and_run_params.TruncationStrategy] | NotGiven = NOT_GIVEN,
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
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Run,
            stream=True,
            stream_cls=AsyncStream[AssistantStreamEvent],
        )
        return AsyncAssistantStreamManager(request, event_handler=event_handler or AsyncAssistantEventHandler())


class ThreadsWithRawResponse:
    def __init__(self, threads: Threads) -> None:
        self._threads = threads

        self.create = _legacy_response.to_raw_response_wrapper(
            threads.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            threads.retrieve,
        )
        self.update = _legacy_response.to_raw_response_wrapper(
            threads.update,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            threads.delete,
        )
        self.create_and_run = _legacy_response.to_raw_response_wrapper(
            threads.create_and_run,
        )

    @cached_property
    def runs(self) -> RunsWithRawResponse:
        return RunsWithRawResponse(self._threads.runs)

    @cached_property
    def messages(self) -> MessagesWithRawResponse:
        return MessagesWithRawResponse(self._threads.messages)


class AsyncThreadsWithRawResponse:
    def __init__(self, threads: AsyncThreads) -> None:
        self._threads = threads

        self.create = _legacy_response.async_to_raw_response_wrapper(
            threads.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            threads.retrieve,
        )
        self.update = _legacy_response.async_to_raw_response_wrapper(
            threads.update,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            threads.delete,
        )
        self.create_and_run = _legacy_response.async_to_raw_response_wrapper(
            threads.create_and_run,
        )

    @cached_property
    def runs(self) -> AsyncRunsWithRawResponse:
        return AsyncRunsWithRawResponse(self._threads.runs)

    @cached_property
    def messages(self) -> AsyncMessagesWithRawResponse:
        return AsyncMessagesWithRawResponse(self._threads.messages)


class ThreadsWithStreamingResponse:
    def __init__(self, threads: Threads) -> None:
        self._threads = threads

        self.create = to_streamed_response_wrapper(
            threads.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            threads.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            threads.update,
        )
        self.delete = to_streamed_response_wrapper(
            threads.delete,
        )
        self.create_and_run = to_streamed_response_wrapper(
            threads.create_and_run,
        )

    @cached_property
    def runs(self) -> RunsWithStreamingResponse:
        return RunsWithStreamingResponse(self._threads.runs)

    @cached_property
    def messages(self) -> MessagesWithStreamingResponse:
        return MessagesWithStreamingResponse(self._threads.messages)


class AsyncThreadsWithStreamingResponse:
    def __init__(self, threads: AsyncThreads) -> None:
        self._threads = threads

        self.create = async_to_streamed_response_wrapper(
            threads.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            threads.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            threads.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            threads.delete,
        )
        self.create_and_run = async_to_streamed_response_wrapper(
            threads.create_and_run,
        )

    @cached_property
    def runs(self) -> AsyncRunsWithStreamingResponse:
        return AsyncRunsWithStreamingResponse(self._threads.runs)

    @cached_property
    def messages(self) -> AsyncMessagesWithStreamingResponse:
        return AsyncMessagesWithStreamingResponse(self._threads.messages)
