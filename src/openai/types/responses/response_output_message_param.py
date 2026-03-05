# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .response_output_text_param import ResponseOutputTextParam
from .response_output_refusal_param import ResponseOutputRefusalParam

__all__ = ["ResponseOutputMessageParam", "Content"]

Content: TypeAlias = Union[ResponseOutputTextParam, ResponseOutputRefusalParam]


class ResponseOutputMessageParam(TypedDict, total=False):
    """An output message from the model."""

    id: Required[str]
    """The unique ID of the output message."""

    content: Required[Iterable[Content]]
    """The content of the output message."""

    role: Required[Literal["assistant"]]
    """The role of the output message. Always `assistant`."""

    status: Required[Literal["in_progress", "completed", "incomplete"]]
    """The status of the message input.

    One of `in_progress`, `completed`, or `incomplete`. Populated when input items
    are returned via API.
    """

    type: Required[Literal["message"]]
    """The type of the output message. Always `message`."""

    phase: Optional[Literal["commentary", "final_answer"]]
    """
    Labels an `assistant` message as intermediate commentary (`commentary`) or the
    final answer (`final_answer`). For models like `gpt-5.3-codex` and beyond, when
    sending follow-up requests, preserve and resend phase on all assistant messages
    — dropping it can degrade performance. Not used for user messages.
    """
