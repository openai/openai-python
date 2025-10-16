from __future__ import annotations


import json
import logging
import threading
from typing import TYPE_CHECKING, Any, Iterable, cast
from typing_extensions import TypeVar, TypeGuard, assert_never
from functools import lru_cache


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


# ============================================================================
# FIX for Issue #2672: Thread-safe bounded TypeAdapter cache
# ============================================================================

_MAX_TYPE_ADAPTER_CACHE_SIZE = 128
_type_adapter_lock = threading.Lock()
_thread_local = threading.local()


def _get_type_cache_key(type_: Any) -> str:
    """
    Generate a stable cache key for a type.
    
    Uses type name and module information to create a key that
    remains consistent across type recreations, preventing hash
    conflicts in multi-threaded environments.
    
    Args:
        type_: The type to generate a key for
        
    Returns:
        A string key that uniquely identifies the type
    """
    try:
        # For generic types, extract the origin and args
        if hasattr(type_, '__origin__'):
            origin = type_.__origin__
            args = getattr(type_, '__args__', ())
            
            origin_key = f"{origin.__module__}.{origin.__qualname__}"
            if args:
                args_keys = ','.join(_get_type_cache_key(arg) for arg in args)
                return f"{origin_key}[{args_keys}]"
            return origin_key
        else:
            # For regular types
            return f"{type_.__module__}.{type_.__qualname__}"
    except (AttributeError, TypeError):
        # Fallback to repr for complex types
        return repr(type_)


def _get_cached_type_adapter(type_: type[ResponseFormatT]) -> pydantic.TypeAdapter[ResponseFormatT]:
    """
    Get a cached TypeAdapter for the given type.
    
    Uses thread-local storage with bounded cache size to prevent
    memory leaks in multi-threaded environments (Issue #2672).
    
    Args:
        type_: The type to create an adapter for
        
    Returns:
        A TypeAdapter instance for the given type
    """
    # Get or create thread-local cache
    if not hasattr(_thread_local, 'adapter_cache'):
        _thread_local.adapter_cache = {}
    
    cache = _thread_local.adapter_cache
    
    # Use stable type name as key instead of type hash
    cache_key = _get_type_cache_key(type_)
    
    if cache_key not in cache:
        # Implement simple FIFO eviction if cache exceeds limit
        if len(cache) >= _MAX_TYPE_ADAPTER_CACHE_SIZE:
            # Remove oldest entry
            first_key = next(iter(cache))
            del cache[first_key]
            log.debug(
                "TypeAdapter cache size limit reached (%d), evicted oldest entry",
                _MAX_TYPE_ADAPTER_CACHE_SIZE
            )
        
        # Create new TypeAdapter
        cache[cache_key] = pydantic.TypeAdapter(type_)
        log.debug("Created new TypeAdapter for type: %s", cache_key)
    
    return cache[cache_key]


# Alternative: Global bounded cache with locking (use if thread-local has issues)
@lru_cache(maxsize=_MAX_TYPE_ADAPTER_CACHE_SIZE)
def _get_cached_type_adapter_global(cache_key: str, type_repr: str) -> Any:
    """
    Global cached TypeAdapter factory with bounded LRU cache.
    
    This is an alternative to thread-local caching. The actual TypeAdapter
    must be created outside this function and cached separately.
    
    Note: This function serves as a cache key manager only.
    """
    # This is used as a bounded LRU cache manager
    # The actual TypeAdapter creation happens in the calling function
    return None


