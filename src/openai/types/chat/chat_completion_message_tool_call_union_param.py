# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import TypeAlias

from .chat_completion_message_custom_tool_call_param import ChatCompletionMessageCustomToolCallParam
from .chat_completion_message_function_tool_call_param import ChatCompletionMessageFunctionToolCallParam

__all__ = ["ChatCompletionMessageToolCallUnionParam"]

ChatCompletionMessageToolCallUnionParam: TypeAlias = Union[
    ChatCompletionMessageFunctionToolCallParam, ChatCompletionMessageCustomToolCallParam
]
