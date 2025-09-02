# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["RealtimeConversationItemFunctionCall"]


class RealtimeConversationItemFunctionCall(BaseModel):
    arguments: str
    """The arguments of the function call."""

    name: str
    """The name of the function being called."""

    type: Literal["function_call"]
    """The type of the item. Always `function_call`."""

    id: Optional[str] = None
    """The unique ID of the item."""

    call_id: Optional[str] = None
    """The ID of the function call."""

    object: Optional[Literal["realtime.item"]] = None
    """Identifier for the API object being returned - always `realtime.item`."""

    status: Optional[Literal["completed", "incomplete", "in_progress"]] = None
    """The status of the item. Has no effect on the conversation."""
