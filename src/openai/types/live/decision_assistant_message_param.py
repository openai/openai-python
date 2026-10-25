# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = ["DecisionAssistantMessageParam", "ContentPart", "ContentPartOutputText", "ContentPartRefusal"]


class ContentPartOutputText(TypedDict, total=False):
    text: Required[str]
    """The text content."""

    type: Required[Literal["output_text"]]


class ContentPartRefusal(TypedDict, total=False):
    refusal: Required[str]
    """The refusal text."""

    type: Required[Literal["refusal"]]


ContentPart: TypeAlias = Union[ContentPartOutputText, ContentPartRefusal]


class DecisionAssistantMessageParam(TypedDict, total=False):
    content: Required[Union[str, Iterable[ContentPart]]]
    """The text input to the model."""

    role: Required[Literal["assistant"]]

    id: Optional[str]
    """The unique ID of this message item."""

    phase: Optional[Literal["commentary", "final_answer"]]
    """
    Labels an `assistant` message as intermediate commentary (`commentary`) or the
    final answer (`final_answer`). For models like `gpt-5.3-codex` and beyond, when
    sending follow-up requests, preserve and resend phase on all assistant messages
    — dropping it can degrade performance. Not used for user messages.
    """

    type: Literal["message"]
