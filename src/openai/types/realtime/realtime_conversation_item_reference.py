# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["RealtimeConversationItemReference"]


class RealtimeConversationItemReference(BaseModel):
    """A reference to an existing conversation item in a Realtime prompt."""

    id: str
    """The unique ID of the conversation item being referenced."""

    type: Literal["item_reference"]
    """The type of the reference. Always `item_reference`."""
