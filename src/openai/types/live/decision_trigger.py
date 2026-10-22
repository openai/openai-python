# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from pydantic import StrictStr, StrictBool

from ..._utils import PropertyInfo
from ..._models import BaseModel
from ..shared.decision_question_input_part import DecisionQuestionInputPart

__all__ = [
    "DecisionTrigger",
    "Decisions",
    "DecisionsQuestion",
    "DecisionsQuestionQuestionParamPredicate",
    "DecisionsQuestionQuestionParamChoice",
    "DecisionsQuestionQuestionParamChoiceChoice",
    "DecisionsQuestionQuestionParamScore",
    "DecisionsQuestionQuestionParamScoreLevel",
]


class DecisionsQuestionQuestionParamPredicate(BaseModel):
    """Estimate how likely it is that a statement about the input is true."""

    instructions: Union[str, List[DecisionQuestionInputPart]]

    type: Literal["predicate"]
    """The type of the object. Always `predicate`."""

    name: Optional[str] = None


class DecisionsQuestionQuestionParamChoiceChoice(BaseModel):
    value: Union[StrictStr, StrictBool]
    """
    Choice values are typed: a string and a boolean with the same text are distinct.
    """

    description: Optional[str] = None


class DecisionsQuestionQuestionParamChoice(BaseModel):
    """Choose from the supplied options based on the input."""

    choices: List[DecisionsQuestionQuestionParamChoiceChoice]
    """Provide between 2 and 255 choices. Each choice must be unique."""

    instructions: Union[str, List[DecisionQuestionInputPart]]

    type: Literal["choice"]
    """The type of the object. Always `choice`."""

    name: Optional[str] = None


class DecisionsQuestionQuestionParamScoreLevel(BaseModel):
    label: str

    description: Optional[str] = None


class DecisionsQuestionQuestionParamScore(BaseModel):
    """Rate the input against the supplied ordered levels."""

    instructions: Union[str, List[DecisionQuestionInputPart]]

    levels: List[DecisionsQuestionQuestionParamScoreLevel]

    type: Literal["score"]
    """The type of the object. Always `score`."""

    name: Optional[str] = None


DecisionsQuestion: TypeAlias = Annotated[
    Union[
        DecisionsQuestionQuestionParamPredicate,
        DecisionsQuestionQuestionParamChoice,
        DecisionsQuestionQuestionParamScore,
    ],
    PropertyInfo(discriminator="type"),
]


class Decisions(BaseModel):
    """
    Questions evaluated using the current transcript and the session's shared Decision items.
    """

    questions: List[DecisionsQuestion]
    """Native Decision API questions evaluated together, in order."""


class DecisionTrigger(BaseModel):
    decisions: Decisions
    """
    Questions evaluated using the current transcript and the session's shared
    Decision items.
    """

    event_type: Literal["session.input_transcript.delta", "session.output_transcript.delta"]

    type: Literal["decisions"]
