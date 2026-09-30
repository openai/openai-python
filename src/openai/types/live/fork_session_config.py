# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .audio_format import AudioFormat
from .client_config import ClientConfig
from .responses_delegation_update_config import ResponsesDelegationUpdateConfig

__all__ = ["ForkSessionConfig", "Audio", "Delegation"]


class Audio(BaseModel):
    """Audio format for a WebSocket fork.

    WebRTC forks negotiate their audio format and must omit this field.
    """

    format: Optional[AudioFormat] = None
    """
    Audio encoding and sample rate for audio sent and received over a Live WebSocket
    connection. WebRTC and SIP negotiate their media format separately.
    """


class Delegation(BaseModel):
    """Overrides for the stored session’s Responses backend.

    Only supported when the stored session already uses Responses delegation; the delegation type cannot change.
    """

    type: Literal["responses"]
    """The delegation owner.

    Always `responses` for tasks handled by the Responses API.
    """

    responses: Optional[ResponsesDelegationUpdateConfig] = None
    """Responses backend settings to update.

    Omitted settings keep their existing values.
    """


class ForkSessionConfig(BaseModel):
    """Overrides for a stored session after connecting to the fork WebSocket.

    An empty object inherits the stored configuration; do not supply a new model. audio.format applies only to the new WebSocket connection. client overrides are only supported for WebRTC forks.
    """

    audio: Optional[Audio] = None
    """Audio format for a WebSocket fork.

    WebRTC forks negotiate their audio format and must omit this field.
    """

    client: Optional[ClientConfig] = None
    """Frontend data-channel permissions for a WebRTC fork.

    Omitted permissions inherit the stored values. Not supported for WebSocket
    forks.
    """

    delegation: Optional[Delegation] = None
    """Overrides for the stored session’s Responses backend.

    Only supported when the stored session already uses Responses delegation; the
    delegation type cannot change.
    """

    store: Optional[bool] = None
    """Whether to store the forked session.

    Omission inherits the stored session's setting.
    """
