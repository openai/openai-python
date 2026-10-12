# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated, TypeAlias

from ..._utils import PropertyInfo
from .chat_completion_message_custom_tool_call import ChatCompletionMessageCustomToolCall
from .chat_completion_message_function_tool_call import (
    Function as Function,
    ChatCompletionMessageFunctionToolCall,
    ChatCompletionMessageFunctionToolCall as _compat_ChatCompletionMessageToolCall,
)

__all__ = ["ChatCompletionMessageToolCallUnion", "Function"]

ChatCompletionMessageToolCallUnion: TypeAlias = Annotated[
    Union[ChatCompletionMessageFunctionToolCall, ChatCompletionMessageCustomToolCall],
    PropertyInfo(discriminator="type"),
]

ChatCompletionMessageToolCall: TypeAlias = _compat_ChatCompletionMessageToolCall
