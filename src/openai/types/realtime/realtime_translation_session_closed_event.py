# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["RealtimeTranslationSessionClosedEvent"]


class RealtimeTranslationSessionClosedEvent(BaseModel):
    """Returned when a realtime translation session is closed."""

    event_id: str
    """The unique ID of the server event."""

    type: Literal["session.closed"]
    """The event type, must be `session.closed`."""
