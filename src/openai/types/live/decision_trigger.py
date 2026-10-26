# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from ..._models import BaseModel
from .decision_question import (
    Score as DecisionsQuestionQuestionParamScore,
    Choice as DecisionsQuestionQuestionParamChoice,
    Predicate as DecisionsQuestionQuestionParamPredicate,
    ScoreLevel as DecisionsQuestionQuestionParamScoreLevel,
    DecisionQuestion,
    DecisionQuestion as DecisionsQuestion,
)
from .decision_choice_option import DecisionChoiceOption as DecisionsQuestionQuestionParamChoiceChoice

__all__ = [
    "DecisionTrigger",
    "Decisions",
    "DecisionsQuestion",
    "DecisionsQuestionQuestionParamChoice",
    "DecisionsQuestionQuestionParamPredicate",
    "DecisionsQuestionQuestionParamScore",
    "DecisionsQuestionQuestionParamScoreLevel",
    "DecisionsQuestionQuestionParamChoiceChoice",
]


class Decisions(BaseModel):
    """
    Questions evaluated using the current transcript and the session's shared Decision items.
    """

    questions: List[DecisionQuestion]
    """Native Decision API questions evaluated together, in order."""


class DecisionTrigger(BaseModel):
    decisions: Decisions
    """
    Questions evaluated using the current transcript and the session's shared
    Decision items.
    """

    event_type: Literal["session.input_transcript.delta", "session.output_transcript.delta"]

    type: Literal["decisions"]
