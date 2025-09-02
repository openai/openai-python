# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["RealtimeConversationItemSystemMessage", "Content"]


class Content(BaseModel):
    text: Optional[str] = None
    """The text content."""

    type: Optional[Literal["input_text"]] = None
    """The content type. Always `input_text` for system messages."""


class RealtimeConversationItemSystemMessage(BaseModel):
    content: List[Content]
    """The content of the message."""

    role: Literal["system"]
    """The role of the message sender. Always `system`."""

    type: Literal["message"]
    """The type of the item. Always `message`."""

    id: Optional[str] = None
    """The unique ID of the item."""

    object: Optional[Literal["realtime.item"]] = None
    """Identifier for the API object being returned - always `realtime.item`."""

    status: Optional[Literal["completed", "incomplete", "in_progress"]] = None
    """The status of the item. Has no effect on the conversation."""
