# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["InputAudioUnmuteEventParam"]


class InputAudioUnmuteEventParam(TypedDict, total=False):
    """Resume audio input to a Live model after muting it.

    The server acknowledges with `session.input_audio.unmuted`.
    """

    type: Required[Literal["session.input_audio.unmute"]]
    """The Live client event type. Always `session.input_audio.unmute`."""

    event_id: Optional[str]
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """
