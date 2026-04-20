# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import json
import time
import random
import logging
from copy import copy
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    Any,
    List,
    Type,
    Union,
    Callable,
    Iterable,
    Iterator,
    Optional,
    Awaitable,
    AsyncIterator,
    cast,
)
from functools import partial
from typing_extensions import Literal, overload

import httpx
from pydantic import BaseModel

from ... import _legacy_response
from ..._types import NOT_GIVEN, Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
from ..._utils import is_given, path_template, maybe_transform, strip_not_given, async_maybe_transform
from ..._compat import cached_property
from ..._models import construct_type_unchecked
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from .input_items import (
    InputItems,
    AsyncInputItems,
    InputItemsWithRawResponse,
    AsyncInputItemsWithRawResponse,
    InputItemsWithStreamingResponse,
    AsyncInputItemsWithStreamingResponse,
)
from ..._streaming import Stream, AsyncStream
from ...lib._tools import PydanticFunctionTool, ResponsesPydanticFunctionTool
from .input_tokens import (
    InputTokens,
    AsyncInputTokens,
    InputTokensWithRawResponse,
    AsyncInputTokensWithRawResponse,
    InputTokensWithStreamingResponse,
    AsyncInputTokensWithStreamingResponse,
)
from ..._exceptions import OpenAIError, WebSocketConnectionClosedError
from ..._send_queue import SendQueue
from ..._base_client import _merge_mappings, make_request_options
from ..._event_handler import EventHandlerRegistry
from ...types.responses import (
    response_create_params,
    response_compact_params,
    response_retrieve_params,
    responses_client_event_param,
)
from ...lib._parsing._responses import (
    TextFormatT,
    parse_response,
    type_to_text_format_param as _type_to_text_format_param,
)
from ...types.responses.response import Response
from ...types.responses.tool_param import ToolParam, ParseableToolParam
from ...types.shared_params.metadata import Metadata
from ...types.websocket_reconnection import ReconnectingEvent, ReconnectingOverrides, is_recoverable_close
from ...types.shared_params.reasoning import Reasoning
from ...types.responses.parsed_response import ParsedResponse
from ...lib.streaming.responses._responses import ResponseStreamManager, AsyncResponseStreamManager
from ...types.responses.compacted_response import CompactedResponse
from ...types.websocket_connection_options import WebSocketConnectionOptions
from ...types.responses.response_includable import ResponseIncludable
from ...types.shared_params.responses_model import ResponsesModel
from ...types.responses.response_error_event import ResponseErrorEvent
from ...types.responses.response_input_param import ResponseInputParam
from ...types.responses.response_prompt_param import ResponsePromptParam
from ...types.responses.response_stream_event import ResponseStreamEvent
from ...types.responses.responses_client_event import ResponsesClientEvent
from ...types.responses.responses_server_event import ResponsesServerEvent
from ...types.responses.response_input_item_param import ResponseInputItemParam
from ...types.responses.response_text_config_param import ResponseTextConfigParam
from ...types.responses.responses_client_event_param import ResponsesClientEventParam

if TYPE_CHECKING:
    from websockets.sync.client import ClientConnection as WebSocketConnection
    from websockets.asyncio.client import ClientConnection as AsyncWebSocketConnection

    from ..._client import OpenAI, AsyncOpenAI

__all__ = ["Responses", "AsyncResponses"]

log: logging.Logger = logging.getLogger(__name__)


