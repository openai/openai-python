from typing_extensions import Literal

from ..._models import BaseModel


class RealtimeConversationItemReference(BaseModel):
    """
    Reference to a previous conversation item in realtime input.
    """

    id: str
    """The unique ID of the conversation item being referenced."""

    type: Literal["item_reference"] = "item_reference"
    """The type of the conversation item. Always `item_reference`."""
