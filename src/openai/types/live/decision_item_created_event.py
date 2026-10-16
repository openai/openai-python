# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel

__all__ = [
    "DecisionItemCreatedEvent",
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
    id: str
    """The ID of the stored Decision input item."""

    content: Union[str, List[ItemContentParts]]
    """The text input to the model."""

    role: Literal["user"]
    """The message role. Always `user`."""

    type: Optional[Literal["message"]] = None


class DecisionItemCreatedEvent(BaseModel):
    """An input item was appended for future decisions."""

    event_id: str
    """The unique ID of the Live server event."""

    item: Item

    type: Literal["decision.item.created"]

    client_event_id: Optional[str] = None
    """
    The event_id of the client command associated with this server event, when
    supplied.
    """
