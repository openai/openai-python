# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["RealtimeTranslationInputAudioBufferAppendEventParam"]


class RealtimeTranslationInputAudioBufferAppendEventParam(TypedDict, total=False):
    """
    Send this event to append audio bytes to the translation session input audio buffer.

    WebSocket translation sessions accept base64-encoded 24 kHz PCM16 mono
    little-endian raw audio bytes. Unsupported websocket audio formats return a
    validation error because lower-quality audio materially degrades translation
    quality.

    Translation consumes 200 ms engine frames. For best realtime behavior, append
    audio in 200 ms chunks. If a chunk is shorter, the server buffers it until it
    has enough audio for one frame. If a chunk is longer, the server splits it into
    200 ms frames and enqueues them back-to-back.

    Keep appending silence while the session is active. If a client stops sending
    audio and later resumes, model time treats the resumed audio as contiguous with
    the previous audio rather than as a real-world pause.
    """

    audio: Required[str]
    """Base64-encoded 24 kHz PCM16 mono audio bytes."""

    type: Required[Literal["session.input_audio_buffer.append"]]
    """The event type, must be `session.input_audio_buffer.append`."""

    event_id: str
    """Optional client-generated ID used to identify this event."""
