# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel
from .decision_question import (
    Score as QuestionQuestionParamScore,
    Choice as QuestionQuestionParamChoice,
    Predicate as QuestionQuestionParamPredicate,
    ScoreLevel as QuestionQuestionParamScoreLevel,
    DecisionQuestion,
    DecisionQuestion as Question,
)
from .decision_choice_option import DecisionChoiceOption as QuestionQuestionParamChoiceChoice

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
