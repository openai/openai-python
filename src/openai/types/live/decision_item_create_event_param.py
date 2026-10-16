# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = [
    "DecisionItemCreateEventParam",
    "Item",
    "ItemContentParts",
    "ItemContentPartsInputText",
    "ItemContentPartsInputImage",
]


class ItemContentPartsInputText(TypedDict, total=False):
    text: Required[str]
    """The text input to the model."""

    type: Required[Literal["input_text"]]
    """The type of the input item. Always `input_text`."""


class ItemContentPartsInputImage(TypedDict, total=False):
    image_url: Required[str]
    """An inline image encoded as a data URL."""

    type: Required[Literal["input_image"]]
    """The type of the input item. Always `input_image`."""

    detail: Optional[Literal["low", "high", "auto", "original"]]
    """The detail level of the image to be sent to the model.

    One of `high`, `low`, `auto`, or `original`. Defaults to `auto`.
    """


ItemContentParts: TypeAlias = Union[ItemContentPartsInputText, ItemContentPartsInputImage]


class Item(TypedDict, total=False):
    content: Required[Union[str, Iterable[ItemContentParts]]]
    """The text input to the model."""

    role: Required[Literal["user"]]
    """The message role. Always `user`."""

    id: Optional[str]
    """The unique ID of this message item."""

    type: Literal["message"]


class DecisionItemCreateEventParam(TypedDict, total=False):
    """
    Append an input item for future decisions without starting an evaluation or changing Live voice context.
    """

    item: Required[Item]

    type: Required[Literal["decision.item.create"]]

    event_id: Optional[str]
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """
