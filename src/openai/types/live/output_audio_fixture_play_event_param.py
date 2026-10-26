# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["OutputAudioFixturePlayEventParam"]


class OutputAudioFixturePlayEventParam(TypedDict, total=False):
    """Play one complete audio fixture through the session output.

    Send this event over the primary WebSocket or a server sideband. Audio must be raw mono PCM16 little-endian at 24 kHz, regardless of the session audio format, and at most 30 seconds. The entire payload is validated before model speech is interrupted and input is muted. Only one fixture can be active. fixture.playing acknowledges acceptance and fixture.played reports server mixer drain. These notifications are not exact transport-media boundaries. Input arriving during playback is dropped and not replayed.
    """

    audio: Required[str]
    """Base64-encoded raw mono PCM16 audio, little-endian, at 24 kHz.

    Do not include a WAV or other container header.
    """

    type: Required[Literal["session.output_audio.fixture.play"]]

    event_id: Optional[str]
    """
    Optional client identifier for correlating this command with a server event's
    client_event_id or error.client_event_id.
    """
