# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from ..._models import BaseModel
from .decision_question import (
    Score as _compat_QuestionQuestionParamScore,
    Choice as _compat_QuestionQuestionParamChoice,
    Predicate as _compat_QuestionQuestionParamPredicate,
    ScoreLevel as _compat_QuestionQuestionParamScoreLevel,
    DecisionQuestion,
    DecisionQuestion as _compat_Question,
)
from .decision_choice_option import DecisionChoiceOption as _compat_QuestionQuestionParamChoiceChoice

__all__ = [
    "DecisionsDelegationConfig",
    "Question",
    "QuestionQuestionParamChoice",
    "QuestionQuestionParamPredicate",
    "QuestionQuestionParamScore",
    "QuestionQuestionParamScoreLevel",
    "QuestionQuestionParamChoiceChoice",
]


class DecisionsDelegationConfig(BaseModel):
    model: str

    questions: List[DecisionQuestion]
    """Native Decision API questions evaluated together, in order."""


Question: TypeAlias = _compat_Question

QuestionQuestionParamChoice: TypeAlias = _compat_QuestionQuestionParamChoice

QuestionQuestionParamPredicate: TypeAlias = _compat_QuestionQuestionParamPredicate

QuestionQuestionParamScore: TypeAlias = _compat_QuestionQuestionParamScore

QuestionQuestionParamScoreLevel: TypeAlias = _compat_QuestionQuestionParamScoreLevel

QuestionQuestionParamChoiceChoice: TypeAlias = _compat_QuestionQuestionParamChoiceChoice
