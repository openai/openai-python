# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["RealtimeConversationItemAssistantMessageParam", "Content"]


class Content(TypedDict, total=False):
    text: str
    """The text content."""

    type: Literal["text"]
    """The content type. Always `text` for assistant messages."""


class RealtimeConversationItemAssistantMessageParam(TypedDict, total=False):
    content: Required[Iterable[Content]]
    """The content of the message."""

    role: Required[Literal["assistant"]]
    """The role of the message sender. Always `assistant`."""

    type: Required[Literal["message"]]
    """The type of the item. Always `message`."""

    id: str
    """The unique ID of the item."""

    object: Literal["realtime.item"]
    """Identifier for the API object being returned - always `realtime.item`."""

    status: Literal["completed", "incomplete", "in_progress"]
    """The status of the item. Has no effect on the conversation."""
