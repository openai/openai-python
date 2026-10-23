from __future__ import annotations

from copy import copy
from typing import TYPE_CHECKING, Any, List, Type, Union, Iterable, Optional, cast
from functools import partial
from typing_extensions import Literal

import httpx2

from openai._types import NOT_GIVEN, Body, Omit, Query, Headers, NotGiven, omit
from openai._utils import is_given, maybe_transform
from openai._streaming import Stream
from openai.lib._tools import PydanticFunctionTool, ResponsesPydanticFunctionTool
from openai._base_client import make_request_options
from openai.types.responses import response_create_params
from openai.lib._parsing._responses import (
    TextFormatT,
    parse_response,
    type_to_text_format_param as _type_to_text_format_param,
)
from openai.types.responses.response import Response
from openai.types.responses.tool_param import ToolParam, ParseableToolParam
from openai.types.responses.service_tier import ServiceTier
from openai.types.shared_params.metadata import Metadata
from openai.types.shared_params.reasoning import Reasoning
from openai.types.responses.parsed_response import ParsedResponse
from openai.lib.streaming.responses._responses import ResponseStreamManager, AsyncResponseStreamManager
from openai.types.responses.response_includable import ResponseIncludable
from openai.types.shared_params.responses_model import ResponsesModel
from openai.types.responses.response_input_param import ResponseInputParam
from openai.types.responses.response_prompt_param import ResponsePromptParam
from openai.types.responses.response_stream_event import ResponseStreamEvent
from openai.types.responses.response_text_config_param import ResponseTextConfigParam

if TYPE_CHECKING:
    from openai.resources.responses.responses import Responses, AsyncResponses


