# File generated from our OpenAPI spec by Stainless.

from typing import List, Union
from typing_extensions import Literal, Annotated

from ....._utils import PropertyInfo
from ....._models import BaseModel
from .code_tool_call import CodeToolCall
from .function_tool_call import FunctionToolCall
from .retrieval_tool_call import RetrievalToolCall

__all__ = ["ToolCallsStepDetails", "ToolCall"]

ToolCall = Annotated[Union[CodeToolCall, RetrievalToolCall, FunctionToolCall], PropertyInfo(discriminator="type")]


class ToolCallsStepDetails(BaseModel):
    tool_calls: List[ToolCall]
    """An array of tool calls the run step was involved in.

    These can be associated with one of three types of tools: `code_interpreter`,
    `retrieval`, or `function`.
    """

    type: Literal["tool_calls"]
    """Always `tool_calls`."""
