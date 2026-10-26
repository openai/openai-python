# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .decision_input_text import DecisionInputText
from .decision_json_object import DecisionJSONObject
from .decision_choice_option import DecisionChoiceOption

__all__ = [
    "DecisionQuestion",
    "Choice",
    "ChoiceInstructionsParts",
    "ChoiceInstructionsPartsInputImage",
    "ChoiceInstructionsPartsInputJSON",
    "Predicate",
    "PredicateInstructionsParts",
    "PredicateInstructionsPartsInputImage",
    "PredicateInstructionsPartsInputJSON",
    "Score",
    "ScoreInstructionsParts",
    "ScoreInstructionsPartsInputImage",
    "ScoreInstructionsPartsInputJSON",
    "ScoreLevel",
]


class ChoiceInstructionsPartsInputImage(BaseModel):
    image_url: str
    """A base64-encoded image data URL or a publicly accessible HTTP(S) image URL."""

    type: Literal["input_image"]

    detail: Optional[Literal["low", "high", "auto", "original"]] = None
    """The detail level of the image to be sent to the model.

    One of `high`, `low`, `auto`, or `original`. Defaults to `auto`.
    """


class ChoiceInstructionsPartsInputJSON(BaseModel):
    data: Union[List[DecisionJSONObject], DecisionJSONObject]

    type: Literal["input_json"]


ChoiceInstructionsParts: TypeAlias = Annotated[
    Union[DecisionInputText, ChoiceInstructionsPartsInputImage, ChoiceInstructionsPartsInputJSON],
    PropertyInfo(discriminator="type"),
]


class Choice(BaseModel):
    choices: List[DecisionChoiceOption]

    instructions: Union[str, List[ChoiceInstructionsParts]]

    type: Literal["choice"]

    name: Optional[str] = None


class PredicateInstructionsPartsInputImage(BaseModel):
    image_url: str
    """A base64-encoded image data URL or a publicly accessible HTTP(S) image URL."""

    type: Literal["input_image"]

    detail: Optional[Literal["low", "high", "auto", "original"]] = None
    """The detail level of the image to be sent to the model.

    One of `high`, `low`, `auto`, or `original`. Defaults to `auto`.
    """


class PredicateInstructionsPartsInputJSON(BaseModel):
    data: Union[List[DecisionJSONObject], DecisionJSONObject]

    type: Literal["input_json"]


PredicateInstructionsParts: TypeAlias = Annotated[
    Union[DecisionInputText, PredicateInstructionsPartsInputImage, PredicateInstructionsPartsInputJSON],
    PropertyInfo(discriminator="type"),
]


class Predicate(BaseModel):
    instructions: Union[str, List[PredicateInstructionsParts]]

    type: Literal["predicate"]

    name: Optional[str] = None


class ScoreInstructionsPartsInputImage(BaseModel):
    image_url: str
    """A base64-encoded image data URL or a publicly accessible HTTP(S) image URL."""

    type: Literal["input_image"]

    detail: Optional[Literal["low", "high", "auto", "original"]] = None
    """The detail level of the image to be sent to the model.

    One of `high`, `low`, `auto`, or `original`. Defaults to `auto`.
    """


class ScoreInstructionsPartsInputJSON(BaseModel):
    data: Union[List[DecisionJSONObject], DecisionJSONObject]

    type: Literal["input_json"]


ScoreInstructionsParts: TypeAlias = Annotated[
    Union[DecisionInputText, ScoreInstructionsPartsInputImage, ScoreInstructionsPartsInputJSON],
    PropertyInfo(discriminator="type"),
]


class ScoreLevel(BaseModel):
    label: str

    description: Optional[str] = None


class Score(BaseModel):
    instructions: Union[str, List[ScoreInstructionsParts]]

    levels: List[ScoreLevel]

    type: Literal["score"]

    name: Optional[str] = None


DecisionQuestion: TypeAlias = Annotated[Union[Choice, Predicate, Score], PropertyInfo(discriminator="type")]
