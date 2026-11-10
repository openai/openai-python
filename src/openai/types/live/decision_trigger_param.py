# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

from .decision_question_param import (
    Score as DecisionsQuestionQuestionParamScore,
    Choice as DecisionsQuestionQuestionParamChoice,
    Predicate as DecisionsQuestionQuestionParamPredicate,
    ScoreLevel as DecisionsQuestionQuestionParamScoreLevel,
    DecisionQuestionParam,
    DecisionQuestionParam as DecisionsQuestion,
)
from .decision_choice_option_param import DecisionChoiceOptionParam as DecisionsQuestionQuestionParamChoiceChoice

__all__ = [
    "DecisionTriggerParam",
    "Decisions",
    "DecisionsQuestion",
    "DecisionsQuestionQuestionParamChoice",
    "DecisionsQuestionQuestionParamPredicate",
    "DecisionsQuestionQuestionParamScore",
    "DecisionsQuestionQuestionParamScoreLevel",
    "DecisionsQuestionQuestionParamChoiceChoice",
]


class Decisions(TypedDict, total=False):
    """
    Questions evaluated using the current transcript and the session's shared Decision items.
    """

    questions: Required[Iterable[DecisionQuestionParam]]
    """Native Decision API questions evaluated together, in order."""


class DecisionTriggerParam(TypedDict, total=False):
    decisions: Required[Decisions]
    """
    Questions evaluated using the current transcript and the session's shared
    Decision items.
    """

    event_type: Required[Literal["session.input_transcript.delta", "session.output_transcript.delta"]]

    type: Required[Literal["decisions"]]
