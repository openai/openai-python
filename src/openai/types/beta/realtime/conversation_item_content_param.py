# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["ConversationItemContentParam"]


class ConversationItemContentParam(TypedDict, total=False):
    id: str
    """
    ID of a previous conversation item (like a model response), used for
    `item_reference` content types.
    """

    audio: str
    """Base64-encoded audio bytes, used for `input_audio` content type."""

    text: str
    """The text content, used for `input_text` and `text` content types."""

    transcript: str
    """The transcript of the audio, used for `input_audio` content type."""

    type: Literal["input_text", "input_audio", "item_reference", "text"]
    """The content type (`input_text`, `input_audio`, `item_reference`, `text`)."""
