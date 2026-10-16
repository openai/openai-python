# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = [
    "DecisionsDelegationConfigParam",
    "Question",
    "QuestionQuestionParamPredicate",
    "QuestionQuestionParamChoice",
    "QuestionQuestionParamChoiceChoice",
    "QuestionQuestionParamScore",
    "QuestionQuestionParamScoreLevel",
]


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
    """Provide between 2 and 255 choices. Each choice must be unique."""

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


class DecisionsDelegationConfigParam(TypedDict, total=False):
    model: Required[str]

    questions: Required[Iterable[Question]]
    """Native Decision API questions evaluated together, in order."""
