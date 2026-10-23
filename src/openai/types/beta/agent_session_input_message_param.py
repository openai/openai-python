# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

from .input_content_param import InputContentParam

__all__ = ["AgentSessionInputMessageParam"]


class AgentSessionInputMessageParam(TypedDict, total=False):
    """A user message submitted to a session."""

    content: Required[Iterable[InputContentParam]]
    """The content of the message."""

    role: Required[Literal["user"]]
    """The role of the message author. Always `user`."""

    type: Literal["message"]
    """The type of the input item. Always `message`."""
