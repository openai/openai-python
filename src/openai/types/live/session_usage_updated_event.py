# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .session_usage import SessionUsage

__all__ = ["SessionUsageUpdatedEvent", "ContextWindow"]


class ContextWindow(BaseModel):
    """The latest measured Live context-window usage.

    Omitted when the context limit is unknown.
    """

    usage_ratio: float
    """The latest active context token count divided by the Live model context limit.

    Can decrease after compaction and may lag between measured audio frames.
    """


class SessionUsageUpdatedEvent(BaseModel):
    """
    Reports cumulative Live audio usage and, when available, the most recent context-window usage. Delegated Responses token usage is reported separately in response.event events.
    """

    event_id: str
    """The unique ID of the Live server event."""

    type: Literal["session.usage.updated"]
    """The event type, always `session.usage.updated`."""

    usage: SessionUsage
    """The cumulative Live audio usage so far."""

    client_event_id: Optional[str] = None
    """
    The event_id of the client command associated with this server event, when
    supplied.
    """

    context_window: Optional[ContextWindow] = None
    """The latest measured Live context-window usage.

    Omitted when the context limit is unknown.
    """
