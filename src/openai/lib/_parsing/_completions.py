from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any, Iterable, cast
from typing_extensions import TypeVar, TypeGuard, assert_never

import pydantic

from .._tools import PydanticFunctionTool
from ..._types import Omit, omit
from ..._utils import is_dict, is_given
from ..._compat import PYDANTIC_V1, model_parse_json
from ..._models import construct_type_unchecked
from .._pydantic import is_basemodel_type, to_strict_json_schema, is_dataclass_like_type
from ...types.chat import (
    ParsedChoice,
    ChatCompletion,
    ParsedFunction,
    ParsedChatCompletion,
    ChatCompletionMessage,
    ParsedFunctionToolCall,
    ParsedChatCompletionMessage,
    ChatCompletionToolUnionParam,
    ChatCompletionFunctionToolParam,
    completion_create_params,
)
from ..._exceptions import LengthFinishReasonError, ContentFilterFinishReasonError
from ...types.shared_params import FunctionDefinition
from ...types.chat.completion_create_params import ResponseFormat as ResponseFormatParam
from ...types.chat.chat_completion_message_function_tool_call import Function

ResponseFormatT = TypeVar(
    "ResponseFormatT",
    # if it isn't given then we don't do any parsing
    default=None,
)
_default_response_format: None = None

log: logging.Logger = logging.getLogger("openai.lib.parsing")


def is_strict_chat_completion_tool_param(
    tool: ChatCompletionToolUnionParam,
) -> TypeGuard[ChatCompletionFunctionToolParam]:
    """Check if the given tool is a strict ChatCompletionFunctionToolParam."""
    if not tool["type"] == "function":
        return False
    if tool["function"].get("strict") is not True:
        return False

    return True


def select_strict_chat_completion_tools(
    tools: Iterable[ChatCompletionToolUnionParam] | Omit = omit,
) -> Iterable[ChatCompletionFunctionToolParam] | Omit:
    """Select only the strict ChatCompletionFunctionToolParams from the given tools."""
    if not is_given(tools):
        return omit

    return [t for t in tools if is_strict_chat_completion_tool_param(t)]


def validate_input_tools(
    tools: Iterable[ChatCompletionToolUnionParam] | Omit = omit,
) -> Iterable[ChatCompletionFunctionToolParam] | Omit:
    """Validate that all *tools* are strict function tools suitable for auto-parsing.

    Raises :class:`ValueError` if any tool is not of type ``function`` or does not
    have ``strict`` set to ``True``.
    """
    if not is_given(tools):
        return omit

    for tool in tools:
        if tool["type"] != "function":
            raise ValueError(
                f"Currently only `function` tool types support auto-parsing; Received `{tool['type']}`",
            )

        strict = tool["function"].get("strict")
        if strict is not True:
            raise ValueError(
                f"`{tool['function']['name']}` is not strict. Only `strict` function tools can be auto-parsed"
            )

    return cast(Iterable[ChatCompletionFunctionToolParam], tools)


def parse_chat_completion(
    *,
    response_format: type[ResponseFormatT] | completion_create_params.ResponseFormat | Omit,
    input_tools: Iterable[ChatCompletionToolUnionParam] | Omit,
    chat_completion: ChatCompletion | ParsedChatCompletion[object],
) -> ParsedChatCompletion[ResponseFormatT]:
    """Parse a raw :class:`ChatCompletion` into a :class:`ParsedChatCompletion`.

    Tool call arguments are deserialized using the corresponding *input_tools*
    definitions, and ``message.content`` is parsed according to *response_format*
    when a rich (class) format is provided.

    Raises :class:`~openai.LengthFinishReasonError` if any choice has
    ``finish_reason="length"`` and :class:`~openai.ContentFilterFinishReasonError`
    if ``finish_reason="content_filter"``.
    """
    if is_given(input_tools):
        input_tools = [t for t in input_tools]
    else:
        input_tools = []

    choices: list[ParsedChoice[ResponseFormatT]] = []
    for choice in chat_completion.choices:
        if choice.finish_reason == "length":
            raise LengthFinishReasonError(completion=chat_completion)

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
                elif tool_call.type == "custom":
                    # warn user that custom tool calls are not callable here
                    log.warning(
                        "Custom tool calls are not callable. Ignoring tool call: %s - %s",
                        tool_call.id,
                        tool_call.custom.name,
                        stacklevel=2,
                    )
                elif TYPE_CHECKING:  # type: ignore[unreachable]
                    assert_never(tool_call)
                else:
                    tool_calls.append(tool_call)

        choices.append(
            construct_type_unchecked(
                type_=ParsedChoice[ResponseFormatT],
                value={
                    **choice.to_dict(),
                    "message": {
                        **message.to_dict(),
                        "parsed": maybe_parse_content(
                            response_format=response_format,
                            message=message,
                        ),
                        "tool_calls": tool_calls if tool_calls else None,
                    },
                },
            )
        )

    return construct_type_unchecked(
        type_=ParsedChatCompletion[ResponseFormatT],
        value={
            **chat_completion.to_dict(),
            "choices": choices,
        },
    )


