# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = [
    "InitialItemParam",
    "Developer",
    "DeveloperContent",
    "User",
    "UserContent",
    "Assistant",
    "AssistantContent",
    "AssistantContentText",
    "AssistantContentOutputText",
]


class DeveloperContent(TypedDict, total=False):
    """Text supplied in a developer or user message when starting a Live session."""

    text: Required[str]
    """The message text to include in the Live session’s initial conversation history."""

    type: Literal["input_text"]
    """The text content type. Always `input_text`."""


class Developer(TypedDict, total=False):
    """A developer message included in the initial text history of a Live session."""

    content: Required[Iterable[DeveloperContent]]
    """The message content.

    Supply exactly one text part for the initial Live conversation history.
    """

    role: Required[Literal["developer"]]
    """The author of this history message. Always `developer`."""

    id: Optional[str]
    """An optional identifier for the supplied history message.

    Live uses the message’s role and text to initialize the conversation.
    """

    status: Optional[Literal["incomplete", "completed"]]
    """The supplied message’s status.

    Live uses its text as history and does not resume an incomplete message.
    """

    type: Literal["message"]
    """The history item type. Always `message`."""


class UserContent(TypedDict, total=False):
    """Text supplied in a developer or user message when starting a Live session."""

    text: Required[str]
    """The message text to include in the Live session’s initial conversation history."""

    type: Literal["input_text"]
    """The text content type. Always `input_text`."""


class User(TypedDict, total=False):
    """A user message included in the initial text history of a Live session."""

    content: Required[Iterable[UserContent]]
    """The message content.

    Supply exactly one text part for the initial Live conversation history.
    """

    role: Required[Literal["user"]]
    """The author of this history message. Always `user`."""

    id: Optional[str]
    """An optional identifier for the supplied history message.

    Live uses the message’s role and text to initialize the conversation.
    """

    status: Optional[Literal["incomplete", "completed"]]
    """The supplied message’s status.

    Live uses its text as history and does not resume an incomplete message.
    """

    type: Literal["message"]
    """The history item type. Always `message`."""


class AssistantContentText(TypedDict, total=False):
    """Assistant text supplied as conversation history when starting a Live session."""

    text: Required[str]
    """The message text to include in the Live session’s initial conversation history."""

    type: Literal["text"]
    """The text content type. Always `text`."""


class AssistantContentOutputText(TypedDict, total=False):
    """
    Assistant output text supplied as conversation history when starting a Live session.
    """

    text: Required[str]
    """The message text to include in the Live session’s initial conversation history."""

    type: Required[Literal["output_text"]]
    """The text content type. Always `output_text`."""


AssistantContent: TypeAlias = Union[AssistantContentText, AssistantContentOutputText]


class Assistant(TypedDict, total=False):
    """An assistant message included in the initial text history of a Live session."""

    content: Required[Iterable[AssistantContent]]
    """The message content.

    Supply exactly one text part for the initial Live conversation history.
    """

    role: Required[Literal["assistant"]]
    """The author of this history message. Always `assistant`."""

    id: Optional[str]
    """An optional identifier for the supplied history message.

    Live uses the message’s role and text to initialize the conversation.
    """

    status: Optional[Literal["incomplete", "completed"]]
    """The supplied message’s status.

    Live uses its text as history and does not resume an incomplete message.
    """

    type: Literal["message"]
    """The history item type. Always `message`."""


InitialItemParam: TypeAlias = Union[Developer, User, Assistant]
