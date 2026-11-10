# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseItemReference"]


class ResponseItemReference(BaseModel):
    """
    Reference an existing item in this Realtime session as response.create input.
    Item references are only accepted in the response input array, not as new
    conversation items.
    """

    id: str
    """The ID of an existing item in the same Realtime session."""

    type: Literal["item_reference"]
    """The type of this item. Always `item_reference`."""
