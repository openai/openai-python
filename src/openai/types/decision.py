# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from pydantic import StrictStr, StrictBool

from .._utils import PropertyInfo
from .._models import BaseModel

__all__ = [
    "Decision",
    "Answer",
    "AnswerAnswerResourcePredicate",
    "AnswerAnswerResourceChoice",
    "AnswerAnswerResourceChoiceProbability",
    "AnswerAnswerResourceScore",
    "AnswerAnswerResourceScoreProbability",
    "AnswerAnswerResourceRefusal",
    "Usage",
    "UsageInputTokensDetails",
    "UsageOutputTokensDetails",
]


class AnswerAnswerResourcePredicate(BaseModel):
    name: Optional[str] = None

    probability: float

    type: Literal["predicate"]
    """The type of the object. Always `predicate`."""


class AnswerAnswerResourceChoiceProbability(BaseModel):
    probability: float

    value: Union[StrictStr, StrictBool]
    """
    Choice values are typed: a string and a boolean with the same text are distinct.
    """


class AnswerAnswerResourceChoice(BaseModel):
    choice: Union[StrictStr, StrictBool]
    """
    Choice values are typed: a string and a boolean with the same text are distinct.
    """

    confidence: float

    name: Optional[str] = None

    probabilities: List[AnswerAnswerResourceChoiceProbability]

    type: Literal["choice"]
    """The type of the object. Always `choice`."""


class AnswerAnswerResourceScoreProbability(BaseModel):
    label: str

    probability: float

    value: int


class AnswerAnswerResourceScore(BaseModel):
    confidence: float

    name: Optional[str] = None

    probabilities: List[AnswerAnswerResourceScoreProbability]

    score: float

    type: Literal["score"]
    """The type of the object. Always `score`."""


class AnswerAnswerResourceRefusal(BaseModel):
    """The host may decline one question without disclosing its refusal score."""

    name: Optional[str] = None

    type: Literal["refusal"]
    """The type of the object. Always `refusal`."""


Answer: TypeAlias = Annotated[
    Union[
        AnswerAnswerResourcePredicate,
        AnswerAnswerResourceChoice,
        AnswerAnswerResourceScore,
        AnswerAnswerResourceRefusal,
    ],
    PropertyInfo(discriminator="type"),
]


class UsageInputTokensDetails(BaseModel):
    cache_write_tokens: int

    cached_tokens: int


class UsageOutputTokensDetails(BaseModel):
    reasoning_tokens: int


class Usage(BaseModel):
    input_tokens: int

    input_tokens_details: UsageInputTokensDetails

    output_tokens: int

    output_tokens_details: UsageOutputTokensDetails

    total_tokens: int


class Decision(BaseModel):
    answers: List[Answer]

    model: str

    usage: Usage
