# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from ..shared_params.decision_question_input_part import DecisionQuestionInputPart

__all__ = [
    "DecisionTriggerParam",
    "Decisions",
    "DecisionsQuestion",
    "DecisionsQuestionQuestionParamPredicate",
    "DecisionsQuestionQuestionParamChoice",
    "DecisionsQuestionQuestionParamChoiceChoice",
    "DecisionsQuestionQuestionParamScore",
    "DecisionsQuestionQuestionParamScoreLevel",
]


class DecisionsQuestionQuestionParamPredicate(TypedDict, total=False):
    """Estimate how likely it is that a statement about the input is true."""

    instructions: Required[Union[str, Iterable[DecisionQuestionInputPart]]]

    type: Required[Literal["predicate"]]
    """The type of the object. Always `predicate`."""

    name: str


class DecisionsQuestionQuestionParamChoiceChoice(TypedDict, total=False):
    value: Required[Union[str, bool]]
    """
    Choice values are typed: a string and a boolean with the same text are distinct.
    """

    description: str


class DecisionsQuestionQuestionParamChoice(TypedDict, total=False):
    """Choose from the supplied options based on the input."""

    choices: Required[Iterable[DecisionsQuestionQuestionParamChoiceChoice]]
    """Provide between 2 and 255 choices. Each choice must be unique."""

    instructions: Required[Union[str, Iterable[DecisionQuestionInputPart]]]

    type: Required[Literal["choice"]]
    """The type of the object. Always `choice`."""

    name: str


class DecisionsQuestionQuestionParamScoreLevel(TypedDict, total=False):
    label: Required[str]

    description: str


class DecisionsQuestionQuestionParamScore(TypedDict, total=False):
    """Rate the input against the supplied ordered levels."""

    instructions: Required[Union[str, Iterable[DecisionQuestionInputPart]]]

    levels: Required[Iterable[DecisionsQuestionQuestionParamScoreLevel]]

    type: Required[Literal["score"]]
    """The type of the object. Always `score`."""

    name: str


DecisionsQuestion: TypeAlias = Union[
    DecisionsQuestionQuestionParamPredicate, DecisionsQuestionQuestionParamChoice, DecisionsQuestionQuestionParamScore
]


class Decisions(TypedDict, total=False):
    """
    Questions evaluated using the current transcript and the session's shared Decision items.
    """

    questions: Required[Iterable[DecisionsQuestion]]
    """Native Decision API questions evaluated together, in order."""


class DecisionTriggerParam(TypedDict, total=False):
    decisions: Required[Decisions]
    """
    Questions evaluated using the current transcript and the session's shared
    Decision items.
    """

    event_type: Required[Literal["session.input_transcript.delta", "session.output_transcript.delta"]]

    type: Required[Literal["decisions"]]
