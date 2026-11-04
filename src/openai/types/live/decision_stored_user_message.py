# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .decision_json_object import DecisionJSONObject

__all__ = [
    "DecisionStoredUserMessage",
    "ContentPart",
    "ContentPartInputText",
    "ContentPartInputImage",
    "ContentPartInputJSON",
]


class ContentPartInputText(BaseModel):
    text: str
    """The text input to the model."""

    type: Literal["input_text"]


class ContentPartInputImage(BaseModel):
    image_url: str
    """A base64-encoded image data URL or a publicly accessible HTTP(S) image URL."""

    type: Literal["input_image"]

    detail: Optional[Literal["low", "high", "auto", "original"]] = None
    """The detail level of the image to be sent to the model.

    One of `high`, `low`, `auto`, or `original`. Defaults to `auto`.
    """


class ContentPartInputJSON(BaseModel):
    data: Union[List[DecisionJSONObject], DecisionJSONObject]

    type: Literal["input_json"]


ContentPart: TypeAlias = Annotated[
    Union[ContentPartInputText, ContentPartInputImage, ContentPartInputJSON], PropertyInfo(discriminator="type")
]


class DecisionStoredUserMessage(BaseModel):
    id: str

    content: Union[str, List[ContentPart]]
    """The text input to the model."""

    role: Literal["user"]
    """The message role. Always `user`."""

    type: Optional[Literal["message"]] = None
