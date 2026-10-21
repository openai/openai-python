# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .response_custom_tool_call import ResponseCustomToolCall

__all__ = ["ResponseCustomToolCallItem"]


class ResponseCustomToolCallItem(ResponseCustomToolCall):
    """A call to a custom tool created by the model."""

    id: str  # type: ignore
    """The unique ID of the custom tool call item."""

    status: Literal["in_progress", "completed", "incomplete"]
    """The status of the item.

    One of `in_progress`, `completed`, or `incomplete`. Populated when items are
    returned via API.
    """

    created_by: Optional[str] = None
    """The identifier of the actor that created the item."""
