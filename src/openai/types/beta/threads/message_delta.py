# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ...._models import BaseModel
from .message_content_delta import MessageContentDelta

__all__ = ["MessageDelta"]


class MessageDelta(BaseModel):
    content: Optional[List[MessageContentDelta]] = None
    """The content of the message in array of text and/or images."""

    file_ids: Optional[List[str]] = None
    """
    A list of [file](https://platform.openai.com/docs/api-reference/files) IDs that
    the assistant should use. Useful for tools like retrieval and code_interpreter
    that can access files. A maximum of 10 files can be attached to a message.
    """

    role: Optional[Literal["user", "assistant"]] = None
    """The entity that produced the message. One of `user` or `assistant`."""
