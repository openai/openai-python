# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["ConversationItemContent"]


class ConversationItemContent(BaseModel):
    id: Optional[str] = None
    """
    ID of a previous conversation item (like a model response), used for
    `item_reference` content types.
    """

    audio: Optional[str] = None
    """Base64-encoded audio bytes, used for `input_audio` content type."""

    text: Optional[str] = None
    """The text content, used for `input_text` and `text` content types."""

    transcript: Optional[str] = None
    """The transcript of the audio, used for `input_audio` content type."""

    type: Optional[Literal["input_text", "input_audio", "item_reference", "text"]] = None
    """The content type (`input_text`, `input_audio`, `item_reference`, `text`)."""
