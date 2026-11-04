# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .realtime_translation_session_update_request import RealtimeTranslationSessionUpdateRequest

__all__ = ["RealtimeTranslationSessionUpdateEvent"]


class RealtimeTranslationSessionUpdateEvent(BaseModel):
    """Send this event to update the translation session configuration.

    Translation
    sessions support updates to `audio.output.language`, `audio.input.transcription`,
    and `audio.input.noise_reduction`.
    """

    session: RealtimeTranslationSessionUpdateRequest
    """Translation session fields to update.

    The session `type` and `model` are set at creation and cannot be changed with
    `session.update`.
    """

    type: Literal["session.update"]
    """The event type, must be `session.update`."""

    event_id: Optional[str] = None
    """Optional client-generated ID used to identify this event."""
