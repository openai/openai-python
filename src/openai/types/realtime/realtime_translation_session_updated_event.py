# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel
from .realtime_translation_session import RealtimeTranslationSession

__all__ = ["RealtimeTranslationSessionUpdatedEvent"]


class RealtimeTranslationSessionUpdatedEvent(BaseModel):
    """
    Returned when a translation session is updated with a `session.update` event,
    unless there is an error.
    """

    event_id: str
    """The unique ID of the server event."""

    session: RealtimeTranslationSession
    """The translation session configuration."""

    type: Literal["session.updated"]
    """The event type, must be `session.updated`."""
