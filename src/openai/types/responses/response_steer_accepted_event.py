# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseSteerAcceptedEvent", "Steer"]


class Steer(BaseModel):
    """The accepted steering submission."""

    id: str
    """The ID assigned to the steering submission."""

    previous_response_id: str
    """The ID of the response being steered."""


class ResponseSteerAcceptedEvent(BaseModel):
    """Emitted when steering input has been validated and queued.

    Acceptance means
    the server owns the input, not that it has been applied. The successor's
    `response.created` event is the commit point. If accepted input cannot be
    committed, `response.steer.failed` returns it with the same steering ID.

    When the response stops for client-owned tool output or approval, the input
    remains queued and `response.steer.pending` is emitted after
    `response.completed`. Fill the pending event's `required_input` stubs with
    saved results and send one matching explicit `response.create` per parent.
    Do not resend accepted input while it is still queued.
    """

    sequence_number: int
    """The sequence number for this event."""

    steer: Steer
    """The accepted steering submission."""

    type: Literal["response.steer.accepted"]
    """The event discriminator. Always `response.steer.accepted`."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the target response's `response.create` event
    supplied a `stream_id`.
    """
