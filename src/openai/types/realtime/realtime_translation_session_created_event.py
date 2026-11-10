# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel
from .realtime_translation_session import RealtimeTranslationSession

__all__ = ["RealtimeTranslationSessionCreatedEvent"]


class RealtimeTranslationSessionCreatedEvent(BaseModel):
    """Returned when a translation session is created.

    Emitted automatically when a
    new connection is established as the first server event. This event contains
    the default translation session configuration.
    """

    event_id: str
    """The unique ID of the server event."""

    session: RealtimeTranslationSession
    """The translation session configuration."""

    type: Literal["session.created"]
    """The event type, must be `session.created`."""
