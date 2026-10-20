# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from pydantic import StrictStr, StrictBool

from ..._utils import PropertyInfo
from ..._models import BaseModel

__all__ = [
    "DecisionsDelegationUpdateConfig",
    "Question",
    "QuestionQuestionParamPredicate",
    "QuestionQuestionParamChoice",
    "QuestionQuestionParamChoiceChoice",
    "QuestionQuestionParamScore",
    "QuestionQuestionParamScoreLevel",
]


class QuestionQuestionParamPredicate(BaseModel):
    """Estimate how likely it is that a statement about the input is true."""

    instructions: str

    type: Literal["predicate"]
    """The type of the object. Always `predicate`."""

    name: Optional[str] = None


class QuestionQuestionParamChoiceChoice(BaseModel):
    value: Union[StrictStr, StrictBool]
    """
    Choice values are typed: a string and a boolean with the same text are distinct.
    """

    description: Optional[str] = None


class QuestionQuestionParamChoice(BaseModel):
    """Choose from the supplied options based on the input."""

    choices: List[QuestionQuestionParamChoiceChoice]
    """Provide between 2 and 255 choices. Each choice must be unique."""

    instructions: str

    type: Literal["choice"]
    """The type of the object. Always `choice`."""

    name: Optional[str] = None


class QuestionQuestionParamScoreLevel(BaseModel):
    label: str

    description: Optional[str] = None


class QuestionQuestionParamScore(BaseModel):
    """Rate the input against the supplied ordered levels."""

    instructions: str

    levels: List[QuestionQuestionParamScoreLevel]

    type: Literal["score"]
    """The type of the object. Always `score`."""

    name: Optional[str] = None


Question: TypeAlias = Annotated[
    Union[QuestionQuestionParamPredicate, QuestionQuestionParamChoice, QuestionQuestionParamScore],
    PropertyInfo(discriminator="type"),
]


class DecisionsDelegationUpdateConfig(BaseModel):
    model: Optional[str] = None

    questions: Optional[List[Question]] = None
    """Native Decision API questions evaluated together, in order."""
