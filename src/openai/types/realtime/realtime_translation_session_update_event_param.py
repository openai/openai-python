# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from .realtime_translation_session_update_request_param import RealtimeTranslationSessionUpdateRequestParam

__all__ = ["RealtimeTranslationSessionUpdateEventParam"]


class RealtimeTranslationSessionUpdateEventParam(TypedDict, total=False):
    """Send this event to update the translation session configuration.

    Translation
    sessions support updates to `audio.output.language`, `audio.input.transcription`,
    and `audio.input.noise_reduction`.
    """

    session: Required[RealtimeTranslationSessionUpdateRequestParam]
    """Translation session fields to update.

    The session `type` and `model` are set at creation and cannot be changed with
    `session.update`.
    """

    type: Required[Literal["session.update"]]
    """The event type, must be `session.update`."""

    event_id: str
    """Optional client-generated ID used to identify this event."""