def parse(
    resource: Responses,
    *,
    text_format: type[TextFormatT] | Omit = omit,
    access_programs: response_create_params.AccessPrograms | Omit = omit,
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
    moderation: Optional[response_create_params.Moderation] | Omit = omit,
    parallel_tool_calls: Optional[bool] | Omit = omit,
    previous_response_id: Optional[str] | Omit = omit,
    prompt: Optional[ResponsePromptParam] | Omit = omit,
    prompt_cache_key: Optional[str] | Omit = omit,
    prompt_cache_options: response_create_params.PromptCacheOptions | Omit = omit,
    prompt_cache_retention: Optional[Literal["in_memory", "24h"]] | Omit = omit,
    reasoning: Optional[Reasoning] | Omit = omit,
    safety_identifier: Optional[str] | Omit = omit,
    service_tier: Optional[ServiceTier] | Omit = omit,
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
    timeout: float | httpx2.Timeout | None | NotGiven = NOT_GIVEN,
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

    return resource._post(
        "/responses",
        body=maybe_transform(
            {
                "model": model,
                "stream": stream,
                "service_tier": service_tier,
                "access_programs": access_programs,
                "background": background,
                "context_management": context_management,
                "conversation": conversation,
                "include": include,
                "input": input,
                "instructions": instructions,
                "max_output_tokens": max_output_tokens,
                "max_tool_calls": max_tool_calls,
                "metadata": metadata,
                "moderation": moderation,
                "parallel_tool_calls": parallel_tool_calls,
                "previous_response_id": previous_response_id,
                "prompt": prompt,
                "prompt_cache_key": prompt_cache_key,
                "prompt_cache_options": prompt_cache_options,
                "prompt_cache_retention": prompt_cache_retention,
                "reasoning": reasoning,
                "safety_identifier": safety_identifier,
                "store": store,
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
            security={"bearer_auth": True},
        ),
        # we turn the `Response` instance into a `ParsedResponse`
        # in the `parser` function above
        cast_to=cast("Type[ParsedResponse[TextFormatT]]", Response),
    )


async def async_parse(
    resource: AsyncResponses,
    *,
    text_format: type[TextFormatT] | Omit = omit,
    access_programs: response_create_params.AccessPrograms | Omit = omit,
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
    moderation: Optional[response_create_params.Moderation] | Omit = omit,
    parallel_tool_calls: Optional[bool] | Omit = omit,
    previous_response_id: Optional[str] | Omit = omit,
    prompt: Optional[ResponsePromptParam] | Omit = omit,
    prompt_cache_key: Optional[str] | Omit = omit,
    prompt_cache_options: response_create_params.PromptCacheOptions | Omit = omit,
    prompt_cache_retention: Optional[Literal["in_memory", "24h"]] | Omit = omit,
    reasoning: Optional[Reasoning] | Omit = omit,
    safety_identifier: Optional[str] | Omit = omit,
    service_tier: Optional[ServiceTier] | Omit = omit,
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
    timeout: float | httpx2.Timeout | None | NotGiven = NOT_GIVEN,
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

    return await resource._post(
        "/responses",
        body=maybe_transform(
            {
                "model": model,
                "stream": stream,
                "service_tier": service_tier,
                "access_programs": access_programs,
                "background": background,
                "context_management": context_management,
                "conversation": conversation,
                "include": include,
                "input": input,
                "instructions": instructions,
                "max_output_tokens": max_output_tokens,
                "max_tool_calls": max_tool_calls,
                "metadata": metadata,
                "moderation": moderation,
                "parallel_tool_calls": parallel_tool_calls,
                "previous_response_id": previous_response_id,
                "prompt": prompt,
                "prompt_cache_key": prompt_cache_key,
                "prompt_cache_options": prompt_cache_options,
                "prompt_cache_retention": prompt_cache_retention,
                "reasoning": reasoning,
                "safety_identifier": safety_identifier,
                "store": store,
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
            security={"bearer_auth": True},
        ),
        # we turn the `Response` instance into a `ParsedResponse`
        # in the `parser` function above
        cast_to=cast("Type[ParsedResponse[TextFormatT]]", Response),
    )


def stream(
    resource: Responses,
    *,
    response_id: str | Omit = omit,
    input: Union[str, ResponseInputParam] | Omit = omit,
    model: ResponsesModel | Omit = omit,
    access_programs: response_create_params.AccessPrograms | Omit = omit,
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
    moderation: Optional[response_create_params.Moderation] | Omit = omit,
    previous_response_id: Optional[str] | Omit = omit,
    prompt: Optional[ResponsePromptParam] | Omit = omit,
    prompt_cache_key: Optional[str] | Omit = omit,
    prompt_cache_options: response_create_params.PromptCacheOptions | Omit = omit,
    prompt_cache_retention: Optional[Literal["in_memory", "24h"]] | Omit = omit,
    reasoning: Optional[Reasoning] | Omit = omit,
    safety_identifier: Optional[str] | Omit = omit,
    service_tier: Optional[ServiceTier] | Omit = omit,
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
    timeout: float | httpx2.Timeout | None | NotGiven = NOT_GIVEN,
) -> ResponseStreamManager[TextFormatT]:
    new_response_args = {
        "access_programs": access_programs,
        "input": input,
        "model": model,
        "context_management": context_management,
        "conversation": conversation,
        "include": include,
        "instructions": instructions,
        "max_output_tokens": max_output_tokens,
        "max_tool_calls": max_tool_calls,
        "metadata": metadata,
        "moderation": moderation,
        "parallel_tool_calls": parallel_tool_calls,
        "previous_response_id": previous_response_id,
        "prompt": prompt,
        "prompt_cache_key": prompt_cache_key,
        "prompt_cache_options": prompt_cache_options,
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
            resource.create,
            access_programs=access_programs,
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
            moderation=moderation,
            parallel_tool_calls=parallel_tool_calls,
            previous_response_id=previous_response_id,
            prompt=prompt,
            prompt_cache_key=prompt_cache_key,
            prompt_cache_options=prompt_cache_options,
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

        return ResponseStreamManager(
            api_request,
            text_format=text_format,
            input_tools=tools,
            starting_after=None,
        )
    else:
        if not is_given(response_id):
            raise ValueError("id must be provided when streaming an existing response")

        return ResponseStreamManager(
            lambda: resource.retrieve(
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


def async_stream(
    resource: AsyncResponses,
    *,
    response_id: str | Omit = omit,
    input: Union[str, ResponseInputParam] | Omit = omit,
    model: ResponsesModel | Omit = omit,
    access_programs: response_create_params.AccessPrograms | Omit = omit,
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
    moderation: Optional[response_create_params.Moderation] | Omit = omit,
    previous_response_id: Optional[str] | Omit = omit,
    prompt: Optional[ResponsePromptParam] | Omit = omit,
    prompt_cache_key: Optional[str] | Omit = omit,
    prompt_cache_options: response_create_params.PromptCacheOptions | Omit = omit,
    prompt_cache_retention: Optional[Literal["in_memory", "24h"]] | Omit = omit,
    reasoning: Optional[Reasoning] | Omit = omit,
    safety_identifier: Optional[str] | Omit = omit,
    service_tier: Optional[ServiceTier] | Omit = omit,
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
    timeout: float | httpx2.Timeout | None | NotGiven = NOT_GIVEN,
) -> AsyncResponseStreamManager[TextFormatT]:
    new_response_args = {
        "access_programs": access_programs,
        "input": input,
        "model": model,
        "context_management": context_management,
        "conversation": conversation,
        "include": include,
        "instructions": instructions,
        "max_output_tokens": max_output_tokens,
        "max_tool_calls": max_tool_calls,
        "metadata": metadata,
        "moderation": moderation,
        "parallel_tool_calls": parallel_tool_calls,
        "previous_response_id": previous_response_id,
        "prompt": prompt,
        "prompt_cache_key": prompt_cache_key,
        "prompt_cache_options": prompt_cache_options,
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

        api_request = resource.create(
            access_programs=access_programs,
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
            moderation=moderation,
            parallel_tool_calls=parallel_tool_calls,
            previous_response_id=previous_response_id,
            prompt=prompt,
            prompt_cache_key=prompt_cache_key,
            prompt_cache_options=prompt_cache_options,
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

        api_request = resource.retrieve(
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


def _make_tools(tools: Iterable[ParseableToolParam] | Omit) -> List[ToolParam] | Omit:
    if not is_given(tools):
        return omit

    converted_tools: List[ToolParam] = []
    for tool in tools:
        if tool["type"] == "namespace":
            converted_tools.append({**tool, "tools": list(tool["tools"])})
            continue
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

        # Retain applicable options added to the compatibility definition.
        new_tool.update({key: value for key, value in function.items() if key not in new_tool})
        converted_tools.append(new_tool.cast())

    return converted_tools
