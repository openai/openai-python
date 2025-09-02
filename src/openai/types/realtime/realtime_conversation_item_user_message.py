# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["RealtimeConversationItemUserMessage", "Content"]


class Content(BaseModel):
    audio: Optional[str] = None
    """Base64-encoded audio bytes (for `input_audio`)."""

    text: Optional[str] = None
    """The text content (for `input_text`)."""

    transcript: Optional[str] = None
    """Transcript of the audio (for `input_audio`)."""

    type: Optional[Literal["input_text", "input_audio"]] = None
    """The content type (`input_text` or `input_audio`)."""


class RealtimeConversationItemUserMessage(BaseModel):
    content: List[Content]
    """The content of the message."""

    role: Literal["user"]
    """The role of the message sender. Always `user`."""

    type: Literal["message"]
    """The type of the item. Always `message`."""

    id: Optional[str] = None
    """The unique ID of the item."""

    object: Optional[Literal["realtime.item"]] = None
    """Identifier for the API object being returned - always `realtime.item`."""

    status: Optional[Literal["completed", "incomplete", "in_progress"]] = None
    """The status of the item. Has no effect on the conversation."""
