# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ...._utils import PropertyInfo
from ...._models import BaseModel
from .chatkit_attachment import ChatKitAttachment

__all__ = [
    "ChatKitThreadUserMessageItem",
    "Content",
    "ContentInputText",
    "ContentQuotedText",
    "InferenceOptions",
    "InferenceOptionsToolChoice",
]


class ContentInputText(BaseModel):
    text: str
    """Plain-text content supplied by the user."""

    type: Literal["input_text"]
    """Type discriminator that is always `input_text`."""


class ContentQuotedText(BaseModel):
    text: str
    """Quoted text content."""

    type: Literal["quoted_text"]
    """Type discriminator that is always `quoted_text`."""


Content: TypeAlias = Annotated[Union[ContentInputText, ContentQuotedText], PropertyInfo(discriminator="type")]


class InferenceOptionsToolChoice(BaseModel):
    id: str
    """Identifier of the requested tool."""


class InferenceOptions(BaseModel):
    model: Optional[str] = None
    """Model name that generated the response.

    Defaults to null when using the session default.
    """

    tool_choice: Optional[InferenceOptionsToolChoice] = None
    """Preferred tool to invoke. Defaults to null when ChatKit should auto-select."""


class ChatKitThreadUserMessageItem(BaseModel):
    id: str
    """Identifier of the thread item."""

    attachments: List[ChatKitAttachment]
    """Attachments associated with the user message. Defaults to an empty list."""

    content: List[Content]
    """Ordered content elements supplied by the user."""

    created_at: int
    """Unix timestamp (in seconds) for when the item was created."""

    inference_options: Optional[InferenceOptions] = None
    """Inference overrides applied to the message. Defaults to null when unset."""

    object: Literal["chatkit.thread_item"]
    """Type discriminator that is always `chatkit.thread_item`."""

    thread_id: str
    """Identifier of the parent thread."""

    type: Literal["chatkit.user_message"]
