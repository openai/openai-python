# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

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
    "DecisionsDelegationConfigParam",
    "Question",
    "QuestionQuestionParamChoice",
    "QuestionQuestionParamPredicate",
    "QuestionQuestionParamScore",
    "QuestionQuestionParamScoreLevel",
    "QuestionQuestionParamChoiceChoice",
]


class DecisionsDelegationConfigParam(TypedDict, total=False):
    model: Required[str]

    questions: Required[Iterable[DecisionQuestionParam]]
    """Native Decision API questions evaluated together, in order."""
