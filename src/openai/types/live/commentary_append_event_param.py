# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["CommentaryAppendEventParam"]


class CommentaryAppendEventParam(TypedDict, total=False):
    """
    Provide context the Live model can communicate to the user, optionally for an existing client delegation.
    """

    content: Required[str]
    """Speakable context for the Live model, limited to 500 tokens.

    Use this for a result the model should communicate; use session.thinking.append
    for silent context.
    """

    delegation_id: Required[Optional[str]]
    """Required, nullable.

    Set null for general session context, or use the ID from
    session.delegation.created for an existing client delegation. Non-null IDs are
    not accepted with Responses delegation.
    """

    type: Required[Literal["session.commentary.append"]]
    """The Live client event type. Always `session.commentary.append`."""

    event_id: Optional[str]
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """
