# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union
from typing_extensions import Literal, Annotated, TypeAlias

from .._utils import PropertyInfo
from .._models import BaseModel

__all__ = [
    "EvalLabelModelGrader",
    "Input",
    "InputInputMessage",
    "InputInputMessageContent",
    "InputAssistant",
    "InputAssistantContent",
]


class InputInputMessageContent(BaseModel):
    text: str
    """The text content."""

    type: Literal["input_text"]
    """The type of content, which is always `input_text`."""


class InputInputMessage(BaseModel):
    content: InputInputMessageContent

    role: Literal["user", "system", "developer"]
    """The role of the message. One of `user`, `system`, or `developer`."""

    type: Literal["message"]
    """The type of item, which is always `message`."""


class InputAssistantContent(BaseModel):
    text: str
    """The text content."""

    type: Literal["output_text"]
    """The type of content, which is always `output_text`."""


class InputAssistant(BaseModel):
    content: InputAssistantContent

    role: Literal["assistant"]
    """The role of the message. Must be `assistant` for output."""

    type: Literal["message"]
    """The type of item, which is always `message`."""


Input: TypeAlias = Annotated[Union[InputInputMessage, InputAssistant], PropertyInfo(discriminator="role")]


class EvalLabelModelGrader(BaseModel):
    input: List[Input]

    labels: List[str]
    """The labels to assign to each item in the evaluation."""

    model: str
    """The model to use for the evaluation. Must support structured outputs."""

    name: str
    """The name of the grader."""

    passing_labels: List[str]
    """The labels that indicate a passing result. Must be a subset of labels."""

    type: Literal["label_model"]
    """The object type, which is always `label_model`."""
