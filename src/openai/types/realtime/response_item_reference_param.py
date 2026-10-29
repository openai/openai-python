# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ResponseItemReferenceParam"]


class ResponseItemReferenceParam(TypedDict, total=False):
    """
    Reference an existing item in this Realtime session as response.create input.
    Item references are only accepted in the response input array, not as new
    conversation items.
    """

    id: Required[str]
    """The ID of an existing item in the same Realtime session."""

    type: Required[Literal["item_reference"]]
    """The type of this item. Always `item_reference`."""
