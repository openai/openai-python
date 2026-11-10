# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .decision_json_object import DecisionJSONObject
from .decision_input_text_param import DecisionInputTextParam
from .decision_choice_option_param import DecisionChoiceOptionParam

__all__ = [
    "DecisionQuestionParam",
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


class ChoiceInstructionsPartsInputImage(TypedDict, total=False):
    image_url: Required[str]
    """A base64-encoded image data URL or a publicly accessible HTTP(S) image URL."""

    type: Required[Literal["input_image"]]

    detail: Optional[Literal["low", "high", "auto", "original"]]
    """The detail level of the image to be sent to the model.

    One of `high`, `low`, `auto`, or `original`. Defaults to `auto`.
    """


class ChoiceInstructionsPartsInputJSON(TypedDict, total=False):
    data: Required[Union[DecisionJSONObject, Iterable[DecisionJSONObject]]]

    type: Required[Literal["input_json"]]


ChoiceInstructionsParts: TypeAlias = Union[
    DecisionInputTextParam, ChoiceInstructionsPartsInputImage, ChoiceInstructionsPartsInputJSON
]


class Choice(TypedDict, total=False):
    choices: Required[Iterable[DecisionChoiceOptionParam]]

    instructions: Required[Union[str, Iterable[ChoiceInstructionsParts]]]

    type: Required[Literal["choice"]]

    name: str


class PredicateInstructionsPartsInputImage(TypedDict, total=False):
    image_url: Required[str]
    """A base64-encoded image data URL or a publicly accessible HTTP(S) image URL."""

    type: Required[Literal["input_image"]]

    detail: Optional[Literal["low", "high", "auto", "original"]]
    """The detail level of the image to be sent to the model.

    One of `high`, `low`, `auto`, or `original`. Defaults to `auto`.
    """


class PredicateInstructionsPartsInputJSON(TypedDict, total=False):
    data: Required[Union[DecisionJSONObject, Iterable[DecisionJSONObject]]]

    type: Required[Literal["input_json"]]


PredicateInstructionsParts: TypeAlias = Union[
    DecisionInputTextParam, PredicateInstructionsPartsInputImage, PredicateInstructionsPartsInputJSON
]


class Predicate(TypedDict, total=False):
    instructions: Required[Union[str, Iterable[PredicateInstructionsParts]]]

    type: Required[Literal["predicate"]]

    name: str


class ScoreInstructionsPartsInputImage(TypedDict, total=False):
    image_url: Required[str]
    """A base64-encoded image data URL or a publicly accessible HTTP(S) image URL."""

    type: Required[Literal["input_image"]]

    detail: Optional[Literal["low", "high", "auto", "original"]]
    """The detail level of the image to be sent to the model.

    One of `high`, `low`, `auto`, or `original`. Defaults to `auto`.
    """


class ScoreInstructionsPartsInputJSON(TypedDict, total=False):
    data: Required[Union[DecisionJSONObject, Iterable[DecisionJSONObject]]]

    type: Required[Literal["input_json"]]


ScoreInstructionsParts: TypeAlias = Union[
    DecisionInputTextParam, ScoreInstructionsPartsInputImage, ScoreInstructionsPartsInputJSON
]


class ScoreLevel(TypedDict, total=False):
    label: Required[str]

    description: str


class Score(TypedDict, total=False):
    instructions: Required[Union[str, Iterable[ScoreInstructionsParts]]]

    levels: Required[Iterable[ScoreLevel]]

    type: Required[Literal["score"]]

    name: str


DecisionQuestionParam: TypeAlias = Union[Choice, Predicate, Score]