def _get_cached_type_adapter_with_lock(type_: type[ResponseFormatT]) -> pydantic.TypeAdapter[ResponseFormatT]:
    """
    Get a cached TypeAdapter using global cache with explicit locking.
    
    Alternative implementation using a global cache protected by locks.
    Use _get_cached_type_adapter() for better thread isolation.
    
    Args:
        type_: The type to create an adapter for
        
    Returns:
        A TypeAdapter instance for the given type
    """
    if not hasattr(_get_cached_type_adapter_with_lock, '_global_cache'):
        _get_cached_type_adapter_with_lock._global_cache = {}
    
    cache_key = _get_type_cache_key(type_)
    
    with _type_adapter_lock:
        cache = _get_cached_type_adapter_with_lock._global_cache
        
        if cache_key not in cache:
            if len(cache) >= _MAX_TYPE_ADAPTER_CACHE_SIZE:
                # Remove first entry (FIFO)
                first_key = next(iter(cache))
                del cache[first_key]
            
            cache[cache_key] = pydantic.TypeAdapter(type_)
        
        return cache[cache_key]


# ============================================================================
# End of fix for Issue #2672
# ============================================================================


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
                type_=cast(Any, ParsedChoice)[solve_response_format_t(response_format)],
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


def get_input_tool_by_name(
    *, input_tools: list[ChatCompletionToolUnionParam], name: str
) -> ChatCompletionFunctionToolParam | None:
    return next((t for t in input_tools if t["type"] == "function" and t.get("function", {}).get("name") == name), None)


def parse_function_tool_arguments(
    *, input_tools: list[ChatCompletionToolUnionParam], function: Function | ParsedFunction
) -> object | None:
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
    if has_rich_response_format(response_format) and message.content and not message.refusal:
        return _parse_content(response_format, message.content)

    return None


def solve_response_format_t(
    response_format: type[ResponseFormatT] | ResponseFormatParam | Omit,
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
    response_format: type | ResponseFormatParam | Omit,
    input_tools: Iterable[ChatCompletionToolUnionParam] | Omit = omit,
) -> bool:
    if has_rich_response_format(response_format):
        return True

    for input_tool in input_tools or []:
        if is_parseable_tool(input_tool):
            return True

    return False


def has_rich_response_format(
    response_format: type[ResponseFormatT] | ResponseFormatParam | Omit,
) -> TypeGuard[type[ResponseFormatT]]:
    if not is_given(response_format):
        return False

    if is_response_format_param(response_format):
        return False

    return True


def is_response_format_param(response_format: object) -> TypeGuard[ResponseFormatParam]:
    return is_dict(response_format)


def is_parseable_tool(input_tool: ChatCompletionToolUnionParam) -> bool:
    if input_tool["type"] != "function":
        return False

    input_fn = cast(object, input_tool.get("function"))
    if isinstance(input_fn, PydanticFunctionTool):
        return True

    return cast(FunctionDefinition, input_fn).get("strict") or False


def _parse_content(response_format: type[ResponseFormatT], content: str) -> ResponseFormatT:
    """
    Parse content string into the specified response format.
    
    FIXED: Uses bounded thread-safe TypeAdapter cache to prevent memory leaks
    in multi-threaded environments (Issue #2672).
    
    Args:
        response_format: The target type for parsing
        content: The JSON string content to parse
        
    Returns:
        Parsed content of type ResponseFormatT
        
    Raises:
        TypeError: If the response format type is not supported
    """
    if is_basemodel_type(response_format):
        return cast(ResponseFormatT, model_parse_json(response_format, content))

    if is_dataclass_like_type(response_format):
        if PYDANTIC_V1:
            raise TypeError(f"Non BaseModel types are only supported with Pydantic v2 - {response_format}")

        # FIXED: Use cached TypeAdapter instead of creating new instances
        # This prevents unbounded memory growth in multi-threaded scenarios
        adapter = _get_cached_type_adapter(response_format)
        return adapter.validate_json(content)

    raise TypeError(f"Unable to automatically parse response format type {response_format}")


def type_to_response_format_param(
    response_format: type | completion_create_params.ResponseFormat | Omit,
) -> ResponseFormatParam | Omit:
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
        # FIXED: Use cached TypeAdapter here as well
        json_schema_type = _get_cached_type_adapter(response_format)
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
