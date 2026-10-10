# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .decision_input_message_param import DecisionInputMessageParam

__all__ = [
    "DecisionCreateParams",
    "Question",
    "QuestionQuestionParamPredicate",
    "QuestionQuestionParamChoice",
    "QuestionQuestionParamChoiceChoice",
    "QuestionQuestionParamScore",
    "QuestionQuestionParamScoreLevel",
]


class DecisionCreateParams(TypedDict, total=False):
    input: Required[Union[str, Iterable[DecisionInputMessageParam]]]
    """The text or images to evaluate for every question.

    Provide a text string or user messages containing text and inline images. Images
    must be inline data URLs; at most 128 images are allowed across all messages in
    one request. External URLs, files, audio, tools, and item references are not
    supported.
    """

    model: Required[str]

    questions: Required[Iterable[Question]]

    safety_identifier: Optional[str]
    """Opaque caller-provided end-user identifier, scoped by the verified org.

    Match Responses' limit; this is never the authenticated user identity.
    """


class QuestionQuestionParamPredicate(TypedDict, total=False):
    """Estimate how likely it is that a statement about the input is true."""

    instructions: Required[str]

    type: Required[Literal["predicate"]]
    """The type of the object. Always `predicate`."""

    name: str


class QuestionQuestionParamChoiceChoice(TypedDict, total=False):
    value: Required[Union[str, bool]]
    """
    Choice values are typed: a string and a boolean with the same text are distinct.
    """

    description: str


class QuestionQuestionParamChoice(TypedDict, total=False):
    """Choose from the supplied options based on the input."""

    choices: Required[Iterable[QuestionQuestionParamChoiceChoice]]

    instructions: Required[str]

    type: Required[Literal["choice"]]
    """The type of the object. Always `choice`."""

    name: str


class QuestionQuestionParamScoreLevel(TypedDict, total=False):
    label: Required[str]

    description: str


class QuestionQuestionParamScore(TypedDict, total=False):
    """Rate the input against the supplied ordered levels."""

    instructions: Required[str]

    levels: Required[Iterable[QuestionQuestionParamScoreLevel]]

    type: Required[Literal["score"]]
    """The type of the object. Always `score`."""

    name: str


Question: TypeAlias = Union[QuestionQuestionParamPredicate, QuestionQuestionParamChoice, QuestionQuestionParamScore]
