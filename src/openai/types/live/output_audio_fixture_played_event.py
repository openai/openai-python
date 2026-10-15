# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["OutputAudioFixturePlayedEvent"]


class OutputAudioFixturePlayedEvent(BaseModel):
    """
    The complete audio fixture has drained from the server mixer and normal inference has resumed. Transport buffers may still contain audio; this event does not prove listener-side completion. The optional client_event_id echoes the play command. This event is not emitted for canceled or failed playback.
    """

    event_id: str
    """The unique ID of the Live server event."""

    type: Literal["session.output_audio.fixture.played"]

    client_event_id: Optional[str] = None
    """
    The event_id of the client command associated with this server event, when
    supplied.
    """
