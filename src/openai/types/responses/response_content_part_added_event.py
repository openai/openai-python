# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .response_output_text import ResponseOutputText
from .response_output_refusal import ResponseOutputRefusal

__all__ = ["ResponseContentPartAddedEvent", "Part"]

Part: TypeAlias = Annotated[Union[ResponseOutputText, ResponseOutputRefusal], PropertyInfo(discriminator="type")]


class ResponseContentPartAddedEvent(BaseModel):
    content_index: int
    """The index of the content part that was added."""

    item_id: str
    """The ID of the output item that the content part was added to."""

    output_index: int
    """The index of the output item that the content part was added to."""

    part: Part
    """The content part that was added."""

    type: Literal["response.content_part.added"]
    """The type of the event. Always `response.content_part.added`."""
