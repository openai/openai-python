# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Any, Dict, Optional
from typing_extensions import Literal

from .response_custom_tool_call_output import ResponseCustomToolCallOutput

__all__ = ["ResponseCustomToolCallOutputItem"]


class ResponseCustomToolCallOutputItem(ResponseCustomToolCallOutput):
    """The output of a custom tool call from your code, being sent back to the model."""

    id: str  # type: ignore
    """The unique ID of the custom tool call output item."""

    status: Literal["in_progress", "completed", "incomplete"]
    """The status of the item.

    One of `in_progress`, `completed`, or `incomplete`. Populated when items are
    returned via API.
    """

    created_by: Optional[str] = None
    """The identifier of the actor that created the item."""

    def as_input(self) -> Dict[str, Any]:
        """Return a dict representation of this item suitable for use as input in a subsequent response.

        Strips output-only fields (``status``, ``created_by``) that the API does not accept as input.
        """
        data = self.to_dict()
        data.pop("status", None)
        data.pop("created_by", None)
        return data
