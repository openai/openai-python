# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ClientDelegationParam"]


class ClientDelegationParam(TypedDict, total=False):
    """Delegate tasks to your application.

    The Live session emits delegation events that your backend handles.
    """

    type: Required[Literal["client"]]
    """The delegation owner. Always `client` for tasks handled by your application."""

    acknowledgement_delay_ms: int
    """
    Milliseconds to wait before requesting an automatic spoken acknowledgement for a
    delegation. The model may still speak before this delay. Any commentary or
    thinking appended to the session cancels all pending acknowledgements, including
    those for other delegations. Defaults to 400 for Decisions sessions and 0
    (request immediately) for other sessions. Omission in a session update preserves
    the current value. Updates apply to subsequent delegations.
    """
