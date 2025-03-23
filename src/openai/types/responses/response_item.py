# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated, TypeAlias

from ..._utils import PropertyInfo
from .response_output_message import ResponseOutputMessage
from .response_computer_tool_call import ResponseComputerToolCall
from .response_input_message_item import ResponseInputMessageItem
from .response_function_web_search import ResponseFunctionWebSearch
from .response_file_search_tool_call import ResponseFileSearchToolCall
from .response_function_tool_call_item import ResponseFunctionToolCallItem
from .response_computer_tool_call_output_item import ResponseComputerToolCallOutputItem
from .response_function_tool_call_output_item import ResponseFunctionToolCallOutputItem

__all__ = ["ResponseItem"]

ResponseItem: TypeAlias = Annotated[
    Union[
        ResponseInputMessageItem,
        ResponseOutputMessage,
        ResponseFileSearchToolCall,
        ResponseComputerToolCall,
        ResponseComputerToolCallOutputItem,
        ResponseFunctionWebSearch,
        ResponseFunctionToolCallItem,
        ResponseFunctionToolCallOutputItem,
    ],
    PropertyInfo(discriminator="type"),
]
