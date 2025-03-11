# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .response_output_message import ResponseOutputMessage
from .response_computer_tool_call import ResponseComputerToolCall
from .response_function_tool_call import ResponseFunctionToolCall
from .response_function_web_search import ResponseFunctionWebSearch
from .response_file_search_tool_call import ResponseFileSearchToolCall

__all__ = ["ResponseOutputItem", "Reasoning", "ReasoningContent"]


class ReasoningContent(BaseModel):
    text: str
    """
    A short summary of the reasoning used by the model when generating the response.
    """

    type: Literal["reasoning_summary"]
    """The type of the object. Always `text`."""


class Reasoning(BaseModel):
    id: str
    """The unique identifier of the reasoning content."""

    content: List[ReasoningContent]
    """Reasoning text contents."""

    type: Literal["reasoning"]
    """The type of the object. Always `reasoning`."""

    status: Optional[Literal["in_progress", "completed", "incomplete"]] = None
    """The status of the item.

    One of `in_progress`, `completed`, or `incomplete`. Populated when items are
    returned via API.
    """


ResponseOutputItem: TypeAlias = Annotated[
    Union[
        ResponseOutputMessage,
        ResponseFileSearchToolCall,
        ResponseFunctionToolCall,
        ResponseFunctionWebSearch,
        ResponseComputerToolCall,
        Reasoning,
    ],
    PropertyInfo(discriminator="type"),
]
