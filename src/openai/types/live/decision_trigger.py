# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel
from .decision_question import (
    Score as _compat_DecisionsQuestionQuestionParamScore,
    Choice as _compat_DecisionsQuestionQuestionParamChoice,
    Predicate as _compat_DecisionsQuestionQuestionParamPredicate,
    ScoreLevel as _compat_DecisionsQuestionQuestionParamScoreLevel,
    DecisionQuestion,
    DecisionQuestion as _compat_DecisionsQuestion,
)
from .decision_choice_option import DecisionChoiceOption as _compat_DecisionsQuestionQuestionParamChoiceChoice

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


DecisionsQuestion: TypeAlias = _compat_DecisionsQuestion

DecisionsQuestionQuestionParamChoice: TypeAlias = _compat_DecisionsQuestionQuestionParamChoice

DecisionsQuestionQuestionParamPredicate: TypeAlias = _compat_DecisionsQuestionQuestionParamPredicate

DecisionsQuestionQuestionParamScore: TypeAlias = _compat_DecisionsQuestionQuestionParamScore

DecisionsQuestionQuestionParamScoreLevel: TypeAlias = _compat_DecisionsQuestionQuestionParamScoreLevel

DecisionsQuestionQuestionParamChoiceChoice: TypeAlias = _compat_DecisionsQuestionQuestionParamChoiceChoice
