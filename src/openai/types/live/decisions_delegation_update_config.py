# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Optional

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
    "DecisionsDelegationUpdateConfig",
    "Question",
    "QuestionQuestionParamChoice",
    "QuestionQuestionParamPredicate",
    "QuestionQuestionParamScore",
    "QuestionQuestionParamScoreLevel",
    "QuestionQuestionParamChoiceChoice",
]


class DecisionsDelegationUpdateConfig(BaseModel):
    model: Optional[str] = None

    questions: Optional[List[DecisionQuestion]] = None
    """Native Decision API questions evaluated together, in order."""
