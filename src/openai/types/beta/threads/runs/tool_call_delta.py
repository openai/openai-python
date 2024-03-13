# File generated from our OpenAPI spec by Stainless.

from typing import Union
from typing_extensions import Annotated

from ....._utils import PropertyInfo
from .function_tool_call_delta import FunctionToolCallDelta
from .retrieval_tool_call_delta import RetrievalToolCallDelta
from .code_interpreter_tool_call_delta import CodeInterpreterToolCallDelta

__all__ = ["ToolCallDelta"]

ToolCallDelta = Annotated[
    Union[CodeInterpreterToolCallDelta, RetrievalToolCallDelta, FunctionToolCallDelta],
    PropertyInfo(discriminator="type"),
]
