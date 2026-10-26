from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Dict, List, Type, Union, Iterable, Optional, cast
from functools import partial
from typing_extensions import Literal

import httpx2
import pydantic

from openai._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from openai._utils import maybe_transform, async_maybe_transform
from openai._streaming import Stream
from openai.types.chat import ChatCompletionAudioParam, completion_create_params
from openai._base_client import make_request_options
from openai.lib._parsing import (
    ResponseFormatT,
    validate_input_tools as _validate_input_tools,
    parse_chat_completion as _parse_chat_completion,
    materialize_input_tools as _materialize_input_tools,
    type_to_response_format_param as _type_to_response_format,
)
from openai.lib.streaming.chat import ChatCompletionStreamManager, AsyncChatCompletionStreamManager
from openai.types.shared.chat_model import ChatModel
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.shared_params.metadata import Metadata
from openai.types.shared.reasoning_effort import ReasoningEffort
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from openai.types.chat.parsed_chat_completion import ParsedChatCompletion
from openai.types.chat.chat_completion_audio_param import ChatCompletionAudioParam
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai.types.chat.chat_completion_tool_union_param import ChatCompletionToolUnionParam
from openai.types.chat.chat_completion_stream_options_param import ChatCompletionStreamOptionsParam
from openai.types.chat.chat_completion_prediction_content_param import ChatCompletionPredictionContentParam
from openai.types.chat.chat_completion_tool_choice_option_param import ChatCompletionToolChoiceOptionParam

if TYPE_CHECKING:
    from openai.resources.chat.completions.completions import Completions, AsyncCompletions


def parse(
    resource: Completions,
    *,
    messages: Iterable[ChatCompletionMessageParam],
    model: Union[str, ChatModel],
    audio: Optional[ChatCompletionAudioParam] | Omit = omit,
    response_format: type[ResponseFormatT] | Omit = omit,
    frequency_penalty: Optional[float] | Omit = omit,
    function_call: completion_create_params.FunctionCall | Omit = omit,
    functions: Iterable[completion_create_params.Function] | Omit = omit,
    logit_bias: Optional[Dict[str, int]] | Omit = omit,
    logprobs: Optional[bool] | Omit = omit,
    max_completion_tokens: Optional[int] | Omit = omit,
    max_tokens: Optional[int] | Omit = omit,
    metadata: Optional[Metadata] | Omit = omit,
    modalities: Optional[List[Literal["text", "audio"]]] | Omit = omit,
    moderation: Optional[completion_create_params.Moderation] | Omit = omit,
    n: Optional[int] | Omit = omit,
    parallel_tool_calls: bool | Omit = omit,
    prediction: Optional[ChatCompletionPredictionContentParam] | Omit = omit,
    presence_penalty: Optional[float] | Omit = omit,
    prompt_cache_key: Optional[str] | Omit = omit,
    prompt_cache_options: completion_create_params.PromptCacheOptions | Omit = omit,
    prompt_cache_retention: Optional[Literal["in_memory", "24h"]] | Omit = omit,
    reasoning_effort: Optional[ReasoningEffort] | Omit = omit,
    safety_identifier: Optional[str] | Omit = omit,
    seed: Optional[int] | Omit = omit,
    service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority", "fast"]] | Omit = omit,
    stop: Union[str, SequenceNotStr[str], None] | Omit = omit,
    store: Optional[bool] | Omit = omit,
    stream_options: Optional[ChatCompletionStreamOptionsParam] | Omit = omit,
    temperature: Optional[float] | Omit = omit,
    tool_choice: ChatCompletionToolChoiceOptionParam | Omit = omit,
    tools: Iterable[ChatCompletionToolUnionParam] | Omit = omit,
    top_logprobs: Optional[int] | Omit = omit,
    top_p: Optional[float] | Omit = omit,
    user: str | Omit = omit,
    verbosity: Optional[Literal["low", "medium", "high"]] | Omit = omit,
    web_search_options: completion_create_params.WebSearchOptions | Omit = omit,
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx2.Timeout | None | NotGiven = not_given,
) -> ParsedChatCompletion[ResponseFormatT]:
    chat_completion_tools = _validate_input_tools(tools)

    extra_headers = {
        "X-Stainless-Helper-Method": "chat.completions.parse",
        **(extra_headers or {}),
    }

    def parser(raw_completion: ChatCompletion) -> ParsedChatCompletion[ResponseFormatT]:
        return _parse_chat_completion(
            response_format=response_format,
            chat_completion=raw_completion,
            input_tools=chat_completion_tools,
        )

    return resource._post(
        "/chat/completions",
        body=maybe_transform(
            {
                "model": model,
                "stream": False,
                "service_tier": service_tier,
                "messages": messages,
                "audio": audio,
                "frequency_penalty": frequency_penalty,
                "function_call": function_call,
                "functions": functions,
                "logit_bias": logit_bias,
                "logprobs": logprobs,
                "max_completion_tokens": max_completion_tokens,
                "max_tokens": max_tokens,
                "metadata": metadata,
                "modalities": modalities,
                "moderation": moderation,
                "n": n,
                "parallel_tool_calls": parallel_tool_calls,
                "prediction": prediction,
                "presence_penalty": presence_penalty,
                "prompt_cache_key": prompt_cache_key,
                "prompt_cache_options": prompt_cache_options,
                "prompt_cache_retention": prompt_cache_retention,
                "reasoning_effort": reasoning_effort,
                "response_format": _type_to_response_format(response_format),
                "safety_identifier": safety_identifier,
                "seed": seed,
                "stop": stop,
                "store": store,
                "stream_options": stream_options,
                "temperature": temperature,
                "tool_choice": tool_choice,
                "tools": chat_completion_tools,
                "top_logprobs": top_logprobs,
                "top_p": top_p,
                "user": user,
                "verbosity": verbosity,
                "web_search_options": web_search_options,
            },
            completion_create_params.CompletionCreateParams,
        ),
        options=make_request_options(
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            post_parser=parser,
            security={"bearer_auth": True},
        ),
        # we turn the `ChatCompletion` instance into a `ParsedChatCompletion`
        # in the `parser` function above
        cast_to=cast(Type[ParsedChatCompletion[ResponseFormatT]], ChatCompletion),
        stream=False,
    )


