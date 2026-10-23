# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel

__all__ = [
    "DecisionItemCreateEvent",
    "Item",
    "ItemContentParts",
    "ItemContentPartsInputText",
    "ItemContentPartsInputImage",
]


class ItemContentPartsInputText(BaseModel):
    text: str
    """The text input to the model."""

    type: Literal["input_text"]
    """The type of the input item. Always `input_text`."""


class ItemContentPartsInputImage(BaseModel):
    image_url: str
    """An inline image encoded as a data URL."""

    type: Literal["input_image"]
    """The type of the input item. Always `input_image`."""

    detail: Optional[Literal["low", "high", "auto", "original"]] = None
    """The detail level of the image to be sent to the model.

    One of `high`, `low`, `auto`, or `original`. Defaults to `auto`.
    """


ItemContentParts: TypeAlias = Annotated[
    Union[ItemContentPartsInputText, ItemContentPartsInputImage], PropertyInfo(discriminator="type")
]


class Item(BaseModel):
    content: Union[str, List[ItemContentParts]]
    """The text input to the model."""

    role: Literal["user"]
    """The message role. Always `user`."""

    id: Optional[str] = None
    """The unique ID of this message item."""

    type: Optional[Literal["message"]] = None


class DecisionItemCreateEvent(BaseModel):
    """
    Append an input item for future decisions without starting an evaluation or changing Live voice context.
    """

    item: Item

    type: Literal["decision.item.create"]

    event_id: Optional[str] = None
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """
