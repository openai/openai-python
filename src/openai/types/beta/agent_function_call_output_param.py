# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .input_content_param import InputContentParam

__all__ = ["AgentFunctionCallOutputParam", "InputContentParamInputText", "InputContentParamInputImage"]


class InputContentParamInputText(TypedDict, total=False):
    """Text input to the model."""

    text: Required[str]
    """The text sent to the model."""

    type: Required[Literal["input_text"]]
    """The type of the object. Always `input_text`."""


class InputContentParamInputImage(TypedDict, total=False):
    """Image input to the model."""

    image_url: Required[str]
    """The URL of the image sent to the model."""

    type: Required[Literal["input_image"]]
    """The type of the object. Always `input_image`."""


AgentFunctionCallOutputParam: TypeAlias = Union[str, Iterable[InputContentParam]]
