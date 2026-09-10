# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel

__all__ = [
    "AgentSessionMessageContent",
    "MessageContentResourceInputText",
    "MessageContentResourceInputImage",
    "MessageContentResourceOutputText",
]


class MessageContentResourceInputText(BaseModel):
    """Text supplied by the user."""

    text: str
    """The text supplied by the user."""

    type: Literal["input_text"]
    """The type of the object. Always `input_text`."""


class MessageContentResourceInputImage(BaseModel):
    """An image supplied by the user."""

    image_url: str
    """
    The URL of the image supplied by the user, which may be a base64-encoded data
    URL.
    """

    type: Literal["input_image"]
    """The type of the object. Always `input_image`."""


class MessageContentResourceOutputText(BaseModel):
    """Text produced by the assistant."""

    text: str
    """The text produced by the assistant."""

    type: Literal["output_text"]
    """The type of the object. Always `output_text`."""


AgentSessionMessageContent: TypeAlias = Annotated[
    Union[MessageContentResourceInputText, MessageContentResourceInputImage, MessageContentResourceOutputText],
    PropertyInfo(discriminator="type"),
]
