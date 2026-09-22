# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ThinkingAppendEvent"]


class ThinkingAppendEvent(BaseModel):
    """
    Provide silent reasoning or progress context to the Live model, optionally for an existing client delegation.
    """

    content: str
    """Silent reasoning or progress context, limited to 500 tokens.

    It does not directly request speech, but can influence later speech and is not a
    secrecy boundary.
    """

    delegation_id: Optional[str] = None
    """Required, nullable.

    Set null for general session context, or use the ID from
    session.delegation.created for an existing client delegation. Non-null IDs are
    not accepted with Responses delegation.
    """

    type: Literal["session.thinking.append"]
    """The Live client event type. Always `session.thinking.append`."""

    event_id: Optional[str] = None
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """
