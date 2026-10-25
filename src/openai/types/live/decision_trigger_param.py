# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .decision_question_param import (
    Score as _compat_DecisionsQuestionQuestionParamScore,
    Choice as _compat_DecisionsQuestionQuestionParamChoice,
    Predicate as _compat_DecisionsQuestionQuestionParamPredicate,
    ScoreLevel as _compat_DecisionsQuestionQuestionParamScoreLevel,
    DecisionQuestionParam,
    DecisionQuestionParam as _compat_DecisionsQuestion,
)
from .decision_choice_option_param import (
    DecisionChoiceOptionParam as _compat_DecisionsQuestionQuestionParamChoiceChoice,
)

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


DecisionsQuestion: TypeAlias = _compat_DecisionsQuestion

DecisionsQuestionQuestionParamChoice: TypeAlias = _compat_DecisionsQuestionQuestionParamChoice

DecisionsQuestionQuestionParamPredicate: TypeAlias = _compat_DecisionsQuestionQuestionParamPredicate

DecisionsQuestionQuestionParamScore: TypeAlias = _compat_DecisionsQuestionQuestionParamScore

DecisionsQuestionQuestionParamScoreLevel: TypeAlias = _compat_DecisionsQuestionQuestionParamScoreLevel

DecisionsQuestionQuestionParamChoiceChoice: TypeAlias = _compat_DecisionsQuestionQuestionParamChoiceChoice
