# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated, TypeAlias

from ..._utils import PropertyInfo
from .chat_completion_message_custom_tool_call import ChatCompletionMessageCustomToolCall
from .chat_completion_message_function_tool_call import ChatCompletionMessageFunctionToolCall

__all__ = ["ChatCompletionMessageToolCall"]

ChatCompletionMessageToolCall: TypeAlias = Annotated[
    Union[ChatCompletionMessageFunctionToolCall, ChatCompletionMessageCustomToolCall],
    PropertyInfo(discriminator="type"),
]
