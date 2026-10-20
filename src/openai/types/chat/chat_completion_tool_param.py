from __future__ import annotations

from typing_extensions import TypeAlias

from .chat_completion_function_tool_param import (
    FunctionDefinition as FunctionDefinition,
    ChatCompletionFunctionToolParam,
)

__all__ = ["ChatCompletionToolParam", "FunctionDefinition"]

ChatCompletionToolParam: TypeAlias = ChatCompletionFunctionToolParam
