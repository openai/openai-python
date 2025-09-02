# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from .realtime_transcription_session_create_request_param import RealtimeTranscriptionSessionCreateRequestParam

__all__ = ["TranscriptionSessionUpdateParam"]


class TranscriptionSessionUpdateParam(TypedDict, total=False):
    session: Required[RealtimeTranscriptionSessionCreateRequestParam]
    """Realtime transcription session object configuration."""

    type: Required[Literal["transcription_session.update"]]
    """The event type, must be `transcription_session.update`."""

    event_id: str
    """Optional client-generated ID used to identify this event."""
