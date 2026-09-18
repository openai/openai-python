# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["InstructionsAppendEvent"]


class InstructionsAppendEvent(BaseModel):
    """
    Append instructions to the Live conversation while it is running, optionally associating them with an existing client delegation.
    """

    content: str
    """Instruction text to append, limited to 500 tokens.

    This is a plain string, not an array of content parts.
    """

    delegation_id: Optional[str] = None
    """Required, nullable.

    Set null for general session context, or use the ID from
    session.delegation.created for an existing client delegation. Non-null IDs are
    not accepted with Responses delegation.
    """

    type: Literal["session.instructions.append"]
    """The Live client event type. Always `session.instructions.append`."""

    event_id: Optional[str] = None
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """
