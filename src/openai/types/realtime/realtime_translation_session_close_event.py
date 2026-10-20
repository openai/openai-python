# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["RealtimeTranslationSessionCloseEvent"]


class RealtimeTranslationSessionCloseEvent(BaseModel):
    """Gracefully close the realtime translation session.

    The server flushes pending
    input audio and emits any remaining translated output before closing the
    session.
    """

    type: Literal["session.close"]
    """The event type, must be `session.close`."""

    event_id: Optional[str] = None
    """Optional client-generated ID used to identify this event."""
