# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import TypeAlias, TypedDict

from .decision_question_param import (
    Score as _compat_QuestionQuestionParamScore,
    Choice as _compat_QuestionQuestionParamChoice,
    Predicate as _compat_QuestionQuestionParamPredicate,
    ScoreLevel as _compat_QuestionQuestionParamScoreLevel,
    DecisionQuestionParam,
    DecisionQuestionParam as _compat_Question,
)
from .decision_choice_option_param import DecisionChoiceOptionParam as _compat_QuestionQuestionParamChoiceChoice

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


Question: TypeAlias = _compat_Question

QuestionQuestionParamChoice: TypeAlias = _compat_QuestionQuestionParamChoice

QuestionQuestionParamPredicate: TypeAlias = _compat_QuestionQuestionParamPredicate

QuestionQuestionParamScore: TypeAlias = _compat_QuestionQuestionParamScore

QuestionQuestionParamScoreLevel: TypeAlias = _compat_QuestionQuestionParamScoreLevel

QuestionQuestionParamChoiceChoice: TypeAlias = _compat_QuestionQuestionParamChoiceChoice
