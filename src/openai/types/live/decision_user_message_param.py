# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .decision_json_object import DecisionJSONObject

__all__ = [
    "DecisionUserMessageParam",
    "ContentPart",
    "ContentPartInputText",
    "ContentPartInputImage",
    "ContentPartInputJSON",
]


class ContentPartInputText(TypedDict, total=False):
    text: Required[str]
    """The text input to the model."""

    type: Required[Literal["input_text"]]


class ContentPartInputImage(TypedDict, total=False):
    image_url: Required[str]
    """A base64-encoded image data URL or a publicly accessible HTTP(S) image URL."""

    type: Required[Literal["input_image"]]

    detail: Optional[Literal["low", "high", "auto", "original"]]
    """The detail level of the image to be sent to the model.

    One of `high`, `low`, `auto`, or `original`. Defaults to `auto`.
    """


class ContentPartInputJSON(TypedDict, total=False):
    data: Required[Union[DecisionJSONObject, Iterable[DecisionJSONObject]]]

    type: Required[Literal["input_json"]]


ContentPart: TypeAlias = Union[ContentPartInputText, ContentPartInputImage, ContentPartInputJSON]


class DecisionUserMessageParam(TypedDict, total=False):
    content: Required[Union[str, Iterable[ContentPart]]]
    """The text input to the model."""

    role: Required[Literal["user"]]
    """The message role. Always `user`."""

    id: Optional[str]
    """The unique ID of this message item."""

    type: Literal["message"]
