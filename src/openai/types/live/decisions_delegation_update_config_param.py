# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import TypedDict

from .decision_question_param import (
    Score as QuestionQuestionParamScore,
    Choice as QuestionQuestionParamChoice,
    Predicate as QuestionQuestionParamPredicate,
    ScoreLevel as QuestionQuestionParamScoreLevel,
    DecisionQuestionParam,
    DecisionQuestionParam as Question,
)
from .decision_choice_option_param import DecisionChoiceOptionParam as QuestionQuestionParamChoiceChoice

__all__ = [
    "DecisionsDelegationUpdateConfigParam",
    "Question",
    "QuestionQuestionParamChoice",
    "QuestionQuestionParamPredicate",
    "QuestionQuestionParamScore",
    "QuestionQuestionParamScoreLevel",
    "QuestionQuestionParamChoiceChoice",
]


class DecisionsDelegationUpdateConfigParam(TypedDict, total=False):
    model: str

    questions: Iterable[DecisionQuestionParam]
    """Native Decision API questions evaluated together, in order."""
