# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from .client_config_param import ClientConfigParam
from .responses_delegation_update_config_param import ResponsesDelegationUpdateConfigParam

__all__ = ["MediaSessionForkConfigParam", "Delegation"]


class Delegation(TypedDict, total=False):
    """
    Update the Responses backend for an existing Live session without changing delegation ownership.
    """

    type: Required[Literal["responses"]]
    """The delegation owner.

    Always `responses` for tasks handled by the Responses API.
    """

    acknowledgement_delay_ms: int
    """
    Milliseconds to wait before requesting an automatic spoken acknowledgement for a
    delegation. The model may still speak before this delay. Any commentary or
    thinking appended to the session cancels all pending acknowledgements, including
    those for other delegations. Defaults to 400 for Decisions sessions and 0
    (request immediately) for other sessions. Omission in a session update preserves
    the current value. Updates apply to subsequent delegations.
    """

    responses: ResponsesDelegationUpdateConfigParam
    """Responses backend settings to update.

    Omitted settings keep their existing values.
    """


class MediaSessionForkConfigParam(TypedDict, total=False):
    """Optional overrides for a stored Live session.

    Omitted settings are inherited. The model, voice, frontend instructions, and prior conversation come from the stored session. WebRTC negotiates its audio format; audio.format is only supported on WebSocket forks.
    """

    client: ClientConfigParam
    """
    Startup-only capabilities for an untrusted frontend attached to a unified WebRTC
    session. Trusted sideband connections are unaffected.
    """

    delegation: Delegation
    """
    Update the Responses backend for an existing Live session without changing
    delegation ownership.
    """

    store: bool
    """Whether to store the forked session.

    Omission inherits the stored session's setting.
    """
