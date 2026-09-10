# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from .audio_format_param import AudioFormatParam
from .client_config_param import ClientConfigParam
from .responses_delegation_update_config_param import ResponsesDelegationUpdateConfigParam

__all__ = ["ForkSessionConfigParam", "Audio", "Delegation"]


class Audio(TypedDict, total=False):
    """Audio format for a WebSocket fork.

    WebRTC forks negotiate their audio format and must omit this field.
    """

    format: AudioFormatParam
    """
    Audio encoding and sample rate for audio sent and received over a Live WebSocket
    connection. WebRTC and SIP negotiate their media format separately.
    """


class Delegation(TypedDict, total=False):
    """Overrides for the stored session’s Responses backend.

    Only supported when the stored session already uses Responses delegation; the delegation type cannot change.
    """

    type: Required[Literal["responses"]]
    """The delegation owner.

    Always `responses` for tasks handled by the Responses API.
    """

    responses: ResponsesDelegationUpdateConfigParam
    """Responses backend settings to update.

    Omitted settings keep their existing values.
    """


class ForkSessionConfigParam(TypedDict, total=False):
    """Overrides for a stored session after connecting to the fork WebSocket.

    An empty object inherits the stored configuration; do not supply a new model. audio.format applies only to the new WebSocket connection. client overrides are only supported for WebRTC forks.
    """

    audio: Audio
    """Audio format for a WebSocket fork.

    WebRTC forks negotiate their audio format and must omit this field.
    """

    client: ClientConfigParam
    """Frontend data-channel permissions for a WebRTC fork.

    Omitted permissions inherit the stored values. Not supported for WebSocket
    forks.
    """

    delegation: Delegation
    """Overrides for the stored session’s Responses backend.

    Only supported when the stored session already uses Responses delegation; the
    delegation type cannot change.
    """

    store: bool
    """Whether to store the forked session.

    Omission inherits the stored session's setting.
    """
