# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["RealtimeConversationItemUserMessageParam", "Content"]


class Content(TypedDict, total=False):
    audio: str
    """Base64-encoded audio bytes (for `input_audio`)."""

    text: str
    """The text content (for `input_text`)."""

    transcript: str
    """Transcript of the audio (for `input_audio`)."""

    type: Literal["input_text", "input_audio"]
    """The content type (`input_text` or `input_audio`)."""


class RealtimeConversationItemUserMessageParam(TypedDict, total=False):
    content: Required[Iterable[Content]]
    """The content of the message."""

    role: Required[Literal["user"]]
    """The role of the message sender. Always `user`."""

    type: Required[Literal["message"]]
    """The type of the item. Always `message`."""

    id: str
    """The unique ID of the item."""

    object: Literal["realtime.item"]
    """Identifier for the API object being returned - always `realtime.item`."""

    status: Literal["completed", "incomplete", "in_progress"]
    """The status of the item. Has no effect on the conversation."""