class Responses(SyncAPIResource):
    @cached_property
    def input_items(self) -> InputItems:
        return InputItems(self._client)

    @cached_property
    def input_tokens(self) -> InputTokens:
        return InputTokens(self._client)

    @cached_property
    def with_raw_response(self) -> ResponsesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return ResponsesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ResponsesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return ResponsesWithStreamingResponse(self)

    @overload
    def create(
        self,
        *,
        background: Optional[bool] | Omit = omit,
        context_management: Optional[Iterable[response_create_params.ContextManagement]] | Omit = omit,
        conversation: Optional[response_create_params.Conversation] | Omit = omit,
        include: Optional[List[ResponseIncludable]] | Omit = omit,
        input: Union[str, ResponseInputParam] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        max_output_tokens: Optional[int] | Omit = omit,
        max_tool_calls: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        model: ResponsesModel | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt: Optional[ResponsePromptParam] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | Omit = omit,
        reasoning: Optional[Reasoning] | Omit = omit,
        safety_identifier: str | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream: Optional[Literal[False]] | Omit = omit,
        stream_options: Optional[response_create_params.StreamOptions] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        text: ResponseTextConfigParam | Omit = omit,
        tool_choice: response_create_params.ToolChoice | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        truncation: Optional[Literal["auto", "disabled"]] | Omit = omit,
        user: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Response:
        """Creates a model response.

        Provide
        [text](https://platform.openai.com/docs/guides/text) or
        [image](https://platform.openai.com/docs/guides/images) inputs to generate
        [text](https://platform.openai.com/docs/guides/text) or
        [JSON](https://platform.openai.com/docs/guides/structured-outputs) outputs. Have
        the model call your own
        [custom code](https://platform.openai.com/docs/guides/function-calling) or use
        built-in [tools](https://platform.openai.com/docs/guides/tools) like
        [web search](https://platform.openai.com/docs/guides/tools-web-search) or
        [file search](https://platform.openai.com/docs/guides/tools-file-search) to use
        your own data as input for the model's response.

        Args:
          background: Whether to run the model response in the background.
              [Learn more](https://platform.openai.com/docs/guides/background).

          context_management: Context management configuration for this request.

          conversation: The conversation that this response belongs to. Items from this conversation are
              prepended to `input_items` for this response request. Input items and output
              items from this response are automatically added to this conversation after this
              response completes.

          include: Specify additional output data to include in the model response. Currently
              supported values are:

              - `web_search_call.action.sources`: Include the sources of the web search tool
                call.
              - `code_interpreter_call.outputs`: Includes the outputs of python code execution
                in code interpreter tool call items.
              - `computer_call_output.output.image_url`: Include image urls from the computer
                call output.
              - `file_search_call.results`: Include the search results of the file search tool
                call.
              - `message.input_image.image_url`: Include image urls from the input message.
              - `message.output_text.logprobs`: Include logprobs with assistant messages.
              - `reasoning.encrypted_content`: Includes an encrypted version of reasoning
                tokens in reasoning item outputs. This enables reasoning items to be used in
                multi-turn conversations when using the Responses API statelessly (like when
                the `store` parameter is set to `false`, or when an organization is enrolled
                in the zero data retention program).

          input: Text, image, or file inputs to the model, used to generate a response.

              Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Image inputs](https://platform.openai.com/docs/guides/images)
              - [File inputs](https://platform.openai.com/docs/guides/pdf-files)
              - [Conversation state](https://platform.openai.com/docs/guides/conversation-state)
              - [Function calling](https://platform.openai.com/docs/guides/function-calling)

          instructions: A system (or developer) message inserted into the model's context.

              When using along with `previous_response_id`, the instructions from a previous
              response will not be carried over to the next response. This makes it simple to
              swap out system (or developer) messages in new responses.

          max_output_tokens: An upper bound for the number of tokens that can be generated for a response,
              including visible output tokens and
              [reasoning tokens](https://platform.openai.com/docs/guides/reasoning).

          max_tool_calls: The maximum number of total calls to built-in tools that can be processed in a
              response. This maximum number applies across all built-in tool calls, not per
              individual tool. Any further attempts to call a tool by the model will be
              ignored.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format, and
              querying for objects via API or the dashboard.

              Keys are strings with a maximum length of 64 characters. Values are strings with
              a maximum length of 512 characters.

          model: Model ID used to generate the response, like `gpt-4o` or `o3`. OpenAI offers a
              wide range of models with different capabilities, performance characteristics,
              and price points. Refer to the
              [model guide](https://platform.openai.com/docs/models) to browse and compare
              available models.

          parallel_tool_calls: Whether to allow the model to run tool calls in parallel.

          previous_response_id: The unique ID of the previous response to the model. Use this to create
              multi-turn conversations. Learn more about
              [conversation state](https://platform.openai.com/docs/guides/conversation-state).
              Cannot be used in conjunction with `conversation`.

          prompt: Reference to a prompt template and its variables.
              [Learn more](https://platform.openai.com/docs/guides/text?api-mode=responses#reusable-prompts).

          prompt_cache_key: Used by OpenAI to cache responses for similar requests to optimize your cache
              hit rates. Replaces the `user` field.
              [Learn more](https://platform.openai.com/docs/guides/prompt-caching).

          prompt_cache_retention: The retention policy for the prompt cache. Set to `24h` to enable extended
              prompt caching, which keeps cached prefixes active for longer, up to a maximum
              of 24 hours.
              [Learn more](https://platform.openai.com/docs/guides/prompt-caching#prompt-cache-retention).

          reasoning: **gpt-5 and o-series models only**

              Configuration options for
              [reasoning models](https://platform.openai.com/docs/guides/reasoning).

          safety_identifier: A stable identifier used to help detect users of your application that may be
              violating OpenAI's usage policies. The IDs should be a string that uniquely
              identifies each user, with a maximum length of 64 characters. We recommend
              hashing their username or email address, in order to avoid sending us any
              identifying information.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).

          service_tier: Specifies the processing type used for serving the request.

              - If set to 'auto', then the request will be processed with the service tier
                configured in the Project settings. Unless otherwise configured, the Project
                will use 'default'.
              - If set to 'default', then the request will be processed with the standard
                pricing and performance for the selected model.
              - If set to '[flex](https://platform.openai.com/docs/guides/flex-processing)' or
                '[priority](https://openai.com/api-priority-processing/)', then the request
                will be processed with the corresponding service tier.
              - When not set, the default behavior is 'auto'.

              When the `service_tier` parameter is set, the response body will include the
              `service_tier` value based on the processing mode actually used to serve the
              request. This response value may be different from the value set in the
              parameter.

          store: Whether to store the generated model response for later retrieval via API.

          stream: If set to true, the model response data will be streamed to the client as it is
              generated using
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
              See the
              [Streaming section below](https://platform.openai.com/docs/api-reference/responses-streaming)
              for more information.

          stream_options: Options for streaming responses. Only set this when you set `stream: true`.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic. We generally recommend altering this or `top_p` but
              not both.

          text: Configuration options for a text response from the model. Can be plain text or
              structured JSON data. Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)

          tool_choice: How the model should select which tool (or tools) to use when generating a
              response. See the `tools` parameter to see how to specify which tools the model
              can call.

          tools: An array of tools the model may call while generating a response. You can
              specify which tool to use by setting the `tool_choice` parameter.

              We support the following categories of tools:

              - **Built-in tools**: Tools that are provided by OpenAI that extend the model's
                capabilities, like
                [web search](https://platform.openai.com/docs/guides/tools-web-search) or
                [file search](https://platform.openai.com/docs/guides/tools-file-search).
                Learn more about
                [built-in tools](https://platform.openai.com/docs/guides/tools).
              - **MCP Tools**: Integrations with third-party systems via custom MCP servers or
                predefined connectors such as Google Drive and SharePoint. Learn more about
                [MCP Tools](https://platform.openai.com/docs/guides/tools-connectors-mcp).
              - **Function calls (custom tools)**: Functions that are defined by you, enabling
                the model to call your own code with strongly typed arguments and outputs.
                Learn more about
                [function calling](https://platform.openai.com/docs/guides/function-calling).
                You can also use custom tools to call your own code.

          top_logprobs: An integer between 0 and 20 specifying the number of most likely tokens to
              return at each token position, each with an associated log probability.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or `temperature` but not both.

          truncation: The truncation strategy to use for the model response.

              - `auto`: If the input to this Response exceeds the model's context window size,
                the model will truncate the response to fit the context window by dropping
                items from the beginning of the conversation.
              - `disabled` (default): If the input size will exceed the context window size
                for a model, the request will fail with a 400 error.

          user: This field is being replaced by `safety_identifier` and `prompt_cache_key`. Use
              `prompt_cache_key` instead to maintain caching optimizations. A stable
              identifier for your end-users. Used to boost cache hit rates by better bucketing
              similar requests and to help OpenAI detect and prevent abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).

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
        stream: Literal[True],
        background: Optional[bool] | Omit = omit,
        context_management: Optional[Iterable[response_create_params.ContextManagement]] | Omit = omit,
        conversation: Optional[response_create_params.Conversation] | Omit = omit,
        include: Optional[List[ResponseIncludable]] | Omit = omit,
        input: Union[str, ResponseInputParam] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        max_output_tokens: Optional[int] | Omit = omit,
        max_tool_calls: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        model: ResponsesModel | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt: Optional[ResponsePromptParam] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | Omit = omit,
        reasoning: Optional[Reasoning] | Omit = omit,
        safety_identifier: str | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream_options: Optional[response_create_params.StreamOptions] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        text: ResponseTextConfigParam | Omit = omit,
        tool_choice: response_create_params.ToolChoice | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        truncation: Optional[Literal["auto", "disabled"]] | Omit = omit,
        user: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Stream[ResponseStreamEvent]:
        """Creates a model response.

        Provide
        [text](https://platform.openai.com/docs/guides/text) or
        [image](https://platform.openai.com/docs/guides/images) inputs to generate
        [text](https://platform.openai.com/docs/guides/text) or
        [JSON](https://platform.openai.com/docs/guides/structured-outputs) outputs. Have
        the model call your own
        [custom code](https://platform.openai.com/docs/guides/function-calling) or use
        built-in [tools](https://platform.openai.com/docs/guides/tools) like
        [web search](https://platform.openai.com/docs/guides/tools-web-search) or
        [file search](https://platform.openai.com/docs/guides/tools-file-search) to use
        your own data as input for the model's response.

        Args:
          stream: If set to true, the model response data will be streamed to the client as it is
              generated using
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
              See the
              [Streaming section below](https://platform.openai.com/docs/api-reference/responses-streaming)
              for more information.

          background: Whether to run the model response in the background.
              [Learn more](https://platform.openai.com/docs/guides/background).

          context_management: Context management configuration for this request.

          conversation: The conversation that this response belongs to. Items from this conversation are
              prepended to `input_items` for this response request. Input items and output
              items from this response are automatically added to this conversation after this
              response completes.

          include: Specify additional output data to include in the model response. Currently
              supported values are:

              - `web_search_call.action.sources`: Include the sources of the web search tool
                call.
              - `code_interpreter_call.outputs`: Includes the outputs of python code execution
                in code interpreter tool call items.
              - `computer_call_output.output.image_url`: Include image urls from the computer
                call output.
              - `file_search_call.results`: Include the search results of the file search tool
                call.
              - `message.input_image.image_url`: Include image urls from the input message.
              - `message.output_text.logprobs`: Include logprobs with assistant messages.
              - `reasoning.encrypted_content`: Includes an encrypted version of reasoning
                tokens in reasoning item outputs. This enables reasoning items to be used in
                multi-turn conversations when using the Responses API statelessly (like when
                the `store` parameter is set to `false`, or when an organization is enrolled
                in the zero data retention program).

          input: Text, image, or file inputs to the model, used to generate a response.

              Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Image inputs](https://platform.openai.com/docs/guides/images)
              - [File inputs](https://platform.openai.com/docs/guides/pdf-files)
              - [Conversation state](https://platform.openai.com/docs/guides/conversation-state)
              - [Function calling](https://platform.openai.com/docs/guides/function-calling)

          instructions: A system (or developer) message inserted into the model's context.

              When using along with `previous_response_id`, the instructions from a previous
              response will not be carried over to the next response. This makes it simple to
              swap out system (or developer) messages in new responses.

          max_output_tokens: An upper bound for the number of tokens that can be generated for a response,
              including visible output tokens and
              [reasoning tokens](https://platform.openai.com/docs/guides/reasoning).

          max_tool_calls: The maximum number of total calls to built-in tools that can be processed in a
              response. This maximum number applies across all built-in tool calls, not per
              individual tool. Any further attempts to call a tool by the model will be
              ignored.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format, and
              querying for objects via API or the dashboard.

              Keys are strings with a maximum length of 64 characters. Values are strings with
              a maximum length of 512 characters.

          model: Model ID used to generate the response, like `gpt-4o` or `o3`. OpenAI offers a
              wide range of models with different capabilities, performance characteristics,
              and price points. Refer to the
              [model guide](https://platform.openai.com/docs/models) to browse and compare
              available models.

          parallel_tool_calls: Whether to allow the model to run tool calls in parallel.

          previous_response_id: The unique ID of the previous response to the model. Use this to create
              multi-turn conversations. Learn more about
              [conversation state](https://platform.openai.com/docs/guides/conversation-state).
              Cannot be used in conjunction with `conversation`.

          prompt: Reference to a prompt template and its variables.
              [Learn more](https://platform.openai.com/docs/guides/text?api-mode=responses#reusable-prompts).

          prompt_cache_key: Used by OpenAI to cache responses for similar requests to optimize your cache
              hit rates. Replaces the `user` field.
              [Learn more](https://platform.openai.com/docs/guides/prompt-caching).

          prompt_cache_retention: The retention policy for the prompt cache. Set to `24h` to enable extended
              prompt caching, which keeps cached prefixes active for longer, up to a maximum
              of 24 hours.
              [Learn more](https://platform.openai.com/docs/guides/prompt-caching#prompt-cache-retention).

          reasoning: **gpt-5 and o-series models only**

              Configuration options for
              [reasoning models](https://platform.openai.com/docs/guides/reasoning).

          safety_identifier: A stable identifier used to help detect users of your application that may be
              violating OpenAI's usage policies. The IDs should be a string that uniquely
              identifies each user, with a maximum length of 64 characters. We recommend
              hashing their username or email address, in order to avoid sending us any
              identifying information.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).

          service_tier: Specifies the processing type used for serving the request.

              - If set to 'auto', then the request will be processed with the service tier
                configured in the Project settings. Unless otherwise configured, the Project
                will use 'default'.
              - If set to 'default', then the request will be processed with the standard
                pricing and performance for the selected model.
              - If set to '[flex](https://platform.openai.com/docs/guides/flex-processing)' or
                '[priority](https://openai.com/api-priority-processing/)', then the request
                will be processed with the corresponding service tier.
              - When not set, the default behavior is 'auto'.

              When the `service_tier` parameter is set, the response body will include the
              `service_tier` value based on the processing mode actually used to serve the
              request. This response value may be different from the value set in the
              parameter.

          store: Whether to store the generated model response for later retrieval via API.

          stream_options: Options for streaming responses. Only set this when you set `stream: true`.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic. We generally recommend altering this or `top_p` but
              not both.

          text: Configuration options for a text response from the model. Can be plain text or
              structured JSON data. Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)

          tool_choice: How the model should select which tool (or tools) to use when generating a
              response. See the `tools` parameter to see how to specify which tools the model
              can call.

          tools: An array of tools the model may call while generating a response. You can
              specify which tool to use by setting the `tool_choice` parameter.

              We support the following categories of tools:

              - **Built-in tools**: Tools that are provided by OpenAI that extend the model's
                capabilities, like
                [web search](https://platform.openai.com/docs/guides/tools-web-search) or
                [file search](https://platform.openai.com/docs/guides/tools-file-search).
                Learn more about
                [built-in tools](https://platform.openai.com/docs/guides/tools).
              - **MCP Tools**: Integrations with third-party systems via custom MCP servers or
                predefined connectors such as Google Drive and SharePoint. Learn more about
                [MCP Tools](https://platform.openai.com/docs/guides/tools-connectors-mcp).
              - **Function calls (custom tools)**: Functions that are defined by you, enabling
                the model to call your own code with strongly typed arguments and outputs.
                Learn more about
                [function calling](https://platform.openai.com/docs/guides/function-calling).
                You can also use custom tools to call your own code.

          top_logprobs: An integer between 0 and 20 specifying the number of most likely tokens to
              return at each token position, each with an associated log probability.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or `temperature` but not both.

          truncation: The truncation strategy to use for the model response.

              - `auto`: If the input to this Response exceeds the model's context window size,
                the model will truncate the response to fit the context window by dropping
                items from the beginning of the conversation.
              - `disabled` (default): If the input size will exceed the context window size
                for a model, the request will fail with a 400 error.

          user: This field is being replaced by `safety_identifier` and `prompt_cache_key`. Use
              `prompt_cache_key` instead to maintain caching optimizations. A stable
              identifier for your end-users. Used to boost cache hit rates by better bucketing
              similar requests and to help OpenAI detect and prevent abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).

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
        stream: bool,
        background: Optional[bool] | Omit = omit,
        context_management: Optional[Iterable[response_create_params.ContextManagement]] | Omit = omit,
        conversation: Optional[response_create_params.Conversation] | Omit = omit,
        include: Optional[List[ResponseIncludable]] | Omit = omit,
        input: Union[str, ResponseInputParam] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        max_output_tokens: Optional[int] | Omit = omit,
        max_tool_calls: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        model: ResponsesModel | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt: Optional[ResponsePromptParam] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | Omit = omit,
        reasoning: Optional[Reasoning] | Omit = omit,
        safety_identifier: str | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream_options: Optional[response_create_params.StreamOptions] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        text: ResponseTextConfigParam | Omit = omit,
        tool_choice: response_create_params.ToolChoice | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        truncation: Optional[Literal["auto", "disabled"]] | Omit = omit,
        user: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Response | Stream[ResponseStreamEvent]:
        """Creates a model response.

        Provide
        [text](https://platform.openai.com/docs/guides/text) or
        [image](https://platform.openai.com/docs/guides/images) inputs to generate
        [text](https://platform.openai.com/docs/guides/text) or
        [JSON](https://platform.openai.com/docs/guides/structured-outputs) outputs. Have
        the model call your own
        [custom code](https://platform.openai.com/docs/guides/function-calling) or use
        built-in [tools](https://platform.openai.com/docs/guides/tools) like
        [web search](https://platform.openai.com/docs/guides/tools-web-search) or
        [file search](https://platform.openai.com/docs/guides/tools-file-search) to use
        your own data as input for the model's response.

        Args:
          stream: If set to true, the model response data will be streamed to the client as it is
              generated using
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
              See the
              [Streaming section below](https://platform.openai.com/docs/api-reference/responses-streaming)
              for more information.

          background: Whether to run the model response in the background.
              [Learn more](https://platform.openai.com/docs/guides/background).

          context_management: Context management configuration for this request.

          conversation: The conversation that this response belongs to. Items from this conversation are
              prepended to `input_items` for this response request. Input items and output
              items from this response are automatically added to this conversation after this
              response completes.

          include: Specify additional output data to include in the model response. Currently
              supported values are:

              - `web_search_call.action.sources`: Include the sources of the web search tool
                call.
              - `code_interpreter_call.outputs`: Includes the outputs of python code execution
                in code interpreter tool call items.
              - `computer_call_output.output.image_url`: Include image urls from the computer
                call output.
              - `file_search_call.results`: Include the search results of the file search tool
                call.
              - `message.input_image.image_url`: Include image urls from the input message.
              - `message.output_text.logprobs`: Include logprobs with assistant messages.
              - `reasoning.encrypted_content`: Includes an encrypted version of reasoning
                tokens in reasoning item outputs. This enables reasoning items to be used in
                multi-turn conversations when using the Responses API statelessly (like when
                the `store` parameter is set to `false`, or when an organization is enrolled
                in the zero data retention program).

          input: Text, image, or file inputs to the model, used to generate a response.

              Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Image inputs](https://platform.openai.com/docs/guides/images)
              - [File inputs](https://platform.openai.com/docs/guides/pdf-files)
              - [Conversation state](https://platform.openai.com/docs/guides/conversation-state)
              - [Function calling](https://platform.openai.com/docs/guides/function-calling)

          instructions: A system (or developer) message inserted into the model's context.

              When using along with `previous_response_id`, the instructions from a previous
              response will not be carried over to the next response. This makes it simple to
              swap out system (or developer) messages in new responses.

          max_output_tokens: An upper bound for the number of tokens that can be generated for a response,
              including visible output tokens and
              [reasoning tokens](https://platform.openai.com/docs/guides/reasoning).

          max_tool_calls: The maximum number of total calls to built-in tools that can be processed in a
              response. This maximum number applies across all built-in tool calls, not per
              individual tool. Any further attempts to call a tool by the model will be
              ignored.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format, and
              querying for objects via API or the dashboard.

              Keys are strings with a maximum length of 64 characters. Values are strings with
              a maximum length of 512 characters.

          model: Model ID used to generate the response, like `gpt-4o` or `o3`. OpenAI offers a
              wide range of models with different capabilities, performance characteristics,
              and price points. Refer to the
              [model guide](https://platform.openai.com/docs/models) to browse and compare
              available models.

          parallel_tool_calls: Whether to allow the model to run tool calls in parallel.

          previous_response_id: The unique ID of the previous response to the model. Use this to create
              multi-turn conversations. Learn more about
              [conversation state](https://platform.openai.com/docs/guides/conversation-state).
              Cannot be used in conjunction with `conversation`.

          prompt: Reference to a prompt template and its variables.
              [Learn more](https://platform.openai.com/docs/guides/text?api-mode=responses#reusable-prompts).

          prompt_cache_key: Used by OpenAI to cache responses for similar requests to optimize your cache
              hit rates. Replaces the `user` field.
              [Learn more](https://platform.openai.com/docs/guides/prompt-caching).

          prompt_cache_retention: The retention policy for the prompt cache. Set to `24h` to enable extended
              prompt caching, which keeps cached prefixes active for longer, up to a maximum
              of 24 hours.
              [Learn more](https://platform.openai.com/docs/guides/prompt-caching#prompt-cache-retention).

          reasoning: **gpt-5 and o-series models only**

              Configuration options for
              [reasoning models](https://platform.openai.com/docs/guides/reasoning).

          safety_identifier: A stable identifier used to help detect users of your application that may be
              violating OpenAI's usage policies. The IDs should be a string that uniquely
              identifies each user, with a maximum length of 64 characters. We recommend
              hashing their username or email address, in order to avoid sending us any
              identifying information.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).

          service_tier: Specifies the processing type used for serving the request.

              - If set to 'auto', then the request will be processed with the service tier
                configured in the Project settings. Unless otherwise configured, the Project
                will use 'default'.
              - If set to 'default', then the request will be processed with the standard
                pricing and performance for the selected model.
              - If set to '[flex](https://platform.openai.com/docs/guides/flex-processing)' or
                '[priority](https://openai.com/api-priority-processing/)', then the request
                will be processed with the corresponding service tier.
              - When not set, the default behavior is 'auto'.

              When the `service_tier` parameter is set, the response body will include the
              `service_tier` value based on the processing mode actually used to serve the
              request. This response value may be different from the value set in the
              parameter.

          store: Whether to store the generated model response for later retrieval via API.

          stream_options: Options for streaming responses. Only set this when you set `stream: true`.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic. We generally recommend altering this or `top_p` but
              not both.

          text: Configuration options for a text response from the model. Can be plain text or
              structured JSON data. Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)

          tool_choice: How the model should select which tool (or tools) to use when generating a
              response. See the `tools` parameter to see how to specify which tools the model
              can call.

          tools: An array of tools the model may call while generating a response. You can
              specify which tool to use by setting the `tool_choice` parameter.

              We support the following categories of tools:

              - **Built-in tools**: Tools that are provided by OpenAI that extend the model's
                capabilities, like
                [web search](https://platform.openai.com/docs/guides/tools-web-search) or
                [file search](https://platform.openai.com/docs/guides/tools-file-search).
                Learn more about
                [built-in tools](https://platform.openai.com/docs/guides/tools).
              - **MCP Tools**: Integrations with third-party systems via custom MCP servers or
                predefined connectors such as Google Drive and SharePoint. Learn more about
                [MCP Tools](https://platform.openai.com/docs/guides/tools-connectors-mcp).
              - **Function calls (custom tools)**: Functions that are defined by you, enabling
                the model to call your own code with strongly typed arguments and outputs.
                Learn more about
                [function calling](https://platform.openai.com/docs/guides/function-calling).
                You can also use custom tools to call your own code.

          top_logprobs: An integer between 0 and 20 specifying the number of most likely tokens to
              return at each token position, each with an associated log probability.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or `temperature` but not both.

          truncation: The truncation strategy to use for the model response.

              - `auto`: If the input to this Response exceeds the model's context window size,
                the model will truncate the response to fit the context window by dropping
                items from the beginning of the conversation.
              - `disabled` (default): If the input size will exceed the context window size
                for a model, the request will fail with a 400 error.

          user: This field is being replaced by `safety_identifier` and `prompt_cache_key`. Use
              `prompt_cache_key` instead to maintain caching optimizations. A stable
              identifier for your end-users. Used to boost cache hit rates by better bucketing
              similar requests and to help OpenAI detect and prevent abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    def create(
        self,
        *,
        background: Optional[bool] | Omit = omit,
        context_management: Optional[Iterable[response_create_params.ContextManagement]] | Omit = omit,
        conversation: Optional[response_create_params.Conversation] | Omit = omit,
        include: Optional[List[ResponseIncludable]] | Omit = omit,
        input: Union[str, ResponseInputParam] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        max_output_tokens: Optional[int] | Omit = omit,
        max_tool_calls: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        model: ResponsesModel | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt: Optional[ResponsePromptParam] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | Omit = omit,
        reasoning: Optional[Reasoning] | Omit = omit,
        safety_identifier: str | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream: Optional[Literal[False]] | Literal[True] | Omit = omit,
        stream_options: Optional[response_create_params.StreamOptions] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        text: ResponseTextConfigParam | Omit = omit,
        tool_choice: response_create_params.ToolChoice | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        truncation: Optional[Literal["auto", "disabled"]] | Omit = omit,
        user: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Response | Stream[ResponseStreamEvent]:
        return self._post(
            "/responses",
            body=maybe_transform(
                {
                    "background": background,
                    "context_management": context_management,
                    "conversation": conversation,
                    "include": include,
                    "input": input,
                    "instructions": instructions,
                    "max_output_tokens": max_output_tokens,
                    "max_tool_calls": max_tool_calls,
                    "metadata": metadata,
                    "model": model,
                    "parallel_tool_calls": parallel_tool_calls,
                    "previous_response_id": previous_response_id,
                    "prompt": prompt,
                    "prompt_cache_key": prompt_cache_key,
                    "prompt_cache_retention": prompt_cache_retention,
                    "reasoning": reasoning,
                    "safety_identifier": safety_identifier,
                    "service_tier": service_tier,
                    "store": store,
                    "stream": stream,
                    "stream_options": stream_options,
                    "temperature": temperature,
                    "text": text,
                    "tool_choice": tool_choice,
                    "tools": tools,
                    "top_logprobs": top_logprobs,
                    "top_p": top_p,
                    "truncation": truncation,
                    "user": user,
                },
                response_create_params.ResponseCreateParamsStreaming
                if stream
                else response_create_params.ResponseCreateParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Response,
            stream=stream or False,
            stream_cls=Stream[ResponseStreamEvent],
        )

    @overload
    def stream(
        self,
        *,
        response_id: str,
        text_format: type[TextFormatT] | Omit = omit,
        starting_after: int | Omit = omit,
        tools: Iterable[ParseableToolParam] | Omit = omit,
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseStreamManager[TextFormatT]: ...

    @overload
    def stream(
        self,
        *,
        input: Union[str, ResponseInputParam],
        model: ResponsesModel,
        background: Optional[bool] | Omit = omit,
        context_management: Optional[Iterable[response_create_params.ContextManagement]] | Omit = omit,
        text_format: type[TextFormatT] | Omit = omit,
        tools: Iterable[ParseableToolParam] | Omit = omit,
        conversation: Optional[response_create_params.Conversation] | Omit = omit,
        include: Optional[List[ResponseIncludable]] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        max_output_tokens: Optional[int] | Omit = omit,
        max_tool_calls: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt: Optional[ResponsePromptParam] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | Omit = omit,
        reasoning: Optional[Reasoning] | Omit = omit,
        safety_identifier: str | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream_options: Optional[response_create_params.StreamOptions] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        text: ResponseTextConfigParam | Omit = omit,
        tool_choice: response_create_params.ToolChoice | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        truncation: Optional[Literal["auto", "disabled"]] | Omit = omit,
        user: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseStreamManager[TextFormatT]: ...

    def stream(
        self,
        *,
        response_id: str | Omit = omit,
        input: Union[str, ResponseInputParam] | Omit = omit,
        model: ResponsesModel | Omit = omit,
        background: Optional[bool] | Omit = omit,
        context_management: Optional[Iterable[response_create_params.ContextManagement]] | Omit = omit,
        text_format: type[TextFormatT] | Omit = omit,
        tools: Iterable[ParseableToolParam] | Omit = omit,
        conversation: Optional[response_create_params.Conversation] | Omit = omit,
        include: Optional[List[ResponseIncludable]] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        max_output_tokens: Optional[int] | Omit = omit,
        max_tool_calls: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt: Optional[ResponsePromptParam] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | Omit = omit,
        reasoning: Optional[Reasoning] | Omit = omit,
        safety_identifier: str | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream_options: Optional[response_create_params.StreamOptions] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        text: ResponseTextConfigParam | Omit = omit,
        tool_choice: response_create_params.ToolChoice | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        truncation: Optional[Literal["auto", "disabled"]] | Omit = omit,
        user: str | Omit = omit,
        starting_after: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseStreamManager[TextFormatT]:
        new_response_args = {
            "input": input,
            "model": model,
            "context_management": context_management,
            "conversation": conversation,
            "include": include,
            "instructions": instructions,
            "max_output_tokens": max_output_tokens,
            "max_tool_calls": max_tool_calls,
            "metadata": metadata,
            "parallel_tool_calls": parallel_tool_calls,
            "previous_response_id": previous_response_id,
            "prompt": prompt,
            "prompt_cache_key": prompt_cache_key,
            "prompt_cache_retention": prompt_cache_retention,
            "reasoning": reasoning,
            "safety_identifier": safety_identifier,
            "service_tier": service_tier,
            "store": store,
            "stream_options": stream_options,
            "temperature": temperature,
            "text": text,
            "tool_choice": tool_choice,
            "top_logprobs": top_logprobs,
            "top_p": top_p,
            "truncation": truncation,
            "user": user,
            "background": background,
        }
        new_response_args_names = [k for k, v in new_response_args.items() if is_given(v)]

        if (is_given(response_id) or is_given(starting_after)) and len(new_response_args_names) > 0:
            raise ValueError(
                "Cannot provide both response_id/starting_after can't be provided together with "
                + ", ".join(new_response_args_names)
            )
        tools = _make_tools(tools)
        if len(new_response_args_names) > 0:
            if not is_given(input):
                raise ValueError("input must be provided when creating a new response")

            if not is_given(model):
                raise ValueError("model must be provided when creating a new response")

            if is_given(text_format):
                if not text:
                    text = {}

                if "format" in text:
                    raise TypeError("Cannot mix and match text.format with text_format")

                text = copy(text)
                text["format"] = _type_to_text_format_param(text_format)

            api_request: partial[Stream[ResponseStreamEvent]] = partial(
                self.create,
                input=input,
                model=model,
                tools=tools,
                context_management=context_management,
                conversation=conversation,
                include=include,
                instructions=instructions,
                max_output_tokens=max_output_tokens,
                max_tool_calls=max_tool_calls,
                metadata=metadata,
                parallel_tool_calls=parallel_tool_calls,
                previous_response_id=previous_response_id,
                prompt=prompt,
                prompt_cache_key=prompt_cache_key,
                prompt_cache_retention=prompt_cache_retention,
                store=store,
                stream_options=stream_options,
                stream=True,
                temperature=temperature,
                text=text,
                tool_choice=tool_choice,
                reasoning=reasoning,
                safety_identifier=safety_identifier,
                service_tier=service_tier,
                top_logprobs=top_logprobs,
                top_p=top_p,
                truncation=truncation,
                user=user,
                background=background,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            )

            return ResponseStreamManager(api_request, text_format=text_format, input_tools=tools, starting_after=None)
        else:
            if not is_given(response_id):
                raise ValueError("id must be provided when streaming an existing response")

            return ResponseStreamManager(
                lambda: self.retrieve(
                    response_id=response_id,
                    stream=True,
                    include=include or [],
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    starting_after=omit,
                    timeout=timeout,
                ),
                text_format=text_format,
                input_tools=tools,
                starting_after=starting_after if is_given(starting_after) else None,
            )

    def parse(
        self,
        *,
        text_format: type[TextFormatT] | Omit = omit,
        background: Optional[bool] | Omit = omit,
        context_management: Optional[Iterable[response_create_params.ContextManagement]] | Omit = omit,
        conversation: Optional[response_create_params.Conversation] | Omit = omit,
        include: Optional[List[ResponseIncludable]] | Omit = omit,
        input: Union[str, ResponseInputParam] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        max_output_tokens: Optional[int] | Omit = omit,
        max_tool_calls: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        model: ResponsesModel | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt: Optional[ResponsePromptParam] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | Omit = omit,
        reasoning: Optional[Reasoning] | Omit = omit,
        safety_identifier: str | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream: Optional[Literal[False]] | Literal[True] | Omit = omit,
        stream_options: Optional[response_create_params.StreamOptions] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        text: ResponseTextConfigParam | Omit = omit,
        tool_choice: response_create_params.ToolChoice | Omit = omit,
        tools: Iterable[ParseableToolParam] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        truncation: Optional[Literal["auto", "disabled"]] | Omit = omit,
        user: str | Omit = omit,
        verbosity: Optional[Literal["low", "medium", "high"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ParsedResponse[TextFormatT]:
        if is_given(text_format):
            if not text:
                text = {}

            if "format" in text:
                raise TypeError("Cannot mix and match text.format with text_format")
            text = copy(text)
            text["format"] = _type_to_text_format_param(text_format)

        tools = _make_tools(tools)

        def parser(raw_response: Response) -> ParsedResponse[TextFormatT]:
            return parse_response(
                input_tools=tools,
                text_format=text_format,
                response=raw_response,
            )

        return self._post(
            "/responses",
            body=maybe_transform(
                {
                    "background": background,
                    "context_management": context_management,
                    "conversation": conversation,
                    "include": include,
                    "input": input,
                    "instructions": instructions,
                    "max_output_tokens": max_output_tokens,
                    "max_tool_calls": max_tool_calls,
                    "metadata": metadata,
                    "model": model,
                    "parallel_tool_calls": parallel_tool_calls,
                    "previous_response_id": previous_response_id,
                    "prompt": prompt,
                    "prompt_cache_key": prompt_cache_key,
                    "prompt_cache_retention": prompt_cache_retention,
                    "reasoning": reasoning,
                    "safety_identifier": safety_identifier,
                    "service_tier": service_tier,
                    "store": store,
                    "stream": stream,
                    "stream_options": stream_options,
                    "temperature": temperature,
                    "text": text,
                    "tool_choice": tool_choice,
                    "tools": tools,
                    "top_logprobs": top_logprobs,
                    "top_p": top_p,
                    "truncation": truncation,
                    "user": user,
                    "verbosity": verbosity,
                },
                response_create_params.ResponseCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                post_parser=parser,
            ),
            # we turn the `Response` instance into a `ParsedResponse`
            # in the `parser` function above
            cast_to=cast(Type[ParsedResponse[TextFormatT]], Response),
        )

    @overload
    def retrieve(
        self,
        response_id: str,
        *,
        include: List[ResponseIncludable] | Omit = omit,
        include_obfuscation: bool | Omit = omit,
        starting_after: int | Omit = omit,
        stream: Literal[False] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Response: ...

    @overload
    def retrieve(
        self,
        response_id: str,
        *,
        stream: Literal[True],
        include: List[ResponseIncludable] | Omit = omit,
        starting_after: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Stream[ResponseStreamEvent]: ...

    @overload
    def retrieve(
        self,
        response_id: str,
        *,
        stream: bool,
        include: List[ResponseIncludable] | Omit = omit,
        starting_after: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Response | Stream[ResponseStreamEvent]: ...

    @overload
    def retrieve(
        self,
        response_id: str,
        *,
        stream: bool = False,
        include: List[ResponseIncludable] | Omit = omit,
        starting_after: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Response | Stream[ResponseStreamEvent]:
        """
        Retrieves a model response with the given ID.

        Args:
          include: Additional fields to include in the response. See the `include` parameter for
              Response creation above for more information.

          include_obfuscation: When true, stream obfuscation will be enabled. Stream obfuscation adds random
              characters to an `obfuscation` field on streaming delta events to normalize
              payload sizes as a mitigation to certain side-channel attacks. These obfuscation
              fields are included by default, but add a small amount of overhead to the data
              stream. You can set `include_obfuscation` to false to optimize for bandwidth if
              you trust the network links between your application and the OpenAI API.

          starting_after: The sequence number of the event after which to start streaming.

          stream: If set to true, the model response data will be streamed to the client as it is
              generated using
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
              See the
              [Streaming section below](https://platform.openai.com/docs/api-reference/responses-streaming)
              for more information.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def retrieve(
        self,
        response_id: str,
        *,
        stream: Literal[True],
        include: List[ResponseIncludable] | Omit = omit,
        include_obfuscation: bool | Omit = omit,
        starting_after: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Stream[ResponseStreamEvent]:
        """
        Retrieves a model response with the given ID.

        Args:
          stream: If set to true, the model response data will be streamed to the client as it is
              generated using
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
              See the
              [Streaming section below](https://platform.openai.com/docs/api-reference/responses-streaming)
              for more information.

          include: Additional fields to include in the response. See the `include` parameter for
              Response creation above for more information.

          include_obfuscation: When true, stream obfuscation will be enabled. Stream obfuscation adds random
              characters to an `obfuscation` field on streaming delta events to normalize
              payload sizes as a mitigation to certain side-channel attacks. These obfuscation
              fields are included by default, but add a small amount of overhead to the data
              stream. You can set `include_obfuscation` to false to optimize for bandwidth if
              you trust the network links between your application and the OpenAI API.

          starting_after: The sequence number of the event after which to start streaming.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def retrieve(
        self,
        response_id: str,
        *,
        stream: bool,
        include: List[ResponseIncludable] | Omit = omit,
        include_obfuscation: bool | Omit = omit,
        starting_after: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Response | Stream[ResponseStreamEvent]:
        """
        Retrieves a model response with the given ID.

        Args:
          stream: If set to true, the model response data will be streamed to the client as it is
              generated using
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
              See the
              [Streaming section below](https://platform.openai.com/docs/api-reference/responses-streaming)
              for more information.

          include: Additional fields to include in the response. See the `include` parameter for
              Response creation above for more information.

          include_obfuscation: When true, stream obfuscation will be enabled. Stream obfuscation adds random
              characters to an `obfuscation` field on streaming delta events to normalize
              payload sizes as a mitigation to certain side-channel attacks. These obfuscation
              fields are included by default, but add a small amount of overhead to the data
              stream. You can set `include_obfuscation` to false to optimize for bandwidth if
              you trust the network links between your application and the OpenAI API.

          starting_after: The sequence number of the event after which to start streaming.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    def retrieve(
        self,
        response_id: str,
        *,
        include: List[ResponseIncludable] | Omit = omit,
        include_obfuscation: bool | Omit = omit,
        starting_after: int | Omit = omit,
        stream: Literal[False] | Literal[True] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Response | Stream[ResponseStreamEvent]:
        if not response_id:
            raise ValueError(f"Expected a non-empty value for `response_id` but received {response_id!r}")
        return self._get(
            path_template("/responses/{response_id}", response_id=response_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "include": include,
                        "include_obfuscation": include_obfuscation,
                        "starting_after": starting_after,
                        "stream": stream,
                    },
                    response_retrieve_params.ResponseRetrieveParams,
                ),
            ),
            cast_to=Response,
            stream=stream or False,
            stream_cls=Stream[ResponseStreamEvent],
        )

    def delete(
        self,
        response_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Deletes a model response with the given ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not response_id:
            raise ValueError(f"Expected a non-empty value for `response_id` but received {response_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            path_template("/responses/{response_id}", response_id=response_id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def cancel(
        self,
        response_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Response:
        """Cancels a model response with the given ID.

        Only responses created with the
        `background` parameter set to `true` can be cancelled.
        [Learn more](https://platform.openai.com/docs/guides/background).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not response_id:
            raise ValueError(f"Expected a non-empty value for `response_id` but received {response_id!r}")
        return self._post(
            path_template("/responses/{response_id}/cancel", response_id=response_id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Response,
        )

    def compact(
        self,
        *,
        model: Union[
            Literal[
                "gpt-5.4",
                "gpt-5.4-mini",
                "gpt-5.4-nano",
                "gpt-5.4-mini-2026-03-17",
                "gpt-5.4-nano-2026-03-17",
                "gpt-5.3-chat-latest",
                "gpt-5.2",
                "gpt-5.2-2025-12-11",
                "gpt-5.2-chat-latest",
                "gpt-5.2-pro",
                "gpt-5.2-pro-2025-12-11",
                "gpt-5.1",
                "gpt-5.1-2025-11-13",
                "gpt-5.1-codex",
                "gpt-5.1-mini",
                "gpt-5.1-chat-latest",
                "gpt-5",
                "gpt-5-mini",
                "gpt-5-nano",
                "gpt-5-2025-08-07",
                "gpt-5-mini-2025-08-07",
                "gpt-5-nano-2025-08-07",
                "gpt-5-chat-latest",
                "gpt-4.1",
                "gpt-4.1-mini",
                "gpt-4.1-nano",
                "gpt-4.1-2025-04-14",
                "gpt-4.1-mini-2025-04-14",
                "gpt-4.1-nano-2025-04-14",
                "o4-mini",
                "o4-mini-2025-04-16",
                "o3",
                "o3-2025-04-16",
                "o3-mini",
                "o3-mini-2025-01-31",
                "o1",
                "o1-2024-12-17",
                "o1-preview",
                "o1-preview-2024-09-12",
                "o1-mini",
                "o1-mini-2024-09-12",
                "gpt-4o",
                "gpt-4o-2024-11-20",
                "gpt-4o-2024-08-06",
                "gpt-4o-2024-05-13",
                "gpt-4o-audio-preview",
                "gpt-4o-audio-preview-2024-10-01",
                "gpt-4o-audio-preview-2024-12-17",
                "gpt-4o-audio-preview-2025-06-03",
                "gpt-4o-mini-audio-preview",
                "gpt-4o-mini-audio-preview-2024-12-17",
                "gpt-4o-search-preview",
                "gpt-4o-mini-search-preview",
                "gpt-4o-search-preview-2025-03-11",
                "gpt-4o-mini-search-preview-2025-03-11",
                "chatgpt-4o-latest",
                "codex-mini-latest",
                "gpt-4o-mini",
                "gpt-4o-mini-2024-07-18",
                "gpt-4-turbo",
                "gpt-4-turbo-2024-04-09",
                "gpt-4-0125-preview",
                "gpt-4-turbo-preview",
                "gpt-4-1106-preview",
                "gpt-4-vision-preview",
                "gpt-4",
                "gpt-4-0314",
                "gpt-4-0613",
                "gpt-4-32k",
                "gpt-4-32k-0314",
                "gpt-4-32k-0613",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k",
                "gpt-3.5-turbo-0301",
                "gpt-3.5-turbo-0613",
                "gpt-3.5-turbo-1106",
                "gpt-3.5-turbo-0125",
                "gpt-3.5-turbo-16k-0613",
                "o1-pro",
                "o1-pro-2025-03-19",
                "o3-pro",
                "o3-pro-2025-06-10",
                "o3-deep-research",
                "o3-deep-research-2025-06-26",
                "o4-mini-deep-research",
                "o4-mini-deep-research-2025-06-26",
                "computer-use-preview",
                "computer-use-preview-2025-03-11",
                "gpt-5-codex",
                "gpt-5-pro",
                "gpt-5-pro-2025-10-06",
                "gpt-5.1-codex-max",
            ],
            str,
            None,
        ],
        input: Union[str, Iterable[ResponseInputItemParam], None] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt_cache_key: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CompactedResponse:
        """Compact a conversation.

        Returns a compacted response object.

        Learn when and how to compact long-running conversations in the
        [conversation state guide](https://platform.openai.com/docs/guides/conversation-state#managing-the-context-window).
        For ZDR-compatible compaction details, see
        [Compaction (advanced)](https://platform.openai.com/docs/guides/conversation-state#compaction-advanced).

        Args:
          model: Model ID used to generate the response, like `gpt-5` or `o3`. OpenAI offers a
              wide range of models with different capabilities, performance characteristics,
              and price points. Refer to the
              [model guide](https://platform.openai.com/docs/models) to browse and compare
              available models.

          input: Text, image, or file inputs to the model, used to generate a response

          instructions: A system (or developer) message inserted into the model's context. When used
              along with `previous_response_id`, the instructions from a previous response
              will not be carried over to the next response. This makes it simple to swap out
              system (or developer) messages in new responses.

          previous_response_id: The unique ID of the previous response to the model. Use this to create
              multi-turn conversations. Learn more about
              [conversation state](https://platform.openai.com/docs/guides/conversation-state).
              Cannot be used in conjunction with `conversation`.

          prompt_cache_key: A key to use when reading from or writing to the prompt cache.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/responses/compact",
            body=maybe_transform(
                {
                    "model": model,
                    "input": input,
                    "instructions": instructions,
                    "previous_response_id": previous_response_id,
                    "prompt_cache_key": prompt_cache_key,
                },
                response_compact_params.ResponseCompactParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CompactedResponse,
        )

    def connect(
        self,
        extra_query: Query = {},
        extra_headers: Headers = {},
        websocket_connection_options: WebSocketConnectionOptions = {},
        on_reconnecting: Callable[[ReconnectingEvent], ReconnectingOverrides | None] | None = None,
        max_retries: int = 5,
        initial_delay: float = 0.5,
        max_delay: float = 8.0,
        max_queue_size: int = 1_048_576,
    ) -> ResponsesConnectionManager:
        """Connect to a persistent Responses API WebSocket.

        Send `response.create` events and receive response stream events over the socket.
        """
        return ResponsesConnectionManager(
            client=self._client,
            extra_query=extra_query,
            extra_headers=extra_headers,
            websocket_connection_options=websocket_connection_options,
            on_reconnecting=on_reconnecting,
            max_retries=max_retries,
            initial_delay=initial_delay,
            max_delay=max_delay,
            max_queue_size=max_queue_size,
        )


class AsyncResponses(AsyncAPIResource):
    @cached_property
    def input_items(self) -> AsyncInputItems:
        return AsyncInputItems(self._client)

    @cached_property
    def input_tokens(self) -> AsyncInputTokens:
        return AsyncInputTokens(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncResponsesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncResponsesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncResponsesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncResponsesWithStreamingResponse(self)

    @overload
    async def create(
        self,
        *,
        background: Optional[bool] | Omit = omit,
        context_management: Optional[Iterable[response_create_params.ContextManagement]] | Omit = omit,
        conversation: Optional[response_create_params.Conversation] | Omit = omit,
        include: Optional[List[ResponseIncludable]] | Omit = omit,
        input: Union[str, ResponseInputParam] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        max_output_tokens: Optional[int] | Omit = omit,
        max_tool_calls: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        model: ResponsesModel | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt: Optional[ResponsePromptParam] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | Omit = omit,
        reasoning: Optional[Reasoning] | Omit = omit,
        safety_identifier: str | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream: Optional[Literal[False]] | Omit = omit,
        stream_options: Optional[response_create_params.StreamOptions] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        text: ResponseTextConfigParam | Omit = omit,
        tool_choice: response_create_params.ToolChoice | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        truncation: Optional[Literal["auto", "disabled"]] | Omit = omit,
        user: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Response:
        """Creates a model response.

        Provide
        [text](https://platform.openai.com/docs/guides/text) or
        [image](https://platform.openai.com/docs/guides/images) inputs to generate
        [text](https://platform.openai.com/docs/guides/text) or
        [JSON](https://platform.openai.com/docs/guides/structured-outputs) outputs. Have
        the model call your own
        [custom code](https://platform.openai.com/docs/guides/function-calling) or use
        built-in [tools](https://platform.openai.com/docs/guides/tools) like
        [web search](https://platform.openai.com/docs/guides/tools-web-search) or
        [file search](https://platform.openai.com/docs/guides/tools-file-search) to use
        your own data as input for the model's response.

        Args:
          background: Whether to run the model response in the background.
              [Learn more](https://platform.openai.com/docs/guides/background).

          context_management: Context management configuration for this request.

          conversation: The conversation that this response belongs to. Items from this conversation are
              prepended to `input_items` for this response request. Input items and output
              items from this response are automatically added to this conversation after this
              response completes.

          include: Specify additional output data to include in the model response. Currently
              supported values are:

              - `web_search_call.action.sources`: Include the sources of the web search tool
                call.
              - `code_interpreter_call.outputs`: Includes the outputs of python code execution
                in code interpreter tool call items.
              - `computer_call_output.output.image_url`: Include image urls from the computer
                call output.
              - `file_search_call.results`: Include the search results of the file search tool
                call.
              - `message.input_image.image_url`: Include image urls from the input message.
              - `message.output_text.logprobs`: Include logprobs with assistant messages.
              - `reasoning.encrypted_content`: Includes an encrypted version of reasoning
                tokens in reasoning item outputs. This enables reasoning items to be used in
                multi-turn conversations when using the Responses API statelessly (like when
                the `store` parameter is set to `false`, or when an organization is enrolled
                in the zero data retention program).

          input: Text, image, or file inputs to the model, used to generate a response.

              Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Image inputs](https://platform.openai.com/docs/guides/images)
              - [File inputs](https://platform.openai.com/docs/guides/pdf-files)
              - [Conversation state](https://platform.openai.com/docs/guides/conversation-state)
              - [Function calling](https://platform.openai.com/docs/guides/function-calling)

          instructions: A system (or developer) message inserted into the model's context.

              When using along with `previous_response_id`, the instructions from a previous
              response will not be carried over to the next response. This makes it simple to
              swap out system (or developer) messages in new responses.

          max_output_tokens: An upper bound for the number of tokens that can be generated for a response,
              including visible output tokens and
              [reasoning tokens](https://platform.openai.com/docs/guides/reasoning).

          max_tool_calls: The maximum number of total calls to built-in tools that can be processed in a
              response. This maximum number applies across all built-in tool calls, not per
              individual tool. Any further attempts to call a tool by the model will be
              ignored.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format, and
              querying for objects via API or the dashboard.

              Keys are strings with a maximum length of 64 characters. Values are strings with
              a maximum length of 512 characters.

          model: Model ID used to generate the response, like `gpt-4o` or `o3`. OpenAI offers a
              wide range of models with different capabilities, performance characteristics,
              and price points. Refer to the
              [model guide](https://platform.openai.com/docs/models) to browse and compare
              available models.

          parallel_tool_calls: Whether to allow the model to run tool calls in parallel.

          previous_response_id: The unique ID of the previous response to the model. Use this to create
              multi-turn conversations. Learn more about
              [conversation state](https://platform.openai.com/docs/guides/conversation-state).
              Cannot be used in conjunction with `conversation`.

          prompt: Reference to a prompt template and its variables.
              [Learn more](https://platform.openai.com/docs/guides/text?api-mode=responses#reusable-prompts).

          prompt_cache_key: Used by OpenAI to cache responses for similar requests to optimize your cache
              hit rates. Replaces the `user` field.
              [Learn more](https://platform.openai.com/docs/guides/prompt-caching).

          prompt_cache_retention: The retention policy for the prompt cache. Set to `24h` to enable extended
              prompt caching, which keeps cached prefixes active for longer, up to a maximum
              of 24 hours.
              [Learn more](https://platform.openai.com/docs/guides/prompt-caching#prompt-cache-retention).

          reasoning: **gpt-5 and o-series models only**

              Configuration options for
              [reasoning models](https://platform.openai.com/docs/guides/reasoning).

          safety_identifier: A stable identifier used to help detect users of your application that may be
              violating OpenAI's usage policies. The IDs should be a string that uniquely
              identifies each user, with a maximum length of 64 characters. We recommend
              hashing their username or email address, in order to avoid sending us any
              identifying information.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).

          service_tier: Specifies the processing type used for serving the request.

              - If set to 'auto', then the request will be processed with the service tier
                configured in the Project settings. Unless otherwise configured, the Project
                will use 'default'.
              - If set to 'default', then the request will be processed with the standard
                pricing and performance for the selected model.
              - If set to '[flex](https://platform.openai.com/docs/guides/flex-processing)' or
                '[priority](https://openai.com/api-priority-processing/)', then the request
                will be processed with the corresponding service tier.
              - When not set, the default behavior is 'auto'.

              When the `service_tier` parameter is set, the response body will include the
              `service_tier` value based on the processing mode actually used to serve the
              request. This response value may be different from the value set in the
              parameter.

          store: Whether to store the generated model response for later retrieval via API.

          stream: If set to true, the model response data will be streamed to the client as it is
              generated using
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
              See the
              [Streaming section below](https://platform.openai.com/docs/api-reference/responses-streaming)
              for more information.

          stream_options: Options for streaming responses. Only set this when you set `stream: true`.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic. We generally recommend altering this or `top_p` but
              not both.

          text: Configuration options for a text response from the model. Can be plain text or
              structured JSON data. Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)

          tool_choice: How the model should select which tool (or tools) to use when generating a
              response. See the `tools` parameter to see how to specify which tools the model
              can call.

          tools: An array of tools the model may call while generating a response. You can
              specify which tool to use by setting the `tool_choice` parameter.

              We support the following categories of tools:

              - **Built-in tools**: Tools that are provided by OpenAI that extend the model's
                capabilities, like
                [web search](https://platform.openai.com/docs/guides/tools-web-search) or
                [file search](https://platform.openai.com/docs/guides/tools-file-search).
                Learn more about
                [built-in tools](https://platform.openai.com/docs/guides/tools).
              - **MCP Tools**: Integrations with third-party systems via custom MCP servers or
                predefined connectors such as Google Drive and SharePoint. Learn more about
                [MCP Tools](https://platform.openai.com/docs/guides/tools-connectors-mcp).
              - **Function calls (custom tools)**: Functions that are defined by you, enabling
                the model to call your own code with strongly typed arguments and outputs.
                Learn more about
                [function calling](https://platform.openai.com/docs/guides/function-calling).
                You can also use custom tools to call your own code.

          top_logprobs: An integer between 0 and 20 specifying the number of most likely tokens to
              return at each token position, each with an associated log probability.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or `temperature` but not both.

          truncation: The truncation strategy to use for the model response.

              - `auto`: If the input to this Response exceeds the model's context window size,
                the model will truncate the response to fit the context window by dropping
                items from the beginning of the conversation.
              - `disabled` (default): If the input size will exceed the context window size
                for a model, the request will fail with a 400 error.

          user: This field is being replaced by `safety_identifier` and `prompt_cache_key`. Use
              `prompt_cache_key` instead to maintain caching optimizations. A stable
              identifier for your end-users. Used to boost cache hit rates by better bucketing
              similar requests and to help OpenAI detect and prevent abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).

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
        stream: Literal[True],
        background: Optional[bool] | Omit = omit,
        context_management: Optional[Iterable[response_create_params.ContextManagement]] | Omit = omit,
        conversation: Optional[response_create_params.Conversation] | Omit = omit,
        include: Optional[List[ResponseIncludable]] | Omit = omit,
        input: Union[str, ResponseInputParam] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        max_output_tokens: Optional[int] | Omit = omit,
        max_tool_calls: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        model: ResponsesModel | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt: Optional[ResponsePromptParam] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | Omit = omit,
        reasoning: Optional[Reasoning] | Omit = omit,
        safety_identifier: str | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream_options: Optional[response_create_params.StreamOptions] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        text: ResponseTextConfigParam | Omit = omit,
        tool_choice: response_create_params.ToolChoice | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        truncation: Optional[Literal["auto", "disabled"]] | Omit = omit,
        user: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncStream[ResponseStreamEvent]:
        """Creates a model response.

        Provide
        [text](https://platform.openai.com/docs/guides/text) or
        [image](https://platform.openai.com/docs/guides/images) inputs to generate
        [text](https://platform.openai.com/docs/guides/text) or
        [JSON](https://platform.openai.com/docs/guides/structured-outputs) outputs. Have
        the model call your own
        [custom code](https://platform.openai.com/docs/guides/function-calling) or use
        built-in [tools](https://platform.openai.com/docs/guides/tools) like
        [web search](https://platform.openai.com/docs/guides/tools-web-search) or
        [file search](https://platform.openai.com/docs/guides/tools-file-search) to use
        your own data as input for the model's response.

        Args:
          stream: If set to true, the model response data will be streamed to the client as it is
              generated using
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
              See the
              [Streaming section below](https://platform.openai.com/docs/api-reference/responses-streaming)
              for more information.

          background: Whether to run the model response in the background.
              [Learn more](https://platform.openai.com/docs/guides/background).

          context_management: Context management configuration for this request.

          conversation: The conversation that this response belongs to. Items from this conversation are
              prepended to `input_items` for this response request. Input items and output
              items from this response are automatically added to this conversation after this
              response completes.

          include: Specify additional output data to include in the model response. Currently
              supported values are:

              - `web_search_call.action.sources`: Include the sources of the web search tool
                call.
              - `code_interpreter_call.outputs`: Includes the outputs of python code execution
                in code interpreter tool call items.
              - `computer_call_output.output.image_url`: Include image urls from the computer
                call output.
              - `file_search_call.results`: Include the search results of the file search tool
                call.
              - `message.input_image.image_url`: Include image urls from the input message.
              - `message.output_text.logprobs`: Include logprobs with assistant messages.
              - `reasoning.encrypted_content`: Includes an encrypted version of reasoning
                tokens in reasoning item outputs. This enables reasoning items to be used in
                multi-turn conversations when using the Responses API statelessly (like when
                the `store` parameter is set to `false`, or when an organization is enrolled
                in the zero data retention program).

          input: Text, image, or file inputs to the model, used to generate a response.

              Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Image inputs](https://platform.openai.com/docs/guides/images)
              - [File inputs](https://platform.openai.com/docs/guides/pdf-files)
              - [Conversation state](https://platform.openai.com/docs/guides/conversation-state)
              - [Function calling](https://platform.openai.com/docs/guides/function-calling)

          instructions: A system (or developer) message inserted into the model's context.

              When using along with `previous_response_id`, the instructions from a previous
              response will not be carried over to the next response. This makes it simple to
              swap out system (or developer) messages in new responses.

          max_output_tokens: An upper bound for the number of tokens that can be generated for a response,
              including visible output tokens and
              [reasoning tokens](https://platform.openai.com/docs/guides/reasoning).

          max_tool_calls: The maximum number of total calls to built-in tools that can be processed in a
              response. This maximum number applies across all built-in tool calls, not per
              individual tool. Any further attempts to call a tool by the model will be
              ignored.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format, and
              querying for objects via API or the dashboard.

              Keys are strings with a maximum length of 64 characters. Values are strings with
              a maximum length of 512 characters.

          model: Model ID used to generate the response, like `gpt-4o` or `o3`. OpenAI offers a
              wide range of models with different capabilities, performance characteristics,
              and price points. Refer to the
              [model guide](https://platform.openai.com/docs/models) to browse and compare
              available models.

          parallel_tool_calls: Whether to allow the model to run tool calls in parallel.

          previous_response_id: The unique ID of the previous response to the model. Use this to create
              multi-turn conversations. Learn more about
              [conversation state](https://platform.openai.com/docs/guides/conversation-state).
              Cannot be used in conjunction with `conversation`.

          prompt: Reference to a prompt template and its variables.
              [Learn more](https://platform.openai.com/docs/guides/text?api-mode=responses#reusable-prompts).

          prompt_cache_key: Used by OpenAI to cache responses for similar requests to optimize your cache
              hit rates. Replaces the `user` field.
              [Learn more](https://platform.openai.com/docs/guides/prompt-caching).

          prompt_cache_retention: The retention policy for the prompt cache. Set to `24h` to enable extended
              prompt caching, which keeps cached prefixes active for longer, up to a maximum
              of 24 hours.
              [Learn more](https://platform.openai.com/docs/guides/prompt-caching#prompt-cache-retention).

          reasoning: **gpt-5 and o-series models only**

              Configuration options for
              [reasoning models](https://platform.openai.com/docs/guides/reasoning).

          safety_identifier: A stable identifier used to help detect users of your application that may be
              violating OpenAI's usage policies. The IDs should be a string that uniquely
              identifies each user, with a maximum length of 64 characters. We recommend
              hashing their username or email address, in order to avoid sending us any
              identifying information.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).

          service_tier: Specifies the processing type used for serving the request.

              - If set to 'auto', then the request will be processed with the service tier
                configured in the Project settings. Unless otherwise configured, the Project
                will use 'default'.
              - If set to 'default', then the request will be processed with the standard
                pricing and performance for the selected model.
              - If set to '[flex](https://platform.openai.com/docs/guides/flex-processing)' or
                '[priority](https://openai.com/api-priority-processing/)', then the request
                will be processed with the corresponding service tier.
              - When not set, the default behavior is 'auto'.

              When the `service_tier` parameter is set, the response body will include the
              `service_tier` value based on the processing mode actually used to serve the
              request. This response value may be different from the value set in the
              parameter.

          store: Whether to store the generated model response for later retrieval via API.

          stream_options: Options for streaming responses. Only set this when you set `stream: true`.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic. We generally recommend altering this or `top_p` but
              not both.

          text: Configuration options for a text response from the model. Can be plain text or
              structured JSON data. Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)

          tool_choice: How the model should select which tool (or tools) to use when generating a
              response. See the `tools` parameter to see how to specify which tools the model
              can call.

          tools: An array of tools the model may call while generating a response. You can
              specify which tool to use by setting the `tool_choice` parameter.

              We support the following categories of tools:

              - **Built-in tools**: Tools that are provided by OpenAI that extend the model's
                capabilities, like
                [web search](https://platform.openai.com/docs/guides/tools-web-search) or
                [file search](https://platform.openai.com/docs/guides/tools-file-search).
                Learn more about
                [built-in tools](https://platform.openai.com/docs/guides/tools).
              - **MCP Tools**: Integrations with third-party systems via custom MCP servers or
                predefined connectors such as Google Drive and SharePoint. Learn more about
                [MCP Tools](https://platform.openai.com/docs/guides/tools-connectors-mcp).
              - **Function calls (custom tools)**: Functions that are defined by you, enabling
                the model to call your own code with strongly typed arguments and outputs.
                Learn more about
                [function calling](https://platform.openai.com/docs/guides/function-calling).
                You can also use custom tools to call your own code.

          top_logprobs: An integer between 0 and 20 specifying the number of most likely tokens to
              return at each token position, each with an associated log probability.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or `temperature` but not both.

          truncation: The truncation strategy to use for the model response.

              - `auto`: If the input to this Response exceeds the model's context window size,
                the model will truncate the response to fit the context window by dropping
                items from the beginning of the conversation.
              - `disabled` (default): If the input size will exceed the context window size
                for a model, the request will fail with a 400 error.

          user: This field is being replaced by `safety_identifier` and `prompt_cache_key`. Use
              `prompt_cache_key` instead to maintain caching optimizations. A stable
              identifier for your end-users. Used to boost cache hit rates by better bucketing
              similar requests and to help OpenAI detect and prevent abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).

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
        stream: bool,
        background: Optional[bool] | Omit = omit,
        context_management: Optional[Iterable[response_create_params.ContextManagement]] | Omit = omit,
        conversation: Optional[response_create_params.Conversation] | Omit = omit,
        include: Optional[List[ResponseIncludable]] | Omit = omit,
        input: Union[str, ResponseInputParam] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        max_output_tokens: Optional[int] | Omit = omit,
        max_tool_calls: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        model: ResponsesModel | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt: Optional[ResponsePromptParam] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | Omit = omit,
        reasoning: Optional[Reasoning] | Omit = omit,
        safety_identifier: str | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream_options: Optional[response_create_params.StreamOptions] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        text: ResponseTextConfigParam | Omit = omit,
        tool_choice: response_create_params.ToolChoice | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        truncation: Optional[Literal["auto", "disabled"]] | Omit = omit,
        user: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Response | AsyncStream[ResponseStreamEvent]:
        """Creates a model response.

        Provide
        [text](https://platform.openai.com/docs/guides/text) or
        [image](https://platform.openai.com/docs/guides/images) inputs to generate
        [text](https://platform.openai.com/docs/guides/text) or
        [JSON](https://platform.openai.com/docs/guides/structured-outputs) outputs. Have
        the model call your own
        [custom code](https://platform.openai.com/docs/guides/function-calling) or use
        built-in [tools](https://platform.openai.com/docs/guides/tools) like
        [web search](https://platform.openai.com/docs/guides/tools-web-search) or
        [file search](https://platform.openai.com/docs/guides/tools-file-search) to use
        your own data as input for the model's response.

        Args:
          stream: If set to true, the model response data will be streamed to the client as it is
              generated using
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
              See the
              [Streaming section below](https://platform.openai.com/docs/api-reference/responses-streaming)
              for more information.

          background: Whether to run the model response in the background.
              [Learn more](https://platform.openai.com/docs/guides/background).

          context_management: Context management configuration for this request.

          conversation: The conversation that this response belongs to. Items from this conversation are
              prepended to `input_items` for this response request. Input items and output
              items from this response are automatically added to this conversation after this
              response completes.

          include: Specify additional output data to include in the model response. Currently
              supported values are:

              - `web_search_call.action.sources`: Include the sources of the web search tool
                call.
              - `code_interpreter_call.outputs`: Includes the outputs of python code execution
                in code interpreter tool call items.
              - `computer_call_output.output.image_url`: Include image urls from the computer
                call output.
              - `file_search_call.results`: Include the search results of the file search tool
                call.
              - `message.input_image.image_url`: Include image urls from the input message.
              - `message.output_text.logprobs`: Include logprobs with assistant messages.
              - `reasoning.encrypted_content`: Includes an encrypted version of reasoning
                tokens in reasoning item outputs. This enables reasoning items to be used in
                multi-turn conversations when using the Responses API statelessly (like when
                the `store` parameter is set to `false`, or when an organization is enrolled
                in the zero data retention program).

          input: Text, image, or file inputs to the model, used to generate a response.

              Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Image inputs](https://platform.openai.com/docs/guides/images)
              - [File inputs](https://platform.openai.com/docs/guides/pdf-files)
              - [Conversation state](https://platform.openai.com/docs/guides/conversation-state)
              - [Function calling](https://platform.openai.com/docs/guides/function-calling)

          instructions: A system (or developer) message inserted into the model's context.

              When using along with `previous_response_id`, the instructions from a previous
              response will not be carried over to the next response. This makes it simple to
              swap out system (or developer) messages in new responses.

          max_output_tokens: An upper bound for the number of tokens that can be generated for a response,
              including visible output tokens and
              [reasoning tokens](https://platform.openai.com/docs/guides/reasoning).

          max_tool_calls: The maximum number of total calls to built-in tools that can be processed in a
              response. This maximum number applies across all built-in tool calls, not per
              individual tool. Any further attempts to call a tool by the model will be
              ignored.

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format, and
              querying for objects via API or the dashboard.

              Keys are strings with a maximum length of 64 characters. Values are strings with
              a maximum length of 512 characters.

          model: Model ID used to generate the response, like `gpt-4o` or `o3`. OpenAI offers a
              wide range of models with different capabilities, performance characteristics,
              and price points. Refer to the
              [model guide](https://platform.openai.com/docs/models) to browse and compare
              available models.

          parallel_tool_calls: Whether to allow the model to run tool calls in parallel.

          previous_response_id: The unique ID of the previous response to the model. Use this to create
              multi-turn conversations. Learn more about
              [conversation state](https://platform.openai.com/docs/guides/conversation-state).
              Cannot be used in conjunction with `conversation`.

          prompt: Reference to a prompt template and its variables.
              [Learn more](https://platform.openai.com/docs/guides/text?api-mode=responses#reusable-prompts).

          prompt_cache_key: Used by OpenAI to cache responses for similar requests to optimize your cache
              hit rates. Replaces the `user` field.
              [Learn more](https://platform.openai.com/docs/guides/prompt-caching).

          prompt_cache_retention: The retention policy for the prompt cache. Set to `24h` to enable extended
              prompt caching, which keeps cached prefixes active for longer, up to a maximum
              of 24 hours.
              [Learn more](https://platform.openai.com/docs/guides/prompt-caching#prompt-cache-retention).

          reasoning: **gpt-5 and o-series models only**

              Configuration options for
              [reasoning models](https://platform.openai.com/docs/guides/reasoning).

          safety_identifier: A stable identifier used to help detect users of your application that may be
              violating OpenAI's usage policies. The IDs should be a string that uniquely
              identifies each user, with a maximum length of 64 characters. We recommend
              hashing their username or email address, in order to avoid sending us any
              identifying information.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).

          service_tier: Specifies the processing type used for serving the request.

              - If set to 'auto', then the request will be processed with the service tier
                configured in the Project settings. Unless otherwise configured, the Project
                will use 'default'.
              - If set to 'default', then the request will be processed with the standard
                pricing and performance for the selected model.
              - If set to '[flex](https://platform.openai.com/docs/guides/flex-processing)' or
                '[priority](https://openai.com/api-priority-processing/)', then the request
                will be processed with the corresponding service tier.
              - When not set, the default behavior is 'auto'.

              When the `service_tier` parameter is set, the response body will include the
              `service_tier` value based on the processing mode actually used to serve the
              request. This response value may be different from the value set in the
              parameter.

          store: Whether to store the generated model response for later retrieval via API.

          stream_options: Options for streaming responses. Only set this when you set `stream: true`.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic. We generally recommend altering this or `top_p` but
              not both.

          text: Configuration options for a text response from the model. Can be plain text or
              structured JSON data. Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)

          tool_choice: How the model should select which tool (or tools) to use when generating a
              response. See the `tools` parameter to see how to specify which tools the model
              can call.

          tools: An array of tools the model may call while generating a response. You can
              specify which tool to use by setting the `tool_choice` parameter.

              We support the following categories of tools:

              - **Built-in tools**: Tools that are provided by OpenAI that extend the model's
                capabilities, like
                [web search](https://platform.openai.com/docs/guides/tools-web-search) or
                [file search](https://platform.openai.com/docs/guides/tools-file-search).
                Learn more about
                [built-in tools](https://platform.openai.com/docs/guides/tools).
              - **MCP Tools**: Integrations with third-party systems via custom MCP servers or
                predefined connectors such as Google Drive and SharePoint. Learn more about
                [MCP Tools](https://platform.openai.com/docs/guides/tools-connectors-mcp).
              - **Function calls (custom tools)**: Functions that are defined by you, enabling
                the model to call your own code with strongly typed arguments and outputs.
                Learn more about
                [function calling](https://platform.openai.com/docs/guides/function-calling).
                You can also use custom tools to call your own code.

          top_logprobs: An integer between 0 and 20 specifying the number of most likely tokens to
              return at each token position, each with an associated log probability.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or `temperature` but not both.

          truncation: The truncation strategy to use for the model response.

              - `auto`: If the input to this Response exceeds the model's context window size,
                the model will truncate the response to fit the context window by dropping
                items from the beginning of the conversation.
              - `disabled` (default): If the input size will exceed the context window size
                for a model, the request will fail with a 400 error.

          user: This field is being replaced by `safety_identifier` and `prompt_cache_key`. Use
              `prompt_cache_key` instead to maintain caching optimizations. A stable
              identifier for your end-users. Used to boost cache hit rates by better bucketing
              similar requests and to help OpenAI detect and prevent abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#safety-identifiers).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    async def create(
        self,
        *,
        background: Optional[bool] | Omit = omit,
        context_management: Optional[Iterable[response_create_params.ContextManagement]] | Omit = omit,
        conversation: Optional[response_create_params.Conversation] | Omit = omit,
        include: Optional[List[ResponseIncludable]] | Omit = omit,
        input: Union[str, ResponseInputParam] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        max_output_tokens: Optional[int] | Omit = omit,
        max_tool_calls: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        model: ResponsesModel | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt: Optional[ResponsePromptParam] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | Omit = omit,
        reasoning: Optional[Reasoning] | Omit = omit,
        safety_identifier: str | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream: Optional[Literal[False]] | Literal[True] | Omit = omit,
        stream_options: Optional[response_create_params.StreamOptions] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        text: ResponseTextConfigParam | Omit = omit,
        tool_choice: response_create_params.ToolChoice | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        truncation: Optional[Literal["auto", "disabled"]] | Omit = omit,
        user: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Response | AsyncStream[ResponseStreamEvent]:
        return await self._post(
            "/responses",
            body=await async_maybe_transform(
                {
                    "background": background,
                    "context_management": context_management,
                    "conversation": conversation,
                    "include": include,
                    "input": input,
                    "instructions": instructions,
                    "max_output_tokens": max_output_tokens,
                    "max_tool_calls": max_tool_calls,
                    "metadata": metadata,
                    "model": model,
                    "parallel_tool_calls": parallel_tool_calls,
                    "previous_response_id": previous_response_id,
                    "prompt": prompt,
                    "prompt_cache_key": prompt_cache_key,
                    "prompt_cache_retention": prompt_cache_retention,
                    "reasoning": reasoning,
                    "safety_identifier": safety_identifier,
                    "service_tier": service_tier,
                    "store": store,
                    "stream": stream,
                    "stream_options": stream_options,
                    "temperature": temperature,
                    "text": text,
                    "tool_choice": tool_choice,
                    "tools": tools,
                    "top_logprobs": top_logprobs,
                    "top_p": top_p,
                    "truncation": truncation,
                    "user": user,
                },
                response_create_params.ResponseCreateParamsStreaming
                if stream
                else response_create_params.ResponseCreateParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Response,
            stream=stream or False,
            stream_cls=AsyncStream[ResponseStreamEvent],
        )

    @overload
    def stream(
        self,
        *,
        response_id: str,
        text_format: type[TextFormatT] | Omit = omit,
        starting_after: int | Omit = omit,
        tools: Iterable[ParseableToolParam] | Omit = omit,
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncResponseStreamManager[TextFormatT]: ...

    @overload
    def stream(
        self,
        *,
        input: Union[str, ResponseInputParam],
        model: ResponsesModel,
        background: Optional[bool] | Omit = omit,
        context_management: Optional[Iterable[response_create_params.ContextManagement]] | Omit = omit,
        text_format: type[TextFormatT] | Omit = omit,
        tools: Iterable[ParseableToolParam] | Omit = omit,
        conversation: Optional[response_create_params.Conversation] | Omit = omit,
        include: Optional[List[ResponseIncludable]] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        max_output_tokens: Optional[int] | Omit = omit,
        max_tool_calls: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt: Optional[ResponsePromptParam] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | Omit = omit,
        reasoning: Optional[Reasoning] | Omit = omit,
        safety_identifier: str | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream_options: Optional[response_create_params.StreamOptions] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        text: ResponseTextConfigParam | Omit = omit,
        tool_choice: response_create_params.ToolChoice | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        truncation: Optional[Literal["auto", "disabled"]] | Omit = omit,
        user: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncResponseStreamManager[TextFormatT]: ...

    def stream(
        self,
        *,
        response_id: str | Omit = omit,
        input: Union[str, ResponseInputParam] | Omit = omit,
        model: ResponsesModel | Omit = omit,
        background: Optional[bool] | Omit = omit,
        context_management: Optional[Iterable[response_create_params.ContextManagement]] | Omit = omit,
        text_format: type[TextFormatT] | Omit = omit,
        tools: Iterable[ParseableToolParam] | Omit = omit,
        conversation: Optional[response_create_params.Conversation] | Omit = omit,
        include: Optional[List[ResponseIncludable]] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        max_output_tokens: Optional[int] | Omit = omit,
        max_tool_calls: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt: Optional[ResponsePromptParam] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | Omit = omit,
        reasoning: Optional[Reasoning] | Omit = omit,
        safety_identifier: str | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream_options: Optional[response_create_params.StreamOptions] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        text: ResponseTextConfigParam | Omit = omit,
        tool_choice: response_create_params.ToolChoice | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        truncation: Optional[Literal["auto", "disabled"]] | Omit = omit,
        user: str | Omit = omit,
        starting_after: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncResponseStreamManager[TextFormatT]:
        new_response_args = {
            "input": input,
            "model": model,
            "context_management": context_management,
            "conversation": conversation,
            "include": include,
            "instructions": instructions,
            "max_output_tokens": max_output_tokens,
            "max_tool_calls": max_tool_calls,
            "metadata": metadata,
            "parallel_tool_calls": parallel_tool_calls,
            "previous_response_id": previous_response_id,
            "prompt": prompt,
            "prompt_cache_key": prompt_cache_key,
            "prompt_cache_retention": prompt_cache_retention,
            "reasoning": reasoning,
            "safety_identifier": safety_identifier,
            "service_tier": service_tier,
            "store": store,
            "stream_options": stream_options,
            "temperature": temperature,
            "text": text,
            "tool_choice": tool_choice,
            "top_logprobs": top_logprobs,
            "top_p": top_p,
            "truncation": truncation,
            "user": user,
            "background": background,
        }
        new_response_args_names = [k for k, v in new_response_args.items() if is_given(v)]

        if (is_given(response_id) or is_given(starting_after)) and len(new_response_args_names) > 0:
            raise ValueError(
                "Cannot provide both response_id/starting_after can't be provided together with "
                + ", ".join(new_response_args_names)
            )

        tools = _make_tools(tools)
        if len(new_response_args_names) > 0:
            if isinstance(input, NotGiven):
                raise ValueError("input must be provided when creating a new response")

            if not is_given(model):
                raise ValueError("model must be provided when creating a new response")

            if is_given(text_format):
                if not text:
                    text = {}

                if "format" in text:
                    raise TypeError("Cannot mix and match text.format with text_format")
                text = copy(text)
                text["format"] = _type_to_text_format_param(text_format)

            api_request = self.create(
                input=input,
                model=model,
                stream=True,
                tools=tools,
                context_management=context_management,
                conversation=conversation,
                include=include,
                instructions=instructions,
                max_output_tokens=max_output_tokens,
                max_tool_calls=max_tool_calls,
                metadata=metadata,
                parallel_tool_calls=parallel_tool_calls,
                previous_response_id=previous_response_id,
                prompt=prompt,
                prompt_cache_key=prompt_cache_key,
                prompt_cache_retention=prompt_cache_retention,
                store=store,
                stream_options=stream_options,
                temperature=temperature,
                text=text,
                tool_choice=tool_choice,
                reasoning=reasoning,
                safety_identifier=safety_identifier,
                service_tier=service_tier,
                top_logprobs=top_logprobs,
                top_p=top_p,
                truncation=truncation,
                user=user,
                background=background,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            )

            return AsyncResponseStreamManager(
                api_request,
                text_format=text_format,
                input_tools=tools,
                starting_after=None,
            )
        else:
            if isinstance(response_id, Omit):
                raise ValueError("response_id must be provided when streaming an existing response")

            api_request = self.retrieve(
                response_id,
                stream=True,
                include=include or [],
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            )
            return AsyncResponseStreamManager(
                api_request,
                text_format=text_format,
                input_tools=tools,
                starting_after=starting_after if is_given(starting_after) else None,
            )

    async def parse(
        self,
        *,
        text_format: type[TextFormatT] | Omit = omit,
        background: Optional[bool] | Omit = omit,
        context_management: Optional[Iterable[response_create_params.ContextManagement]] | Omit = omit,
        conversation: Optional[response_create_params.Conversation] | Omit = omit,
        include: Optional[List[ResponseIncludable]] | Omit = omit,
        input: Union[str, ResponseInputParam] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        max_output_tokens: Optional[int] | Omit = omit,
        max_tool_calls: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        model: ResponsesModel | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt: Optional[ResponsePromptParam] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | Omit = omit,
        reasoning: Optional[Reasoning] | Omit = omit,
        safety_identifier: str | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream: Optional[Literal[False]] | Literal[True] | Omit = omit,
        stream_options: Optional[response_create_params.StreamOptions] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        text: ResponseTextConfigParam | Omit = omit,
        tool_choice: response_create_params.ToolChoice | Omit = omit,
        tools: Iterable[ParseableToolParam] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        truncation: Optional[Literal["auto", "disabled"]] | Omit = omit,
        user: str | Omit = omit,
        verbosity: Optional[Literal["low", "medium", "high"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ParsedResponse[TextFormatT]:
        if is_given(text_format):
            if not text:
                text = {}

            if "format" in text:
                raise TypeError("Cannot mix and match text.format with text_format")
            text = copy(text)
            text["format"] = _type_to_text_format_param(text_format)

        tools = _make_tools(tools)

        def parser(raw_response: Response) -> ParsedResponse[TextFormatT]:
            return parse_response(
                input_tools=tools,
                text_format=text_format,
                response=raw_response,
            )

        return await self._post(
            "/responses",
            body=maybe_transform(
                {
                    "background": background,
                    "context_management": context_management,
                    "conversation": conversation,
                    "include": include,
                    "input": input,
                    "instructions": instructions,
                    "max_output_tokens": max_output_tokens,
                    "max_tool_calls": max_tool_calls,
                    "metadata": metadata,
                    "model": model,
                    "parallel_tool_calls": parallel_tool_calls,
                    "previous_response_id": previous_response_id,
                    "prompt": prompt,
                    "prompt_cache_key": prompt_cache_key,
                    "prompt_cache_retention": prompt_cache_retention,
                    "reasoning": reasoning,
                    "safety_identifier": safety_identifier,
                    "service_tier": service_tier,
                    "store": store,
                    "stream": stream,
                    "stream_options": stream_options,
                    "temperature": temperature,
                    "text": text,
                    "tool_choice": tool_choice,
                    "tools": tools,
                    "top_logprobs": top_logprobs,
                    "top_p": top_p,
                    "truncation": truncation,
                    "user": user,
                    "verbosity": verbosity,
                },
                response_create_params.ResponseCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                post_parser=parser,
            ),
            # we turn the `Response` instance into a `ParsedResponse`
            # in the `parser` function above
            cast_to=cast(Type[ParsedResponse[TextFormatT]], Response),
        )

    @overload
    async def retrieve(
        self,
        response_id: str,
        *,
        include: List[ResponseIncludable] | Omit = omit,
        include_obfuscation: bool | Omit = omit,
        starting_after: int | Omit = omit,
        stream: Literal[False] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Response: ...

    @overload
    async def retrieve(
        self,
        response_id: str,
        *,
        stream: Literal[True],
        include: List[ResponseIncludable] | Omit = omit,
        starting_after: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncStream[ResponseStreamEvent]: ...

    @overload
    async def retrieve(
        self,
        response_id: str,
        *,
        stream: bool,
        include: List[ResponseIncludable] | Omit = omit,
        starting_after: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Response | AsyncStream[ResponseStreamEvent]: ...

    @overload
    async def retrieve(
        self,
        response_id: str,
        *,
        stream: bool = False,
        include: List[ResponseIncludable] | Omit = omit,
        starting_after: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Response | AsyncStream[ResponseStreamEvent]:
        """
        Retrieves a model response with the given ID.

        Args:
          include: Additional fields to include in the response. See the `include` parameter for
              Response creation above for more information.

          include_obfuscation: When true, stream obfuscation will be enabled. Stream obfuscation adds random
              characters to an `obfuscation` field on streaming delta events to normalize
              payload sizes as a mitigation to certain side-channel attacks. These obfuscation
              fields are included by default, but add a small amount of overhead to the data
              stream. You can set `include_obfuscation` to false to optimize for bandwidth if
              you trust the network links between your application and the OpenAI API.

          starting_after: The sequence number of the event after which to start streaming.

          stream: If set to true, the model response data will be streamed to the client as it is
              generated using
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
              See the
              [Streaming section below](https://platform.openai.com/docs/api-reference/responses-streaming)
              for more information.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def retrieve(
        self,
        response_id: str,
        *,
        stream: Literal[True],
        include: List[ResponseIncludable] | Omit = omit,
        include_obfuscation: bool | Omit = omit,
        starting_after: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncStream[ResponseStreamEvent]:
        """
        Retrieves a model response with the given ID.

        Args:
          stream: If set to true, the model response data will be streamed to the client as it is
              generated using
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
              See the
              [Streaming section below](https://platform.openai.com/docs/api-reference/responses-streaming)
              for more information.

          include: Additional fields to include in the response. See the `include` parameter for
              Response creation above for more information.

          include_obfuscation: When true, stream obfuscation will be enabled. Stream obfuscation adds random
              characters to an `obfuscation` field on streaming delta events to normalize
              payload sizes as a mitigation to certain side-channel attacks. These obfuscation
              fields are included by default, but add a small amount of overhead to the data
              stream. You can set `include_obfuscation` to false to optimize for bandwidth if
              you trust the network links between your application and the OpenAI API.

          starting_after: The sequence number of the event after which to start streaming.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def retrieve(
        self,
        response_id: str,
        *,
        stream: bool,
        include: List[ResponseIncludable] | Omit = omit,
        include_obfuscation: bool | Omit = omit,
        starting_after: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Response | AsyncStream[ResponseStreamEvent]:
        """
        Retrieves a model response with the given ID.

        Args:
          stream: If set to true, the model response data will be streamed to the client as it is
              generated using
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
              See the
              [Streaming section below](https://platform.openai.com/docs/api-reference/responses-streaming)
              for more information.

          include: Additional fields to include in the response. See the `include` parameter for
              Response creation above for more information.

          include_obfuscation: When true, stream obfuscation will be enabled. Stream obfuscation adds random
              characters to an `obfuscation` field on streaming delta events to normalize
              payload sizes as a mitigation to certain side-channel attacks. These obfuscation
              fields are included by default, but add a small amount of overhead to the data
              stream. You can set `include_obfuscation` to false to optimize for bandwidth if
              you trust the network links between your application and the OpenAI API.

          starting_after: The sequence number of the event after which to start streaming.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    async def retrieve(
        self,
        response_id: str,
        *,
        include: List[ResponseIncludable] | Omit = omit,
        include_obfuscation: bool | Omit = omit,
        starting_after: int | Omit = omit,
        stream: Literal[False] | Literal[True] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Response | AsyncStream[ResponseStreamEvent]:
        if not response_id:
            raise ValueError(f"Expected a non-empty value for `response_id` but received {response_id!r}")
        return await self._get(
            path_template("/responses/{response_id}", response_id=response_id),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "include": include,
                        "include_obfuscation": include_obfuscation,
                        "starting_after": starting_after,
                        "stream": stream,
                    },
                    response_retrieve_params.ResponseRetrieveParams,
                ),
            ),
            cast_to=Response,
            stream=stream or False,
            stream_cls=AsyncStream[ResponseStreamEvent],
        )

    async def delete(
        self,
        response_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Deletes a model response with the given ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not response_id:
            raise ValueError(f"Expected a non-empty value for `response_id` but received {response_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            path_template("/responses/{response_id}", response_id=response_id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def cancel(
        self,
        response_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Response:
        """Cancels a model response with the given ID.

        Only responses created with the
        `background` parameter set to `true` can be cancelled.
        [Learn more](https://platform.openai.com/docs/guides/background).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not response_id:
            raise ValueError(f"Expected a non-empty value for `response_id` but received {response_id!r}")
        return await self._post(
            path_template("/responses/{response_id}/cancel", response_id=response_id),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Response,
        )

    async def compact(
        self,
        *,
        model: Union[
            Literal[
                "gpt-5.4",
                "gpt-5.4-mini",
                "gpt-5.4-nano",
                "gpt-5.4-mini-2026-03-17",
                "gpt-5.4-nano-2026-03-17",
                "gpt-5.3-chat-latest",
                "gpt-5.2",
                "gpt-5.2-2025-12-11",
                "gpt-5.2-chat-latest",
                "gpt-5.2-pro",
                "gpt-5.2-pro-2025-12-11",
                "gpt-5.1",
                "gpt-5.1-2025-11-13",
                "gpt-5.1-codex",
                "gpt-5.1-mini",
                "gpt-5.1-chat-latest",
                "gpt-5",
                "gpt-5-mini",
                "gpt-5-nano",
                "gpt-5-2025-08-07",
                "gpt-5-mini-2025-08-07",
                "gpt-5-nano-2025-08-07",
                "gpt-5-chat-latest",
                "gpt-4.1",
                "gpt-4.1-mini",
                "gpt-4.1-nano",
                "gpt-4.1-2025-04-14",
                "gpt-4.1-mini-2025-04-14",
                "gpt-4.1-nano-2025-04-14",
                "o4-mini",
                "o4-mini-2025-04-16",
                "o3",
                "o3-2025-04-16",
                "o3-mini",
                "o3-mini-2025-01-31",
                "o1",
                "o1-2024-12-17",
                "o1-preview",
                "o1-preview-2024-09-12",
                "o1-mini",
                "o1-mini-2024-09-12",
                "gpt-4o",
                "gpt-4o-2024-11-20",
                "gpt-4o-2024-08-06",
                "gpt-4o-2024-05-13",
                "gpt-4o-audio-preview",
                "gpt-4o-audio-preview-2024-10-01",
                "gpt-4o-audio-preview-2024-12-17",
                "gpt-4o-audio-preview-2025-06-03",
                "gpt-4o-mini-audio-preview",
                "gpt-4o-mini-audio-preview-2024-12-17",
                "gpt-4o-search-preview",
                "gpt-4o-mini-search-preview",
                "gpt-4o-search-preview-2025-03-11",
                "gpt-4o-mini-search-preview-2025-03-11",
                "chatgpt-4o-latest",
                "codex-mini-latest",
                "gpt-4o-mini",
                "gpt-4o-mini-2024-07-18",
                "gpt-4-turbo",
                "gpt-4-turbo-2024-04-09",
                "gpt-4-0125-preview",
                "gpt-4-turbo-preview",
                "gpt-4-1106-preview",
                "gpt-4-vision-preview",
                "gpt-4",
                "gpt-4-0314",
                "gpt-4-0613",
                "gpt-4-32k",
                "gpt-4-32k-0314",
                "gpt-4-32k-0613",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k",
                "gpt-3.5-turbo-0301",
                "gpt-3.5-turbo-0613",
                "gpt-3.5-turbo-1106",
                "gpt-3.5-turbo-0125",
                "gpt-3.5-turbo-16k-0613",
                "o1-pro",
                "o1-pro-2025-03-19",
                "o3-pro",
                "o3-pro-2025-06-10",
                "o3-deep-research",
                "o3-deep-research-2025-06-26",
                "o4-mini-deep-research",
                "o4-mini-deep-research-2025-06-26",
                "computer-use-preview",
                "computer-use-preview-2025-03-11",
                "gpt-5-codex",
                "gpt-5-pro",
                "gpt-5-pro-2025-10-06",
                "gpt-5.1-codex-max",
            ],
            str,
            None,
        ],
        input: Union[str, Iterable[ResponseInputItemParam], None] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt_cache_key: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CompactedResponse:
        """Compact a conversation.

        Returns a compacted response object.

        Learn when and how to compact long-running conversations in the
        [conversation state guide](https://platform.openai.com/docs/guides/conversation-state#managing-the-context-window).
        For ZDR-compatible compaction details, see
        [Compaction (advanced)](https://platform.openai.com/docs/guides/conversation-state#compaction-advanced).

        Args:
          model: Model ID used to generate the response, like `gpt-5` or `o3`. OpenAI offers a
              wide range of models with different capabilities, performance characteristics,
              and price points. Refer to the
              [model guide](https://platform.openai.com/docs/models) to browse and compare
              available models.

          input: Text, image, or file inputs to the model, used to generate a response

          instructions: A system (or developer) message inserted into the model's context. When used
              along with `previous_response_id`, the instructions from a previous response
              will not be carried over to the next response. This makes it simple to swap out
              system (or developer) messages in new responses.

          previous_response_id: The unique ID of the previous response to the model. Use this to create
              multi-turn conversations. Learn more about
              [conversation state](https://platform.openai.com/docs/guides/conversation-state).
              Cannot be used in conjunction with `conversation`.

          prompt_cache_key: A key to use when reading from or writing to the prompt cache.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/responses/compact",
            body=await async_maybe_transform(
                {
                    "model": model,
                    "input": input,
                    "instructions": instructions,
                    "previous_response_id": previous_response_id,
                    "prompt_cache_key": prompt_cache_key,
                },
                response_compact_params.ResponseCompactParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CompactedResponse,
        )

    def connect(
        self,
        extra_query: Query = {},
        extra_headers: Headers = {},
        websocket_connection_options: WebSocketConnectionOptions = {},
        on_reconnecting: Callable[[ReconnectingEvent], ReconnectingOverrides | None] | None = None,
        max_retries: int = 5,
        initial_delay: float = 0.5,
        max_delay: float = 8.0,
        max_queue_size: int = 1_048_576,
    ) -> AsyncResponsesConnectionManager:
        """Connect to a persistent Responses API WebSocket.

        Send `response.create` events and receive response stream events over the socket.
        """
        return AsyncResponsesConnectionManager(
            client=self._client,
            extra_query=extra_query,
            extra_headers=extra_headers,
            websocket_connection_options=websocket_connection_options,
            on_reconnecting=on_reconnecting,
            max_retries=max_retries,
            initial_delay=initial_delay,
            max_delay=max_delay,
            max_queue_size=max_queue_size,
        )


class ResponsesWithRawResponse:
    def __init__(self, responses: Responses) -> None:
        self._responses = responses

        self.create = _legacy_response.to_raw_response_wrapper(
            responses.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            responses.retrieve,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            responses.delete,
        )
        self.cancel = _legacy_response.to_raw_response_wrapper(
            responses.cancel,
        )
        self.compact = _legacy_response.to_raw_response_wrapper(
            responses.compact,
        )
        self.parse = _legacy_response.to_raw_response_wrapper(
            responses.parse,
        )

    @cached_property
    def input_items(self) -> InputItemsWithRawResponse:
        return InputItemsWithRawResponse(self._responses.input_items)

    @cached_property
    def input_tokens(self) -> InputTokensWithRawResponse:
        return InputTokensWithRawResponse(self._responses.input_tokens)


class AsyncResponsesWithRawResponse:
    def __init__(self, responses: AsyncResponses) -> None:
        self._responses = responses

        self.create = _legacy_response.async_to_raw_response_wrapper(
            responses.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            responses.retrieve,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            responses.delete,
        )
        self.cancel = _legacy_response.async_to_raw_response_wrapper(
            responses.cancel,
        )
        self.compact = _legacy_response.async_to_raw_response_wrapper(
            responses.compact,
        )
        self.parse = _legacy_response.async_to_raw_response_wrapper(
            responses.parse,
        )

    @cached_property
    def input_items(self) -> AsyncInputItemsWithRawResponse:
        return AsyncInputItemsWithRawResponse(self._responses.input_items)

    @cached_property
    def input_tokens(self) -> AsyncInputTokensWithRawResponse:
        return AsyncInputTokensWithRawResponse(self._responses.input_tokens)


class ResponsesWithStreamingResponse:
    def __init__(self, responses: Responses) -> None:
        self._responses = responses

        self.create = to_streamed_response_wrapper(
            responses.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            responses.retrieve,
        )
        self.delete = to_streamed_response_wrapper(
            responses.delete,
        )
        self.cancel = to_streamed_response_wrapper(
            responses.cancel,
        )
        self.compact = to_streamed_response_wrapper(
            responses.compact,
        )

    @cached_property
    def input_items(self) -> InputItemsWithStreamingResponse:
        return InputItemsWithStreamingResponse(self._responses.input_items)

    @cached_property
    def input_tokens(self) -> InputTokensWithStreamingResponse:
        return InputTokensWithStreamingResponse(self._responses.input_tokens)


class AsyncResponsesWithStreamingResponse:
    def __init__(self, responses: AsyncResponses) -> None:
        self._responses = responses

        self.create = async_to_streamed_response_wrapper(
            responses.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            responses.retrieve,
        )
        self.delete = async_to_streamed_response_wrapper(
            responses.delete,
        )
        self.cancel = async_to_streamed_response_wrapper(
            responses.cancel,
        )
        self.compact = async_to_streamed_response_wrapper(
            responses.compact,
        )

    @cached_property
    def input_items(self) -> AsyncInputItemsWithStreamingResponse:
        return AsyncInputItemsWithStreamingResponse(self._responses.input_items)

    @cached_property
    def input_tokens(self) -> AsyncInputTokensWithStreamingResponse:
        return AsyncInputTokensWithStreamingResponse(self._responses.input_tokens)


def _make_tools(tools: Iterable[ParseableToolParam] | Omit) -> List[ToolParam] | Omit:
    if not is_given(tools):
        return omit

    converted_tools: List[ToolParam] = []
    for tool in tools:
        if tool["type"] != "function":
            converted_tools.append(tool)
            continue

        if "function" not in tool:
            # standard Responses API case
            converted_tools.append(tool)
            continue

        function = cast(Any, tool)["function"]  # pyright: ignore[reportUnnecessaryCast]
        if not isinstance(function, PydanticFunctionTool):
            raise Exception(
                "Expected Chat Completions function tool shape to be created using `openai.pydantic_function_tool()`"
            )

        assert "parameters" in function
        new_tool = ResponsesPydanticFunctionTool(
            {
                "type": "function",
                "name": function["name"],
                "description": function.get("description"),
                "parameters": function["parameters"],
                "strict": function.get("strict") or False,
            },
            function.model,
        )

        converted_tools.append(new_tool.cast())

    return converted_tools


class AsyncResponsesConnection:
    """Represents a live WebSocket connection to the Responses API"""

    response: AsyncResponsesResponseResource

    _connection: AsyncWebSocketConnection

    def __init__(
        self,
        connection: AsyncWebSocketConnection,
        *,
        make_ws: Callable[[Query, Headers], Awaitable[AsyncWebSocketConnection]] | None = None,
        on_reconnecting: Callable[[ReconnectingEvent], ReconnectingOverrides | None] | None = None,
        max_retries: int = 5,
        initial_delay: float = 0.5,
        max_delay: float = 8.0,
        extra_query: Query = {},
        extra_headers: Headers = {},
        send_queue: SendQueue | None = None,
    ) -> None:
        self._connection = connection
        self._make_ws = make_ws
        self._on_reconnecting = on_reconnecting
        self._max_retries = max_retries
        self._initial_delay = initial_delay
        self._max_delay = max_delay
        self._extra_query = extra_query
        self._extra_headers = extra_headers
        self._intentionally_closed = False
        self._is_reconnecting = False
        self._send_queue = send_queue or SendQueue()
        self._event_handler_registry = EventHandlerRegistry(use_lock=False)

        self.response = AsyncResponsesResponseResource(self)

    async def __aiter__(self) -> AsyncIterator[ResponsesServerEvent]:
        """
        An infinite-iterator that will continue to yield events until
        the connection is closed.
        """
        from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

        while True:
            try:
                yield await self.recv()
            except ConnectionClosedOK:
                return
            except ConnectionClosedError as exc:
                if not await self._reconnect(exc):
                    unsent = self._send_queue.drain()
                    if unsent:
                        raise WebSocketConnectionClosedError(
                            "WebSocket connection closed with unsent messages",
                            unsent_messages=unsent,
                        ) from exc
                    raise

    async def recv(self) -> ResponsesServerEvent:
        """
        Receive the next message from the connection and parses it into a `ResponsesServerEvent` object.

        Canceling this method is safe. There's no risk of losing data.
        """
        return self.parse_event(await self.recv_bytes())

    async def recv_bytes(self) -> bytes:
        """Receive the next message from the connection as raw bytes.

        Canceling this method is safe. There's no risk of losing data.

        If you want to parse the message into a `ResponsesServerEvent` object like `.recv()` does,
        then you can call `.parse_event(data)`.
        """
        message = await self._connection.recv(decode=False)
        log.debug(f"Received WebSocket message: %s", message)
        return message

    async def send(self, event: ResponsesClientEvent | ResponsesClientEventParam) -> None:
        data = (
            event.to_json(use_api_names=True, exclude_defaults=True, exclude_unset=True)
            if isinstance(event, BaseModel)
            else json.dumps(await async_maybe_transform(event, ResponsesClientEventParam))
        )
        if self._is_reconnecting:
            self._send_queue.enqueue(data)
            return
        try:
            await self._connection.send(data)
        except Exception:
            self._send_queue.enqueue(data)
            raise

    async def send_raw(self, data: bytes | str) -> None:
        if self._is_reconnecting:
            raw = data if isinstance(data, str) else data.decode("utf-8")
            self._send_queue.enqueue(raw)
            return
        await self._connection.send(data)

    async def close(self, *, code: int = 1000, reason: str = "") -> None:
        self._intentionally_closed = True
        await self._connection.close(code=code, reason=reason)

    def parse_event(self, data: str | bytes) -> ResponsesServerEvent:
        """
        Converts a raw `str` or `bytes` message into a `ResponsesServerEvent` object.

        This is helpful if you're using `.recv_bytes()`.
        """
        return cast(
            ResponsesServerEvent,
            construct_type_unchecked(value=json.loads(data), type_=cast(Any, ResponsesServerEvent)),
        )

    async def _reconnect(self, exc: Exception) -> bool:
        """Attempt to reconnect after a connection failure.

        Returns ``True`` if a new connection was established, ``False`` if the
        caller should re-raise the original exception.
        """
        import asyncio

        if self._on_reconnecting is None or self._make_ws is None:
            return False

        from websockets.exceptions import ConnectionClosedError

        close_code = 1006
        if isinstance(exc, ConnectionClosedError) and exc.rcvd is not None:
            close_code = exc.rcvd.code

        if not is_recoverable_close(close_code):
            return False

        self._is_reconnecting = True

        for attempt in range(1, self._max_retries + 1):
            base_delay = min(self._initial_delay * (2 ** (attempt - 1)), self._max_delay)
            jitter = 0.75 + random.random() * 0.25
            delay = base_delay * jitter

            event = ReconnectingEvent(
                attempt=attempt,
                max_attempts=self._max_retries,
                delay=delay,
                close_code=close_code,
                extra_query=self._extra_query,
                extra_headers=self._extra_headers,
            )

            try:
                result = self._on_reconnecting(event)
            except Exception:
                self._is_reconnecting = False
                return False

            if result is not None and result.get("abort"):
                self._is_reconnecting = False
                return False

            if result is not None:
                if "extra_query" in result:
                    self._extra_query = result["extra_query"]
                if "extra_headers" in result:
                    self._extra_headers = result["extra_headers"]

            log.info(
                "Reconnecting to WebSocket API (attempt %d/%d) after %.1fs delay",
                attempt,
                self._max_retries,
                delay,
            )
            await asyncio.sleep(delay)

            if self._intentionally_closed:
                self._is_reconnecting = False
                return False

            try:
                self._connection = await self._make_ws(self._extra_query, self._extra_headers)
                log.info("Reconnected to WebSocket API")
                self._is_reconnecting = False
                await self._flush_send_queue()
                return True
            except Exception:
                pass

        self._is_reconnecting = False
        return False

    async def _flush_send_queue(self) -> None:
        """Send all queued messages over the current connection."""

        async def _send(data: str) -> None:
            await self._connection.send(data)

        try:
            await self._send_queue.flush_async(_send)
        except Exception:
            log.warning("Failed to flush send queue after reconnect", exc_info=True)

    def on(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[AsyncResponsesConnection, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Adds the handler to the end of the handlers list for the given event type.

        No checks are made to see if the handler has already been added. Multiple calls
        passing the same combination of event type and handler will result in the handler
        being added, and called, multiple times.

        Can be used as a method (returns ``self`` for chaining)::

            connection.on("response.audio.delta", my_handler)

        Or as a decorator::

            @connection.on("response.audio.delta")
            async def my_handler(event): ...
        """
        if handler is not None:
            self._event_handler_registry.add(event_type, handler)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self._event_handler_registry.add(event_type, fn)
            return fn

        return decorator

    def off(self, event_type: str, handler: Callable[..., Any]) -> AsyncResponsesConnection:
        """Remove a previously registered event handler."""
        self._event_handler_registry.remove(event_type, handler)
        return self

    def once(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[AsyncResponsesConnection, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Register a one-time event handler.

        Automatically removed after first invocation.
        """
        if handler is not None:
            self._event_handler_registry.add(event_type, handler, once=True)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self._event_handler_registry.add(event_type, fn, once=True)
            return fn

        return decorator

    async def dispatch_events(self) -> None:
        """Run the event loop, dispatching received events to registered handlers.

        Blocks until the connection is closed. This is the push-based
        alternative to iterating with ``async for event in connection``.

        If an ``"error"`` event arrives and no handler is registered for
        ``"error"`` or ``"event"``, an ``OpenAIError`` is raised.
        """
        import asyncio

        async for event in self:
            event_type = event.type
            specific = self._event_handler_registry.get_handlers(event_type)
            generic = self._event_handler_registry.get_handlers("event")

            if event_type == "error" and not specific and not generic:
                if isinstance(event, ResponseErrorEvent):
                    raise OpenAIError(f"WebSocket error: {event}")

            for handler in specific:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    await result

            for handler in generic:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    await result


class AsyncResponsesConnectionManager:
    """
    Context manager over a `AsyncResponsesConnection` that is returned by `responses.connect()`

    This context manager ensures that the connection will be closed when it exits.

    ---

    Note that if your application doesn't work well with the context manager approach then you
    can call the `.enter()` method directly to initiate a connection.

    **Warning**: You must remember to close the connection with `.close()`.

    ```py
    connection = await client.responses.connect(...).enter()
    # ...
    await connection.close()
    ```
    """

    def __init__(
        self,
        *,
        client: AsyncOpenAI,
        extra_query: Query,
        extra_headers: Headers,
        websocket_connection_options: WebSocketConnectionOptions,
        on_reconnecting: Callable[[ReconnectingEvent], ReconnectingOverrides | None] | None = None,
        max_retries: int = 5,
        initial_delay: float = 0.5,
        max_delay: float = 8.0,
        max_queue_size: int = 1_048_576,
    ) -> None:
        self.__client = client
        self.__connection: AsyncResponsesConnection | None = None
        self.__extra_query = extra_query
        self.__extra_headers = extra_headers
        self.__websocket_connection_options = websocket_connection_options
        self.__on_reconnecting = on_reconnecting
        self.__max_retries = max_retries
        self.__initial_delay = initial_delay
        self.__max_delay = max_delay
        self.__send_queue = SendQueue(max_bytes=max_queue_size)
        self.__event_handler_registry = EventHandlerRegistry(use_lock=False)

    def send(self, event: ResponsesClientEvent | ResponsesClientEventParam) -> None:
        """Queue a message to be sent when the connection is established.

        This can be called before entering the context manager. Queued messages
        are automatically sent once the WebSocket connection opens.
        """
        data = (
            event.to_json(use_api_names=True, exclude_defaults=True, exclude_unset=True)
            if isinstance(event, BaseModel)
            else json.dumps(event)
        )
        self.__send_queue.enqueue(data)

    def on(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[AsyncResponsesConnectionManager, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Register an event handler before the connection is established.

        Handlers are transferred to the connection on enter. Supports the
        same method and decorator forms as ``AsyncResponsesConnection.on``.
        """
        if handler is not None:
            self.__event_handler_registry.add(event_type, handler)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.__event_handler_registry.add(event_type, fn)
            return fn

        return decorator

    def off(self, event_type: str, handler: Callable[..., Any]) -> AsyncResponsesConnectionManager:
        """Remove a previously registered event handler."""
        self.__event_handler_registry.remove(event_type, handler)
        return self

    def once(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[AsyncResponsesConnectionManager, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Register a one-time event handler before the connection is established."""
        if handler is not None:
            self.__event_handler_registry.add(event_type, handler, once=True)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.__event_handler_registry.add(event_type, fn, once=True)
            return fn

        return decorator

    async def __aenter__(self) -> AsyncResponsesConnection:
        """
        If your application doesn't work well with the context manager approach then you
        can call this method directly to initiate a connection.

        **Warning**: You must remember to close the connection with `.close()`.

        ```py
        connection = await client.responses.connect(...).enter()
        # ...
        await connection.close()
        ```
        """
        ws = await self._connect_ws(self.__extra_query, self.__extra_headers)

        self.__connection = AsyncResponsesConnection(
            ws,
            make_ws=self._connect_ws if self.__on_reconnecting is not None else None,
            on_reconnecting=self.__on_reconnecting,
            max_retries=self.__max_retries,
            initial_delay=self.__initial_delay,
            max_delay=self.__max_delay,
            extra_query=self.__extra_query,
            extra_headers=self.__extra_headers,
            send_queue=self.__send_queue,
        )

        self.__event_handler_registry.merge_into(self.__connection._event_handler_registry)
        await self.__connection._flush_send_queue()

        return self.__connection

    enter = __aenter__

    async def _connect_ws(self, extra_query: Query, extra_headers: Headers) -> AsyncWebSocketConnection:
        try:
            from websockets.asyncio.client import connect
        except ImportError as exc:
            raise OpenAIError("You need to install `openai[realtime]` to use this method") from exc

        url = self._prepare_url().copy_with(
            params={
                **self.__client.base_url.params,
                **extra_query,
            },
        )
        log.debug("Connecting to %s", url)
        if self.__websocket_connection_options:
            log.debug("Connection options: %s", self.__websocket_connection_options)

        return await connect(
            str(url),
            user_agent_header=self.__client.user_agent,
            additional_headers=_merge_mappings(
                {
                    **self.__client.auth_headers,
                },
                extra_headers,
            ),
            **self.__websocket_connection_options,
        )

    def _prepare_url(self) -> httpx.URL:
        if self.__client.websocket_base_url is not None:
            base_url = httpx.URL(self.__client.websocket_base_url)
        else:
            scheme = self.__client._base_url.scheme
            ws_scheme = "ws" if scheme == "http" else "wss"
            base_url = self.__client._base_url.copy_with(scheme=ws_scheme)

        merge_raw_path = base_url.raw_path.rstrip(b"/") + b"/responses"
        return base_url.copy_with(raw_path=merge_raw_path)

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        if self.__connection is not None:
            await self.__connection.close()


class ResponsesConnection:
    """Represents a live WebSocket connection to the Responses API"""

    response: ResponsesResponseResource

    _connection: WebSocketConnection

    def __init__(
        self,
        connection: WebSocketConnection,
        *,
        make_ws: Callable[[Query, Headers], WebSocketConnection] | None = None,
        on_reconnecting: Callable[[ReconnectingEvent], ReconnectingOverrides | None] | None = None,
        max_retries: int = 5,
        initial_delay: float = 0.5,
        max_delay: float = 8.0,
        extra_query: Query = {},
        extra_headers: Headers = {},
        send_queue: SendQueue | None = None,
    ) -> None:
        self._connection = connection
        self._make_ws = make_ws
        self._on_reconnecting = on_reconnecting
        self._max_retries = max_retries
        self._initial_delay = initial_delay
        self._max_delay = max_delay
        self._extra_query = extra_query
        self._extra_headers = extra_headers
        self._intentionally_closed = False
        self._is_reconnecting = False
        self._send_queue = send_queue or SendQueue()
        self._event_handler_registry = EventHandlerRegistry(use_lock=True)

        self.response = ResponsesResponseResource(self)

    def __iter__(self) -> Iterator[ResponsesServerEvent]:
        """
        An infinite-iterator that will continue to yield events until
        the connection is closed.
        """
        from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

        while True:
            try:
                yield self.recv()
            except ConnectionClosedOK:
                return
            except ConnectionClosedError as exc:
                if not self._reconnect(exc):
                    unsent = self._send_queue.drain()
                    if unsent:
                        raise WebSocketConnectionClosedError(
                            "WebSocket connection closed with unsent messages",
                            unsent_messages=unsent,
                        ) from exc
                    raise

    def recv(self) -> ResponsesServerEvent:
        """
        Receive the next message from the connection and parses it into a `ResponsesServerEvent` object.

        Canceling this method is safe. There's no risk of losing data.
        """
        return self.parse_event(self.recv_bytes())

    def recv_bytes(self) -> bytes:
        """Receive the next message from the connection as raw bytes.

        Canceling this method is safe. There's no risk of losing data.

        If you want to parse the message into a `ResponsesServerEvent` object like `.recv()` does,
        then you can call `.parse_event(data)`.
        """
        message = self._connection.recv(decode=False)
        log.debug(f"Received WebSocket message: %s", message)
        return message

    def send(self, event: ResponsesClientEvent | ResponsesClientEventParam) -> None:
        data = (
            event.to_json(use_api_names=True, exclude_defaults=True, exclude_unset=True)
            if isinstance(event, BaseModel)
            else json.dumps(maybe_transform(event, ResponsesClientEventParam))
        )
        if self._is_reconnecting:
            self._send_queue.enqueue(data)
            return
        try:
            self._connection.send(data)
        except Exception:
            self._send_queue.enqueue(data)
            raise

    def send_raw(self, data: bytes | str) -> None:
        if self._is_reconnecting:
            raw = data if isinstance(data, str) else data.decode("utf-8")
            self._send_queue.enqueue(raw)
            return
        self._connection.send(data)

    def close(self, *, code: int = 1000, reason: str = "") -> None:
        self._intentionally_closed = True
        self._connection.close(code=code, reason=reason)

    def parse_event(self, data: str | bytes) -> ResponsesServerEvent:
        """
        Converts a raw `str` or `bytes` message into a `ResponsesServerEvent` object.

        This is helpful if you're using `.recv_bytes()`.
        """
        return cast(
            ResponsesServerEvent,
            construct_type_unchecked(value=json.loads(data), type_=cast(Any, ResponsesServerEvent)),
        )

    def _reconnect(self, exc: Exception) -> bool:
        """Attempt to reconnect after a connection failure.

        Returns ``True`` if a new connection was established, ``False`` if the
        caller should re-raise the original exception.
        """
        if self._on_reconnecting is None or self._make_ws is None:
            return False

        from websockets.exceptions import ConnectionClosedError

        close_code = 1006
        if isinstance(exc, ConnectionClosedError) and exc.rcvd is not None:
            close_code = exc.rcvd.code

        if not is_recoverable_close(close_code):
            return False

        self._is_reconnecting = True

        for attempt in range(1, self._max_retries + 1):
            base_delay = min(self._initial_delay * (2 ** (attempt - 1)), self._max_delay)
            jitter = 0.75 + random.random() * 0.25
            delay = base_delay * jitter

            event = ReconnectingEvent(
                attempt=attempt,
                max_attempts=self._max_retries,
                delay=delay,
                close_code=close_code,
                extra_query=self._extra_query,
                extra_headers=self._extra_headers,
            )

            try:
                result = self._on_reconnecting(event)
            except Exception:
                self._is_reconnecting = False
                return False

            if result is not None and result.get("abort"):
                self._is_reconnecting = False
                return False

            if result is not None:
                if "extra_query" in result:
                    self._extra_query = result["extra_query"]
                if "extra_headers" in result:
                    self._extra_headers = result["extra_headers"]

            log.info(
                "Reconnecting to WebSocket API (attempt %d/%d) after %.1fs delay",
                attempt,
                self._max_retries,
                delay,
            )
            time.sleep(delay)

            if self._intentionally_closed:
                self._is_reconnecting = False
                return False

            try:
                self._connection = self._make_ws(self._extra_query, self._extra_headers)
                log.info("Reconnected to WebSocket API")
                self._is_reconnecting = False
                self._flush_send_queue()
                return True
            except Exception:
                pass

        self._is_reconnecting = False
        return False

    def _flush_send_queue(self) -> None:
        """Send all queued messages over the current connection."""
        try:
            self._send_queue.flush_sync(lambda data: self._connection.send(data))
        except Exception:
            log.warning("Failed to flush send queue after reconnect", exc_info=True)

    def on(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[ResponsesConnection, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Adds the handler to the end of the handlers list for the given event type.

        No checks are made to see if the handler has already been added. Multiple calls
        passing the same combination of event type and handler will result in the handler
        being added, and called, multiple times.

        Can be used as a method (returns ``self`` for chaining)::

            connection.on("response.audio.delta", my_handler)

        Or as a decorator::

            @connection.on("response.audio.delta")
            def my_handler(event): ...
        """
        if handler is not None:
            self._event_handler_registry.add(event_type, handler)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self._event_handler_registry.add(event_type, fn)
            return fn

        return decorator

    def off(self, event_type: str, handler: Callable[..., Any]) -> ResponsesConnection:
        """Remove a previously registered event handler."""
        self._event_handler_registry.remove(event_type, handler)
        return self

    def once(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[ResponsesConnection, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Register a one-time event handler.

        Automatically removed after first invocation.
        """
        if handler is not None:
            self._event_handler_registry.add(event_type, handler, once=True)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self._event_handler_registry.add(event_type, fn, once=True)
            return fn

        return decorator

    def dispatch_events(self) -> None:
        """Run the event loop, dispatching received events to registered handlers.

        Blocks the current thread until the connection is closed. This is the push-based
        alternative to iterating with ``for event in connection``.

        If an ``"error"`` event arrives and no handler is registered for
        ``"error"`` or ``"event"``, an ``OpenAIError`` is raised.
        """
        for event in self:
            event_type = event.type
            specific = self._event_handler_registry.get_handlers(event_type)
            generic = self._event_handler_registry.get_handlers("event")

            if event_type == "error" and not specific and not generic:
                if isinstance(event, ResponseErrorEvent):
                    raise OpenAIError(f"WebSocket error: {event}")

            for handler in specific:
                handler(event)

            for handler in generic:
                handler(event)


class ResponsesConnectionManager:
    """
    Context manager over a `ResponsesConnection` that is returned by `responses.connect()`

    This context manager ensures that the connection will be closed when it exits.

    ---

    Note that if your application doesn't work well with the context manager approach then you
    can call the `.enter()` method directly to initiate a connection.

    **Warning**: You must remember to close the connection with `.close()`.

    ```py
    connection = client.responses.connect(...).enter()
    # ...
    connection.close()
    ```
    """

    def __init__(
        self,
        *,
        client: OpenAI,
        extra_query: Query,
        extra_headers: Headers,
        websocket_connection_options: WebSocketConnectionOptions,
        on_reconnecting: Callable[[ReconnectingEvent], ReconnectingOverrides | None] | None = None,
        max_retries: int = 5,
        initial_delay: float = 0.5,
        max_delay: float = 8.0,
        max_queue_size: int = 1_048_576,
    ) -> None:
        self.__client = client
        self.__connection: ResponsesConnection | None = None
        self.__extra_query = extra_query
        self.__extra_headers = extra_headers
        self.__websocket_connection_options = websocket_connection_options
        self.__on_reconnecting = on_reconnecting
        self.__max_retries = max_retries
        self.__initial_delay = initial_delay
        self.__max_delay = max_delay
        self.__send_queue = SendQueue(max_bytes=max_queue_size)
        self.__event_handler_registry = EventHandlerRegistry(use_lock=True)

    def send(self, event: ResponsesClientEvent | ResponsesClientEventParam) -> None:
        """Queue a message to be sent when the connection is established.

        This can be called before entering the context manager. Queued messages
        are automatically sent once the WebSocket connection opens.
        """
        data = (
            event.to_json(use_api_names=True, exclude_defaults=True, exclude_unset=True)
            if isinstance(event, BaseModel)
            else json.dumps(event)
        )
        self.__send_queue.enqueue(data)

    def on(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[ResponsesConnectionManager, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Register an event handler before the connection is established.

        Handlers are transferred to the connection on enter. Supports the
        same method and decorator forms as ``ResponsesConnection.on``.
        """
        if handler is not None:
            self.__event_handler_registry.add(event_type, handler)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.__event_handler_registry.add(event_type, fn)
            return fn

        return decorator

    def off(self, event_type: str, handler: Callable[..., Any]) -> ResponsesConnectionManager:
        """Remove a previously registered event handler."""
        self.__event_handler_registry.remove(event_type, handler)
        return self

    def once(
        self, event_type: str, handler: Callable[..., Any] | None = None
    ) -> Union[ResponsesConnectionManager, Callable[[Callable[..., Any]], Callable[..., Any]]]:
        """Register a one-time event handler before the connection is established."""
        if handler is not None:
            self.__event_handler_registry.add(event_type, handler, once=True)
            return self

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.__event_handler_registry.add(event_type, fn, once=True)
            return fn

        return decorator

    def __enter__(self) -> ResponsesConnection:
        """
        If your application doesn't work well with the context manager approach then you
        can call this method directly to initiate a connection.

        **Warning**: You must remember to close the connection with `.close()`.

        ```py
        connection = client.responses.connect(...).enter()
        # ...
        connection.close()
        ```
        """
        ws = self._connect_ws(self.__extra_query, self.__extra_headers)

        self.__connection = ResponsesConnection(
            ws,
            make_ws=self._connect_ws if self.__on_reconnecting is not None else None,
            on_reconnecting=self.__on_reconnecting,
            max_retries=self.__max_retries,
            initial_delay=self.__initial_delay,
            max_delay=self.__max_delay,
            extra_query=self.__extra_query,
            extra_headers=self.__extra_headers,
            send_queue=self.__send_queue,
        )

        self.__event_handler_registry.merge_into(self.__connection._event_handler_registry)
        self.__connection._flush_send_queue()

        return self.__connection

    enter = __enter__

    def _connect_ws(self, extra_query: Query, extra_headers: Headers) -> WebSocketConnection:
        try:
            from websockets.sync.client import connect
        except ImportError as exc:
            raise OpenAIError("You need to install `openai[realtime]` to use this method") from exc

        url = self._prepare_url().copy_with(
            params={
                **self.__client.base_url.params,
                **extra_query,
            },
        )
        log.debug("Connecting to %s", url)
        if self.__websocket_connection_options:
            log.debug("Connection options: %s", self.__websocket_connection_options)

        return connect(
            str(url),
            user_agent_header=self.__client.user_agent,
            additional_headers=_merge_mappings(
                {
                    **self.__client.auth_headers,
                },
                extra_headers,
            ),
            **self.__websocket_connection_options,
        )

    def _prepare_url(self) -> httpx.URL:
        if self.__client.websocket_base_url is not None:
            base_url = httpx.URL(self.__client.websocket_base_url)
        else:
            scheme = self.__client._base_url.scheme
            ws_scheme = "ws" if scheme == "http" else "wss"
            base_url = self.__client._base_url.copy_with(scheme=ws_scheme)

        merge_raw_path = base_url.raw_path.rstrip(b"/") + b"/responses"
        return base_url.copy_with(raw_path=merge_raw_path)

    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        if self.__connection is not None:
            self.__connection.close()


class BaseResponsesConnectionResource:
    def __init__(self, connection: ResponsesConnection) -> None:
        self._connection = connection


class ResponsesResponseResource(BaseResponsesConnectionResource):
    def create(
        self,
        *,
        background: Optional[bool] | Omit = omit,
        context_management: Optional[Iterable[responses_client_event_param.ContextManagement]] | Omit = omit,
        conversation: Optional[responses_client_event_param.Conversation] | Omit = omit,
        include: Optional[List[ResponseIncludable]] | Omit = omit,
        input: Union[str, ResponseInputParam] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        max_output_tokens: Optional[int] | Omit = omit,
        max_tool_calls: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        model: ResponsesModel | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt: Optional[ResponsePromptParam] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | Omit = omit,
        reasoning: Optional[Reasoning] | Omit = omit,
        safety_identifier: str | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream: Optional[bool] | Omit = omit,
        stream_options: Optional[responses_client_event_param.StreamOptions] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        text: ResponseTextConfigParam | Omit = omit,
        tool_choice: responses_client_event_param.ToolChoice | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        truncation: Optional[Literal["auto", "disabled"]] | Omit = omit,
        user: str | Omit = omit,
    ) -> None:
        self._connection.send(
            cast(
                ResponsesClientEventParam,
                strip_not_given(
                    {
                        "type": "response.create",
                        "background": background,
                        "context_management": context_management,
                        "conversation": conversation,
                        "include": include,
                        "input": input,
                        "instructions": instructions,
                        "max_output_tokens": max_output_tokens,
                        "max_tool_calls": max_tool_calls,
                        "metadata": metadata,
                        "model": model,
                        "parallel_tool_calls": parallel_tool_calls,
                        "previous_response_id": previous_response_id,
                        "prompt": prompt,
                        "prompt_cache_key": prompt_cache_key,
                        "prompt_cache_retention": prompt_cache_retention,
                        "reasoning": reasoning,
                        "safety_identifier": safety_identifier,
                        "service_tier": service_tier,
                        "store": store,
                        "stream": stream,
                        "stream_options": stream_options,
                        "temperature": temperature,
                        "text": text,
                        "tool_choice": tool_choice,
                        "tools": tools,
                        "top_logprobs": top_logprobs,
                        "top_p": top_p,
                        "truncation": truncation,
                        "user": user,
                    }
                ),
            )
        )


class BaseAsyncResponsesConnectionResource:
    def __init__(self, connection: AsyncResponsesConnection) -> None:
        self._connection = connection


class AsyncResponsesResponseResource(BaseAsyncResponsesConnectionResource):
    async def create(
        self,
        *,
        background: Optional[bool] | Omit = omit,
        context_management: Optional[Iterable[responses_client_event_param.ContextManagement]] | Omit = omit,
        conversation: Optional[responses_client_event_param.Conversation] | Omit = omit,
        include: Optional[List[ResponseIncludable]] | Omit = omit,
        input: Union[str, ResponseInputParam] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        max_output_tokens: Optional[int] | Omit = omit,
        max_tool_calls: Optional[int] | Omit = omit,
        metadata: Optional[Metadata] | Omit = omit,
        model: ResponsesModel | Omit = omit,
        parallel_tool_calls: Optional[bool] | Omit = omit,
        previous_response_id: Optional[str] | Omit = omit,
        prompt: Optional[ResponsePromptParam] | Omit = omit,
        prompt_cache_key: str | Omit = omit,
        prompt_cache_retention: Optional[Literal["in-memory", "24h"]] | Omit = omit,
        reasoning: Optional[Reasoning] | Omit = omit,
        safety_identifier: str | Omit = omit,
        service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | Omit = omit,
        store: Optional[bool] | Omit = omit,
        stream: Optional[bool] | Omit = omit,
        stream_options: Optional[responses_client_event_param.StreamOptions] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        text: ResponseTextConfigParam | Omit = omit,
        tool_choice: responses_client_event_param.ToolChoice | Omit = omit,
        tools: Iterable[ToolParam] | Omit = omit,
        top_logprobs: Optional[int] | Omit = omit,
        top_p: Optional[float] | Omit = omit,
        truncation: Optional[Literal["auto", "disabled"]] | Omit = omit,
        user: str | Omit = omit,
    ) -> None:
        await self._connection.send(
            cast(
                ResponsesClientEventParam,
                strip_not_given(
                    {
                        "type": "response.create",
                        "background": background,
                        "context_management": context_management,
                        "conversation": conversation,
                        "include": include,
                        "input": input,
                        "instructions": instructions,
                        "max_output_tokens": max_output_tokens,
                        "max_tool_calls": max_tool_calls,
                        "metadata": metadata,
                        "model": model,
                        "parallel_tool_calls": parallel_tool_calls,
                        "previous_response_id": previous_response_id,
                        "prompt": prompt,
                        "prompt_cache_key": prompt_cache_key,
                        "prompt_cache_retention": prompt_cache_retention,
                        "reasoning": reasoning,
                        "safety_identifier": safety_identifier,
                        "service_tier": service_tier,
                        "store": store,
                        "stream": stream,
                        "stream_options": stream_options,
                        "temperature": temperature,
                        "text": text,
                        "tool_choice": tool_choice,
                        "tools": tools,
                        "top_logprobs": top_logprobs,
                        "top_p": top_p,
                        "truncation": truncation,
                        "user": user,
                    }
                ),
            )
        )
