# File generated from our OpenAPI spec by Stainless.

from typing import Union
from typing_extensions import Annotated

from ....._utils import PropertyInfo
from .function_tool_call import FunctionToolCall
from .retrieval_tool_call import RetrievalToolCall
from .code_interpreter_tool_call import CodeInterpreterToolCall

__all__ = ["ToolCall"]

ToolCall = Annotated[
    Union[CodeInterpreterToolCall, RetrievalToolCall, FunctionToolCall], PropertyInfo(discriminator="type")
]