async def async_parse(
    resource: AsyncCompletions,
    *,
    messages: Iterable[ChatCompletionMessageParam],
    model: Union[str, ChatModel],
    audio: Optional[ChatCompletionAudioParam] | Omit = omit,
    response_format: type[ResponseFormatT] | Omit = omit,
    frequency_penalty: Optional[float] | Omit = omit,
    function_call: completion_create_params.FunctionCall | Omit = omit,
    functions: Iterable[completion_create_params.Function] | Omit = omit,
    logit_bias: Optional[Dict[str, int]] | Omit = omit,
    logprobs: Optional[bool] | Omit = omit,
    max_completion_tokens: Optional[int] | Omit = omit,
    max_tokens: Optional[int] | Omit = omit,
    metadata: Optional[Metadata] | Omit = omit,
    modalities: Optional[List[Literal["text", "audio"]]] | Omit = omit,
    moderation: Optional[completion_create_params.Moderation] | Omit = omit,
    n: Optional[int] | Omit = omit,
    parallel_tool_calls: bool | Omit = omit,
    prediction: Optional[ChatCompletionPredictionContentParam] | Omit = omit,
    presence_penalty: Optional[float] | Omit = omit,
    prompt_cache_key: Optional[str] | Omit = omit,
    prompt_cache_options: completion_create_params.PromptCacheOptions | Omit = omit,
    prompt_cache_retention: Optional[Literal["in_memory", "24h"]] | Omit = omit,
    reasoning_effort: Optional[ReasoningEffort] | Omit = omit,
    safety_identifier: Optional[str] | Omit = omit,
    seed: Optional[int] | Omit = omit,
    service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority", "fast"]] | Omit = omit,
    stop: Union[str, SequenceNotStr[str], None] | Omit = omit,
    store: Optional[bool] | Omit = omit,
    stream_options: Optional[ChatCompletionStreamOptionsParam] | Omit = omit,
    temperature: Optional[float] | Omit = omit,
    tool_choice: ChatCompletionToolChoiceOptionParam | Omit = omit,
    tools: Iterable[ChatCompletionToolUnionParam] | Omit = omit,
    top_logprobs: Optional[int] | Omit = omit,
    top_p: Optional[float] | Omit = omit,
    user: str | Omit = omit,
    verbosity: Optional[Literal["low", "medium", "high"]] | Omit = omit,
    web_search_options: completion_create_params.WebSearchOptions | Omit = omit,
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx2.Timeout | None | NotGiven = not_given,
) -> ParsedChatCompletion[ResponseFormatT]:
    chat_completion_tools = _validate_input_tools(tools)

    extra_headers = {
        "X-Stainless-Helper-Method": "chat.completions.parse",
        **(extra_headers or {}),
    }

    def parser(raw_completion: ChatCompletion) -> ParsedChatCompletion[ResponseFormatT]:
        return _parse_chat_completion(
            response_format=response_format,
            chat_completion=raw_completion,
            input_tools=chat_completion_tools,
        )

    return await resource._post(
        "/chat/completions",
        body=await async_maybe_transform(
            {
                "model": model,
                "stream": False,
                "service_tier": service_tier,
                "messages": messages,
                "audio": audio,
                "frequency_penalty": frequency_penalty,
                "function_call": function_call,
                "functions": functions,
                "logit_bias": logit_bias,
                "logprobs": logprobs,
                "max_completion_tokens": max_completion_tokens,
                "max_tokens": max_tokens,
                "metadata": metadata,
                "modalities": modalities,
                "moderation": moderation,
                "n": n,
                "parallel_tool_calls": parallel_tool_calls,
                "prediction": prediction,
                "presence_penalty": presence_penalty,
                "prompt_cache_key": prompt_cache_key,
                "prompt_cache_options": prompt_cache_options,
                "prompt_cache_retention": prompt_cache_retention,
                "reasoning_effort": reasoning_effort,
                "response_format": _type_to_response_format(response_format),
                "safety_identifier": safety_identifier,
                "seed": seed,
                "store": store,
                "stop": stop,
                "stream_options": stream_options,
                "temperature": temperature,
                "tool_choice": tool_choice,
                "tools": chat_completion_tools,
                "top_logprobs": top_logprobs,
                "top_p": top_p,
                "user": user,
                "verbosity": verbosity,
                "web_search_options": web_search_options,
            },
            completion_create_params.CompletionCreateParams,
        ),
        options=make_request_options(
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            post_parser=parser,
            security={"bearer_auth": True},
        ),
        # we turn the `ChatCompletion` instance into a `ParsedChatCompletion`
        # in the `parser` function above
        cast_to=cast(Type[ParsedChatCompletion[ResponseFormatT]], ChatCompletion),
        stream=False,
    )


def stream(
    resource: Completions,
    *,
    messages: Iterable[ChatCompletionMessageParam],
    model: Union[str, ChatModel],
    audio: Optional[ChatCompletionAudioParam] | Omit = omit,
    response_format: completion_create_params.ResponseFormat | type[ResponseFormatT] | Omit = omit,
    frequency_penalty: Optional[float] | Omit = omit,
    function_call: completion_create_params.FunctionCall | Omit = omit,
    functions: Iterable[completion_create_params.Function] | Omit = omit,
    logit_bias: Optional[Dict[str, int]] | Omit = omit,
    logprobs: Optional[bool] | Omit = omit,
    max_completion_tokens: Optional[int] | Omit = omit,
    max_tokens: Optional[int] | Omit = omit,
    metadata: Optional[Metadata] | Omit = omit,
    modalities: Optional[List[Literal["text", "audio"]]] | Omit = omit,
    moderation: Optional[completion_create_params.Moderation] | Omit = omit,
    n: Optional[int] | Omit = omit,
    parallel_tool_calls: bool | Omit = omit,
    prediction: Optional[ChatCompletionPredictionContentParam] | Omit = omit,
    presence_penalty: Optional[float] | Omit = omit,
    prompt_cache_key: Optional[str] | Omit = omit,
    prompt_cache_options: completion_create_params.PromptCacheOptions | Omit = omit,
    prompt_cache_retention: Optional[Literal["in_memory", "24h"]] | Omit = omit,
    reasoning_effort: Optional[ReasoningEffort] | Omit = omit,
    safety_identifier: Optional[str] | Omit = omit,
    seed: Optional[int] | Omit = omit,
    service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority", "fast"]] | Omit = omit,
    stop: Union[str, SequenceNotStr[str], None] | Omit = omit,
    store: Optional[bool] | Omit = omit,
    stream_options: Optional[ChatCompletionStreamOptionsParam] | Omit = omit,
    temperature: Optional[float] | Omit = omit,
    tool_choice: ChatCompletionToolChoiceOptionParam | Omit = omit,
    tools: Iterable[ChatCompletionToolUnionParam] | Omit = omit,
    top_logprobs: Optional[int] | Omit = omit,
    top_p: Optional[float] | Omit = omit,
    user: str | Omit = omit,
    verbosity: Optional[Literal["low", "medium", "high"]] | Omit = omit,
    web_search_options: completion_create_params.WebSearchOptions | Omit = omit,
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx2.Timeout | None | NotGiven = not_given,
) -> ChatCompletionStreamManager[ResponseFormatT]:
    chat_completion_tools = _materialize_input_tools(tools)

    extra_headers = {
        "X-Stainless-Helper-Method": "chat.completions.stream",
        **(extra_headers or {}),
    }

    api_request: partial[Stream[ChatCompletionChunk]] = partial(
        resource.create,
        messages=messages,
        model=model,
        audio=audio,
        stream=True,
        response_format=_type_to_response_format(response_format),
        frequency_penalty=frequency_penalty,
        function_call=function_call,
        functions=functions,
        logit_bias=logit_bias,
        logprobs=logprobs,
        max_completion_tokens=max_completion_tokens,
        max_tokens=max_tokens,
        metadata=metadata,
        modalities=modalities,
        moderation=moderation,
        n=n,
        parallel_tool_calls=parallel_tool_calls,
        prediction=prediction,
        presence_penalty=presence_penalty,
        prompt_cache_key=prompt_cache_key,
        prompt_cache_options=prompt_cache_options,
        prompt_cache_retention=prompt_cache_retention,
        reasoning_effort=reasoning_effort,
        safety_identifier=safety_identifier,
        seed=seed,
        service_tier=service_tier,
        store=store,
        stop=stop,
        stream_options=stream_options,
        temperature=temperature,
        tool_choice=tool_choice,
        tools=chat_completion_tools,
        top_logprobs=top_logprobs,
        top_p=top_p,
        user=user,
        verbosity=verbosity,
        web_search_options=web_search_options,
        extra_headers=extra_headers,
        extra_query=extra_query,
        extra_body=extra_body,
        timeout=timeout,
    )
    return ChatCompletionStreamManager(
        api_request,
        response_format=response_format,
        input_tools=chat_completion_tools,
    )