def get_input_tool_by_name(
    *, input_tools: list[ChatCompletionToolUnionParam], name: str
) -> ChatCompletionFunctionToolParam | None:
    """Look up the first function tool in *input_tools* whose name matches *name*.

    Returns ``None`` if no matching tool is found.
    """
    return next((t for t in input_tools if t["type"] == "function" and t.get("function", {}).get("name") == name), None)


def parse_function_tool_arguments(
    *, input_tools: list[ChatCompletionToolUnionParam], function: Function | ParsedFunction
) -> object | None:
    """Deserialize the JSON ``arguments`` of a function tool call.

    If the matching input tool wraps a Pydantic model, the arguments are
    validated and returned as a model instance.  For other strict tools the
    raw JSON is decoded.  Returns ``None`` when no matching tool is found or
    the tool is not strict.
    """
    input_tool = get_input_tool_by_name(input_tools=input_tools, name=function.name)
    if not input_tool:
        return None

    input_fn = cast(object, input_tool.get("function"))
    if isinstance(input_fn, PydanticFunctionTool):
        return model_parse_json(input_fn.model, function.arguments)

    input_fn = cast(FunctionDefinition, input_fn)

    if not input_fn.get("strict"):
        return None

    return json.loads(function.arguments)  # type: ignore[no-any-return]


def maybe_parse_content(
    *,
    response_format: type[ResponseFormatT] | ResponseFormatParam | Omit,
    message: ChatCompletionMessage | ParsedChatCompletionMessage[object],
) -> ResponseFormatT | None:
    """Parse the message content into *response_format* if applicable.

    Returns ``None`` when *response_format* is not a rich type, the message
    has no content, or the message contains a refusal.
    """
    if has_rich_response_format(response_format) and message.content and not message.refusal:
        return _parse_content(response_format, message.content)

    return None


def has_parseable_input(
    *,
    response_format: type | ResponseFormatParam | Omit,
    input_tools: Iterable[ChatCompletionToolUnionParam] | Omit = omit,
) -> bool:
    """Return ``True`` if the request configuration contains anything that can be auto-parsed.

    This is the case when *response_format* is a rich type (e.g. a Pydantic model)
    or at least one of the *input_tools* is a parseable strict function tool.
    """
    if has_rich_response_format(response_format):
        return True

    for input_tool in input_tools or []:
        if is_parseable_tool(input_tool):
            return True

    return False


def has_rich_response_format(
    response_format: type[ResponseFormatT] | ResponseFormatParam | Omit,
) -> TypeGuard[type[ResponseFormatT]]:
    """Return ``True`` if *response_format* is a class type (not a dict param or omitted)."""
    if not is_given(response_format):
        return False

    if is_response_format_param(response_format):
        return False

    return True


def is_response_format_param(response_format: object) -> TypeGuard[ResponseFormatParam]:
    """Return ``True`` if *response_format* is a dictionary-style response format parameter."""
    return is_dict(response_format)


def is_parseable_tool(input_tool: ChatCompletionToolUnionParam) -> bool:
    """Return ``True`` if *input_tool* is a strict function tool that can be auto-parsed."""
    if input_tool["type"] != "function":
        return False

    input_fn = cast(object, input_tool.get("function"))
    if isinstance(input_fn, PydanticFunctionTool):
        return True

    return cast(FunctionDefinition, input_fn).get("strict") or False


def _parse_content(response_format: type[ResponseFormatT], content: str) -> ResponseFormatT:
    if is_basemodel_type(response_format):
        return cast(ResponseFormatT, model_parse_json(response_format, content))

    if is_dataclass_like_type(response_format):
        if PYDANTIC_V1:
            raise TypeError(f"Non BaseModel types are only supported with Pydantic v2 - {response_format}")

        return pydantic.TypeAdapter(response_format).validate_json(content)

    raise TypeError(f"Unable to automatically parse response format type {response_format}")


def type_to_response_format_param(
    response_format: type | completion_create_params.ResponseFormat | Omit,
) -> ResponseFormatParam | Omit:
    """Convert a *response_format* type into the ``json_schema`` parameter dict expected by the API.

    If *response_format* is already a dict parameter it is returned as-is. Pydantic models
    and ``@pydantic.dataclass`` types are converted to a strict JSON schema.
    """
    if not is_given(response_format):
        return omit

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
