from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Iterable, cast
from typing_extensions import TypeVar, TypeGuard, assert_never

import pydantic

from .._tools import PydanticFunctionTool
from ..._types import NOT_GIVEN, NotGiven
from ..._utils import is_dict, is_given
from ..._compat import PYDANTIC_V2, model_parse_json
from ..._models import construct_type_unchecked
from .._pydantic import is_basemodel_type, to_strict_json_schema, is_dataclass_like_type
from ...types.chat import (
    ParsedChoice,
    ChatCompletion,
    ParsedFunction,
    ParsedChatCompletion,
    ChatCompletionMessage,
    ParsedFunctionToolCall,
    ChatCompletionToolParam,
    ParsedChatCompletionMessage,
    completion_create_params,
)
from ..._exceptions import LengthFinishReasonError, ContentFilterFinishReasonError
from ...types.shared_params import FunctionDefinition
from ...types.chat.completion_create_params import ResponseFormat as ResponseFormatParam
from ...types.chat.chat_completion_message_tool_call import Function

ResponseFormatT = TypeVar(
    "ResponseFormatT",
    # if it isn't given then we don't do any parsing
    default=None,
)
_default_response_format: None = None


def validate_input_tools(
    tools: Iterable[ChatCompletionToolParam] | NotGiven = NOT_GIVEN,
) -> None:
    if not is_given(tools):
        return

    for tool in tools:
        if tool["type"] != "function":
            raise ValueError(
                f'Currently only `function` tool types support auto-parsing; Received `{tool["type"]}`',
            )

        strict = tool["function"].get("strict")
        if strict is not True:
            raise ValueError(
                f'`{tool["function"]["name"]}` is not strict. Only `strict` function tools can be auto-parsed'
            )


def parse_chat_completion(
    *,
    response_format: type[ResponseFormatT] | completion_create_params.ResponseFormat | NotGiven,
    input_tools: Iterable[ChatCompletionToolParam] | NotGiven,
    chat_completion: ChatCompletion | ParsedChatCompletion[object],
) -> ParsedChatCompletion[ResponseFormatT]:
    if is_given(input_tools):
        input_tools = [t for t in input_tools]
    else:
        input_tools = []

    choices: list[ParsedChoice[ResponseFormatT]] = []
    for choice in chat_completion.choices:
        if choice.finish_reason == "length":
            raise LengthFinishReasonError()

        if choice.finish_reason == "content_filter":
            raise ContentFilterFinishReasonError()

        message = choice.message

        tool_calls: list[ParsedFunctionToolCall] = []
        if message.tool_calls:
            for tool_call in message.tool_calls:
                if tool_call.type == "function":
                    tool_call_dict = tool_call.to_dict()
                    tool_calls.append(
                        construct_type_unchecked(
                            value={
                                **tool_call_dict,
                                "function": {
                                    **cast(Any, tool_call_dict["function"]),
                                    "parsed_arguments": parse_function_tool_arguments(
                                        input_tools=input_tools, function=tool_call.function
                                    ),
                                },
                            },
                            type_=ParsedFunctionToolCall,
                        )
                    )
                elif TYPE_CHECKING:  # type: ignore[unreachable]
                    assert_never(tool_call)
                else:
                    tool_calls.append(tool_call)

        choices.append(
            construct_type_unchecked(
                type_=cast(Any, ParsedChoice)[solve_response_format_t(response_format)],
                value={
                    **choice.to_dict(),
                    "message": {
                        **message.to_dict(),
                        "parsed": maybe_parse_content(
                            response_format=response_format,
                            message=message,
                        ),
                        "tool_calls": tool_calls,
                    },
                },
            )
        )

    return cast(
        ParsedChatCompletion[ResponseFormatT],
        construct_type_unchecked(
            type_=cast(Any, ParsedChatCompletion)[solve_response_format_t(response_format)],
            value={
                **chat_completion.to_dict(),
                "choices": choices,
            },
        ),
    )


def get_input_tool_by_name(*, input_tools: list[ChatCompletionToolParam], name: str) -> ChatCompletionToolParam | None:
    return next((t for t in input_tools if t.get("function", {}).get("name") == name), None)


