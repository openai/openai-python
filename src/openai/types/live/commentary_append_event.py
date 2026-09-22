# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["CommentaryAppendEvent"]


class CommentaryAppendEvent(BaseModel):
    """
    Provide context the Live model can communicate to the user, optionally for an existing client delegation.
    """

    content: str
    """Speakable context for the Live model, limited to 500 tokens.

    Use this for a result the model should communicate; use session.thinking.append
    for silent context.
    """

    delegation_id: Optional[str] = None
    """Required, nullable.

    Set null for general session context, or use the ID from
    session.delegation.created for an existing client delegation. Non-null IDs are
    not accepted with Responses delegation.
    """

    type: Literal["session.commentary.append"]
    """The Live client event type. Always `session.commentary.append`."""

    event_id: Optional[str] = None
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """
