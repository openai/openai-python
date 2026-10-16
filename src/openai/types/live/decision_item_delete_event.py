# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["DecisionItemDeleteEvent"]


class DecisionItemDeleteEvent(BaseModel):
    """
    Delete an input item from future decisions without starting an evaluation or changing Live voice context.
    """

    item_id: str

    type: Literal["decision.item.delete"]

    event_id: Optional[str] = None
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """
