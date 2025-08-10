# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, Union, overload
from typing_extensions import Literal, TypeAlias

from .chat_completion_message_custom_tool_call_param import ChatCompletionMessageCustomToolCallParam, Custom
from .chat_completion_message_function_tool_call_param import ChatCompletionMessageFunctionToolCallParam, Function

__all__ = ["ChatCompletionMessageToolCallParam", "ChatCompletionMessageToolCallParamType"]


class _ChatCompletionMessageToolCallParamConstructor:
    """
    Constructor class that provides backward compatibility for ChatCompletionMessageToolCallParam.
    This allows instantiation while maintaining the Union type behavior.
    """
    
    @overload
    def __call__(
        self,
        *,
        id: str,
        type: Literal["function"],
        function: Function,
        **kwargs: Any,
    ) -> ChatCompletionMessageFunctionToolCallParam: ...
    
    @overload  
    def __call__(
        self,
        *,
        id: str,
        type: Literal["custom"],
        custom: Custom,
        **kwargs: Any,
    ) -> ChatCompletionMessageCustomToolCallParam: ...
    
    def __call__(self, **kwargs: Any) -> Union[ChatCompletionMessageFunctionToolCallParam, ChatCompletionMessageCustomToolCallParam]:
        from typing import cast
        
        tool_type = kwargs.get("type")
        
        if tool_type == "function":
            return cast(ChatCompletionMessageFunctionToolCallParam, kwargs)
        elif tool_type == "custom":
            return cast(ChatCompletionMessageCustomToolCallParam, kwargs)
        else:
            # Default to function for backward compatibility (pre-1.99.2 behavior)
            if "function" in kwargs and "type" not in kwargs:
                kwargs["type"] = "function"
                return cast(ChatCompletionMessageFunctionToolCallParam, kwargs)
            
            raise ValueError(f"Invalid tool call type: {tool_type}. Expected 'function' or 'custom'.")


# Create an instance that can be called like a constructor
ChatCompletionMessageToolCallParam = _ChatCompletionMessageToolCallParamConstructor()

# Also create the type alias for static type checking
ChatCompletionMessageToolCallParamType: TypeAlias = Union[
    ChatCompletionMessageFunctionToolCallParam, ChatCompletionMessageCustomToolCallParam
]
