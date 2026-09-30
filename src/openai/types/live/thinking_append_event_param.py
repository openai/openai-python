# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["ThinkingAppendEventParam"]


class ThinkingAppendEventParam(TypedDict, total=False):
    """
    Provide silent reasoning or progress context to the Live model, optionally for an existing client delegation.
    """

    content: Required[str]
    """Silent reasoning or progress context, limited to 500 tokens.

    It does not directly request speech, but can influence later speech and is not a
    secrecy boundary.
    """

    delegation_id: Required[Optional[str]]
    """Required, nullable.

    Set null for general session context, or use the ID from
    session.delegation.created for an existing client delegation. Non-null IDs are
    not accepted with Responses delegation.
    """

    type: Required[Literal["session.thinking.append"]]
    """The Live client event type. Always `session.thinking.append`."""

    event_id: Optional[str]
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """
