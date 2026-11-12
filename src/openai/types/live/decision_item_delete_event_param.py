# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["DecisionItemDeleteEventParam"]


class DecisionItemDeleteEventParam(TypedDict, total=False):
    """
    Delete an input item from future decisions without starting an evaluation or changing Live voice context.
    """

    item_id: Required[str]

    type: Required[Literal["decision.item.delete"]]

    event_id: Optional[str]
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """
