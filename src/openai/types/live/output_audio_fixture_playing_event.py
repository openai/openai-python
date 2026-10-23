# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["OutputAudioFixturePlayingEvent"]


class OutputAudioFixturePlayingEvent(BaseModel):
    """The existing playback path has accepted the validated audio fixture.

    This acknowledgment does not identify when the listener receives the first sample. The optional client_event_id echoes the play command.
    """

    event_id: str
    """The unique ID of the Live server event."""

    type: Literal["session.output_audio.fixture.playing"]

    client_event_id: Optional[str] = None
    """
    The event_id of the client command associated with this server event, when
    supplied.
    """
