# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["RealtimeConversationItemFunctionCallOutput"]


class RealtimeConversationItemFunctionCallOutput(BaseModel):
    call_id: str
    """The ID of the function call this output is for."""

    output: str
    """The output of the function call."""

    type: Literal["function_call_output"]
    """The type of the item. Always `function_call_output`."""

    id: Optional[str] = None
    """The unique ID of the item."""

    object: Optional[Literal["realtime.item"]] = None
    """Identifier for the API object being returned - always `realtime.item`."""

    status: Optional[Literal["completed", "incomplete", "in_progress"]] = None
    """The status of the item. Has no effect on the conversation."""
