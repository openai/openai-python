# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel

__all__ = [
    "InitialItem",
    "Developer",
    "DeveloperContent",
    "User",
    "UserContent",
    "Assistant",
    "AssistantContent",
    "AssistantContentText",
    "AssistantContentOutputText",
]


class DeveloperContent(BaseModel):
    """Text supplied in a developer or user message when starting a Live session."""

    text: str
    """The message text to include in the Live session’s initial conversation history."""

    type: Optional[Literal["input_text"]] = None
    """The text content type. Always `input_text`."""


class Developer(BaseModel):
    """A developer message included in the initial text history of a Live session."""

    content: List[DeveloperContent]
    """The message content.

    Supply exactly one text part for the initial Live conversation history.
    """

    role: Literal["developer"]
    """The author of this history message. Always `developer`."""

    id: Optional[str] = None
    """An optional identifier for the supplied history message.

    Live uses the message’s role and text to initialize the conversation.
    """

    status: Optional[Literal["incomplete", "completed"]] = None
    """The supplied message’s status.

    Live uses its text as history and does not resume an incomplete message.
    """

    type: Optional[Literal["message"]] = None
    """The history item type. Always `message`."""


class UserContent(BaseModel):
    """Text supplied in a developer or user message when starting a Live session."""

    text: str
    """The message text to include in the Live session’s initial conversation history."""

    type: Optional[Literal["input_text"]] = None
    """The text content type. Always `input_text`."""


class User(BaseModel):
    """A user message included in the initial text history of a Live session."""

    content: List[UserContent]
    """The message content.

    Supply exactly one text part for the initial Live conversation history.
    """

    role: Literal["user"]
    """The author of this history message. Always `user`."""

    id: Optional[str] = None
    """An optional identifier for the supplied history message.

    Live uses the message’s role and text to initialize the conversation.
    """

    status: Optional[Literal["incomplete", "completed"]] = None
    """The supplied message’s status.

    Live uses its text as history and does not resume an incomplete message.
    """

    type: Optional[Literal["message"]] = None
    """The history item type. Always `message`."""


class AssistantContentText(BaseModel):
    """Assistant text supplied as conversation history when starting a Live session."""

    text: str
    """The message text to include in the Live session’s initial conversation history."""

    type: Optional[Literal["text"]] = None
    """The text content type. Always `text`."""


class AssistantContentOutputText(BaseModel):
    """
    Assistant output text supplied as conversation history when starting a Live session.
    """

    text: str
    """The message text to include in the Live session’s initial conversation history."""

    type: Literal["output_text"]
    """The text content type. Always `output_text`."""


AssistantContent: TypeAlias = Annotated[
    Union[AssistantContentText, AssistantContentOutputText], PropertyInfo(discriminator="type")
]


class Assistant(BaseModel):
    """An assistant message included in the initial text history of a Live session."""

    content: List[AssistantContent]
    """The message content.

    Supply exactly one text part for the initial Live conversation history.
    """

    role: Literal["assistant"]
    """The author of this history message. Always `assistant`."""

    id: Optional[str] = None
    """An optional identifier for the supplied history message.

    Live uses the message’s role and text to initialize the conversation.
    """

    status: Optional[Literal["incomplete", "completed"]] = None
    """The supplied message’s status.

    Live uses its text as history and does not resume an incomplete message.
    """

    type: Optional[Literal["message"]] = None
    """The history item type. Always `message`."""


InitialItem: TypeAlias = Annotated[Union[Developer, User, Assistant], PropertyInfo(discriminator="role")]
