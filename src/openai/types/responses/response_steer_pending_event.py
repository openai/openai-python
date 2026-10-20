# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .response_steer_pending_reason import ResponseSteerPendingReason
from .response_steer_required_input import ResponseSteerRequiredInput

__all__ = ["ResponseSteerPendingEvent", "Steer"]


class Steer(BaseModel):
    """The steering submission that remains queued."""

    id: str
    """The ID assigned to the steering submission."""

    previous_response_id: str
    """The ID of the response being steered."""


class ResponseSteerPendingEvent(BaseModel):
    """
    Emitted when accepted steering input remains queued after the target
    response completes. The server still owns the input. Do not resend it.
    The successor's `response.created` event is the commit point.

    When `reason` is `waiting_for_required_input`, this event follows
    `response.completed` while the response waits for the tool results or
    approval decisions identified by `required_input`. Copy those stubs, fill
    their result fields using the ordinary `response.create` input schemas,
    and submit one continuation per parent with the same `previous_response_id`
    and WebSocket lane. Use saved results without rerunning tools. The queued
    steering input is prepended in submission order to the continuation's
    input. That explicit request retains its own settings.

    This notification is emitted at most once per steering submission. Multiple
    submissions for the same parent can report the same required inputs; they
    do not each require a separate continuation.
    """

    reason: ResponseSteerPendingReason
    """
    An extensible enum describing why accepted steering input is still queued.
    Clients should handle unknown values because additional reasons may be
    introduced. Known values include:

    - `waiting_for_required_input`: The response is waiting for the tool results or
      approval decisions identified by `required_input`.
    """

    required_input: List[ResponseSteerRequiredInput]
    """
    Input stubs identifying outstanding client-owned tool results or approval
    decisions. Each stub contains identifying fields only; the client supplies the
    result before including it in `response.create`.
    """

    sequence_number: int
    """The sequence number for this event."""

    steer: Steer
    """The steering submission that remains queued."""

    type: Literal["response.steer.pending"]
    """The event discriminator. Always `response.steer.pending`."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the target response's `response.create` event
    supplied a `stream_id`.
    """
