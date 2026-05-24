# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .response_function_tool_call import ResponseFunctionToolCall

__all__ = ["ResponseFunctionToolCallItem"]


class ResponseFunctionToolCallItem(ResponseFunctionToolCall):
    """A tool call to run a function.

    See the
    [function calling guide](https://platform.openai.com/docs/guides/function-calling) for more information.
    """

    id: str  # type: ignore
    """The unique ID of the function tool call."""

    status: Literal["in_progress", "completed", "incomplete"]  # type: ignore
    """The status of the item.

    One of `in_progress`, `completed`, or `incomplete`. Populated when items are
    returned via API.
    """

    created_by: Optional[str] = None
    """The identifier of the actor that created the item."""
