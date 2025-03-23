# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .response_output_text import ResponseOutputText
from .response_output_refusal import ResponseOutputRefusal

__all__ = ["ResponseContentPartDoneEvent", "Part"]

Part: TypeAlias = Annotated[Union[ResponseOutputText, ResponseOutputRefusal], PropertyInfo(discriminator="type")]


class ResponseContentPartDoneEvent(BaseModel):
    content_index: int
    """The index of the content part that is done."""

    item_id: str
    """The ID of the output item that the content part was added to."""

    output_index: int
    """The index of the output item that the content part was added to."""

    part: Part
    """The content part that is done."""

    type: Literal["response.content_part.done"]
    """The type of the event. Always `response.content_part.done`."""
