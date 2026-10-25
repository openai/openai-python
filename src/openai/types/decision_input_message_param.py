# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .decision_input_text_param import DecisionInputTextParam
from .decision_input_part_union_param import DecisionInputPartUnionParam

__all__ = [
    "DecisionInputMessageParam",
    "DecisionInputMessageUnionParam",
    "DecisionInputUserMessage",
    "DecisionInputDeveloperMessage",
    "DecisionInputSystemMessage",
    "DecisionInputAssistantMessage",
    "DecisionInputAssistantMessageContentParts",
    "DecisionInputAssistantMessageContentPartsDecisionInputOutputText",
    "DecisionInputAssistantMessageContentPartsDecisionInputRefusal",
]


class DecisionInputUserMessage(TypedDict, total=False):
    """A user message containing input text, images, or JSON."""

    content: Required[Union[str, Iterable[DecisionInputPartUnionParam]]]
    """A text string or an ordered list of text, image, and JSON parts."""

    role: Required[Literal["user"]]

    type: Literal["message"]


class DecisionInputMessageParam(DecisionInputUserMessage, total=False):
    """A user message containing input text, images, or JSON."""


class DecisionInputDeveloperMessage(TypedDict, total=False):
    """A developer message containing input text."""

    content: Required[Union[str, Iterable[DecisionInputTextParam]]]
    """A text string or an ordered list of input text parts."""

    role: Required[Literal["developer"]]

    type: Literal["message"]


class DecisionInputSystemMessage(TypedDict, total=False):
    """A system message containing input text."""

    content: Required[Union[str, Iterable[DecisionInputTextParam]]]
    """A text string or an ordered list of input text parts."""

    role: Required[Literal["system"]]

    type: Literal["message"]


class DecisionInputAssistantMessageContentPartsDecisionInputOutputText(TypedDict, total=False):
    text: Required[str]

    type: Required[Literal["output_text"]]


class DecisionInputAssistantMessageContentPartsDecisionInputRefusal(TypedDict, total=False):
    refusal: Required[str]

    type: Required[Literal["refusal"]]


DecisionInputAssistantMessageContentParts: TypeAlias = Union[
    DecisionInputAssistantMessageContentPartsDecisionInputOutputText,
    DecisionInputAssistantMessageContentPartsDecisionInputRefusal,
]


class DecisionInputAssistantMessage(TypedDict, total=False):
    """An assistant message containing output text or refusals."""

    content: Required[Union[str, Iterable[DecisionInputAssistantMessageContentParts]]]
    """A text string or an ordered list of output text and refusal parts."""

    role: Required[Literal["assistant"]]

    phase: Optional[Literal["commentary", "final_answer"]]
    """The phase of an assistant message."""

    type: Literal["message"]


DecisionInputMessageUnionParam: TypeAlias = Union[
    DecisionInputUserMessage, DecisionInputDeveloperMessage, DecisionInputSystemMessage, DecisionInputAssistantMessage
]
