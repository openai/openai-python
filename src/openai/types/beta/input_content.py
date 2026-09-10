# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel

__all__ = ["InputContent", "InputContentResourceInputText", "InputContentResourceInputImage"]


class InputContentResourceInputText(BaseModel):
    """Text input recorded in a session item."""

    text: str
    """The text supplied to the agent."""

    type: Literal["input_text"]
    """The type of the object. Always `input_text`."""


class InputContentResourceInputImage(BaseModel):
    """Image input recorded in a session item."""

    image_url: str
    """
    The URL of the image supplied to the agent, which may be a base64-encoded data
    URL.
    """

    type: Literal["input_image"]
    """The type of the object. Always `input_image`."""


InputContent: TypeAlias = Annotated[
    Union[InputContentResourceInputText, InputContentResourceInputImage], PropertyInfo(discriminator="type")
]