def async_stream(
    resource: AsyncCompletions,
    *,
    messages: Iterable[ChatCompletionMessageParam],
    model: Union[str, ChatModel],
    audio: Optional[ChatCompletionAudioParam] | Omit = omit,
    response_format: completion_create_params.ResponseFormat | type[ResponseFormatT] | Omit = omit,
    frequency_penalty: Optional[float] | Omit = omit,
    function_call: completion_create_params.FunctionCall | Omit = omit,
    functions: Iterable[completion_create_params.Function] | Omit = omit,
    logit_bias: Optional[Dict[str, int]] | Omit = omit,
    logprobs: Optional[bool] | Omit = omit,
    max_completion_tokens: Optional[int] | Omit = omit,
    max_tokens: Optional[int] | Omit = omit,
    metadata: Optional[Metadata] | Omit = omit,
    modalities: Optional[List[Literal["text", "audio"]]] | Omit = omit,
    moderation: Optional[completion_create_params.Moderation] | Omit = omit,
    n: Optional[int] | Omit = omit,
    parallel_tool_calls: bool | Omit = omit,
    prediction: Optional[ChatCompletionPredictionContentParam] | Omit = omit,
    presence_penalty: Optional[float] | Omit = omit,
    prompt_cache_key: Optional[str] | Omit = omit,
    prompt_cache_options: completion_create_params.PromptCacheOptions | Omit = omit,
    prompt_cache_retention: Optional[Literal["in_memory", "24h"]] | Omit = omit,
    reasoning_effort: Optional[ReasoningEffort] | Omit = omit,
    safety_identifier: Optional[str] | Omit = omit,
    seed: Optional[int] | Omit = omit,
    service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority", "fast"]] | Omit = omit,
    stop: Union[str, SequenceNotStr[str], None] | Omit = omit,
    store: Optional[bool] | Omit = omit,
    stream_options: Optional[ChatCompletionStreamOptionsParam] | Omit = omit,
    temperature: Optional[float] | Omit = omit,
    tool_choice: ChatCompletionToolChoiceOptionParam | Omit = omit,
    tools: Iterable[ChatCompletionToolUnionParam] | Omit = omit,
    top_logprobs: Optional[int] | Omit = omit,
    top_p: Optional[float] | Omit = omit,
    user: str | Omit = omit,
    verbosity: Optional[Literal["low", "medium", "high"]] | Omit = omit,
    web_search_options: completion_create_params.WebSearchOptions | Omit = omit,
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx2.Timeout | None | NotGiven = not_given,
) -> AsyncChatCompletionStreamManager[ResponseFormatT]:
    chat_completion_tools = _materialize_input_tools(tools)

    extra_headers = {
        "X-Stainless-Helper-Method": "chat.completions.stream",
        **(extra_headers or {}),
    }

    api_request = resource.create(
        messages=messages,
        model=model,
        audio=audio,
        stream=True,
        response_format=_type_to_response_format(response_format),
        frequency_penalty=frequency_penalty,
        function_call=function_call,
        functions=functions,
        logit_bias=logit_bias,
        logprobs=logprobs,
        max_completion_tokens=max_completion_tokens,
        max_tokens=max_tokens,
        metadata=metadata,
        modalities=modalities,
        moderation=moderation,
        n=n,
        parallel_tool_calls=parallel_tool_calls,
        prediction=prediction,
        presence_penalty=presence_penalty,
        prompt_cache_key=prompt_cache_key,
        prompt_cache_options=prompt_cache_options,
        prompt_cache_retention=prompt_cache_retention,
        reasoning_effort=reasoning_effort,
        safety_identifier=safety_identifier,
        seed=seed,
        service_tier=service_tier,
        stop=stop,
        store=store,
        stream_options=stream_options,
        temperature=temperature,
        tool_choice=tool_choice,
        tools=chat_completion_tools,
        top_logprobs=top_logprobs,
        top_p=top_p,
        user=user,
        verbosity=verbosity,
        web_search_options=web_search_options,
        extra_headers=extra_headers,
        extra_query=extra_query,
        extra_body=extra_body,
        timeout=timeout,
    )
    return AsyncChatCompletionStreamManager(
        api_request,
        response_format=response_format,
        input_tools=chat_completion_tools,
    )


def validate_response_format(response_format: object) -> None:
    if inspect.isclass(response_format) and issubclass(response_format, pydantic.BaseModel):
        raise TypeError(
            "You tried to pass a `BaseModel` class to `chat.completions.create()`; You must use `chat.completions.parse()` instead"
        )
