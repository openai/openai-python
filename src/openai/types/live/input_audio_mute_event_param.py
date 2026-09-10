# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["InputAudioMuteEventParam"]


class InputAudioMuteEventParam(TypedDict, total=False):
    """Mute audio input to the Live model without closing the session.

    The server acknowledges with `session.input_audio.muted`.
    """

    type: Required[Literal["session.input_audio.mute"]]
    """The Live client event type. Always `session.input_audio.mute`."""

    event_id: Optional[str]
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """
