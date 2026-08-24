from typing import Optional
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["ConversationItemRetrieveEvent"]


class ConversationItemRetrieveEvent(BaseModel):
    item_id: str
    """The ID of the item to retrieve."""

    type: Literal["conversation.item.retrieve"]
    """The event type, must be `conversation.item.retrieve`."""

    event_id: Optional[str] = None
    """Optional client-generated ID used to identify this event."""
