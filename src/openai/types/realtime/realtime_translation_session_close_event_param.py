# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["RealtimeTranslationSessionCloseEventParam"]


class RealtimeTranslationSessionCloseEventParam(TypedDict, total=False):
    """Gracefully close the realtime translation session.

    The server flushes pending
    input audio and emits any remaining translated output before closing the
    session.
    """

    type: Required[Literal["session.close"]]
    """The event type, must be `session.close`."""

    event_id: str
    """Optional client-generated ID used to identify this event."""