def parse_function_tool_arguments(
    *, input_tools: list[ChatCompletionToolParam], function: Function | ParsedFunction
) -> object:
    input_tool = get_input_tool_by_name(input_tools=input_tools, name=function.name)
    if not input_tool:
        return None

    input_fn = cast(object, input_tool.get("function"))
    if isinstance(input_fn, PydanticFunctionTool):
        return model_parse_json(input_fn.model, function.arguments)

    input_fn = cast(FunctionDefinition, input_fn)

    if not input_fn.get("strict"):
        return None

    return json.loads(function.arguments)


def maybe_parse_content(
    *,
    response_format: type[ResponseFormatT] | ResponseFormatParam | NotGiven,
    message: ChatCompletionMessage | ParsedChatCompletionMessage[object],
) -> ResponseFormatT | None:
    if has_rich_response_format(response_format) and message.content is not None and not message.refusal:
        return _parse_content(response_format, message.content)

    return None


def solve_response_format_t(
    response_format: type[ResponseFormatT] | ResponseFormatParam | NotGiven,
) -> type[ResponseFormatT]:
    """Return the runtime type for the given response format.

    If no response format is given, or if we won't auto-parse the response format
    then we default to `None`.
    """
    if has_rich_response_format(response_format):
        return response_format

    return cast("type[ResponseFormatT]", _default_response_format)


def has_parseable_input(
    *,
    response_format: type | ResponseFormatParam | NotGiven,
    input_tools: Iterable[ChatCompletionToolParam] | NotGiven = NOT_GIVEN,
) -> bool:
    if has_rich_response_format(response_format):
        return True

    for input_tool in input_tools or []:
        if is_parseable_tool(input_tool):
            return True

    return False


def has_rich_response_format(
    response_format: type[ResponseFormatT] | ResponseFormatParam | NotGiven,
) -> TypeGuard[type[ResponseFormatT]]:
    if not is_given(response_format):
        return False

    if is_response_format_param(response_format):
        return False

    return True


def is_response_format_param(response_format: object) -> TypeGuard[ResponseFormatParam]:
    return is_dict(response_format)


def is_parseable_tool(input_tool: ChatCompletionToolParam) -> bool:
    input_fn = cast(object, input_tool.get("function"))
    if isinstance(input_fn, PydanticFunctionTool):
        return True

    return cast(FunctionDefinition, input_fn).get("strict") or False


def _parse_content(response_format: type[ResponseFormatT], content: str) -> ResponseFormatT:
    if is_basemodel_type(response_format):
        return cast(ResponseFormatT, model_parse_json(response_format, content))

    if is_dataclass_like_type(response_format):
        if not PYDANTIC_V2:
            raise TypeError(f"Non BaseModel types are only supported with Pydantic v2 - {response_format}")

        return pydantic.TypeAdapter(response_format).validate_json(content)

    raise TypeError(f"Unable to automatically parse response format type {response_format}")


def type_to_response_format_param(
    response_format: type | completion_create_params.ResponseFormat | NotGiven,
) -> ResponseFormatParam | NotGiven:
    if not is_given(response_format):
        return NOT_GIVEN

    if is_response_format_param(response_format):
        return response_format

    # type checkers don't narrow the negation of a `TypeGuard` as it isn't
    # a safe default behaviour but we know that at this point the `response_format`
    # can only be a `type`
    response_format = cast(type, response_format)

    json_schema_type: type[pydantic.BaseModel] | pydantic.TypeAdapter[Any] | None = None

    if is_basemodel_type(response_format):
        name = response_format.__name__
        json_schema_type = response_format
    elif is_dataclass_like_type(response_format):
        name = response_format.__name__
        json_schema_type = pydantic.TypeAdapter(response_format)
    else:
        raise TypeError(f"Unsupported response_format type - {response_format}")

    return {
        "type": "json_schema",
        "json_schema": {
            "schema": to_strict_json_schema(json_schema_type),
            "name": name,
            "strict": True,
        },
    }
