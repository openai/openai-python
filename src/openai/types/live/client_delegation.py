# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ClientDelegation"]


class ClientDelegation(BaseModel):
    """Delegate tasks to your application.

    The Live session emits delegation events that your backend handles.
    """

    type: Literal["client"]
    """The delegation owner. Always `client` for tasks handled by your application."""

    acknowledgement_delay_ms: Optional[int] = None
    """
    Milliseconds to wait before requesting an automatic spoken acknowledgement for a
    delegation. The model may still speak before this delay. Any commentary or
    thinking appended to the session cancels all pending acknowledgements, including
    those for other delegations. Defaults to 400 for Decisions sessions and 0
    (request immediately) for other sessions. Omission in a session update preserves
    the current value. Updates apply to subsequent delegations.
    """
