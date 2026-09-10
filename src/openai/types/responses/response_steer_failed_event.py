# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .response_steer_input import ResponseSteerInput
from .response_steer_error_code import ResponseSteerErrorCode

__all__ = ["ResponseSteerFailedEvent", "Error", "Steer"]


class Error(BaseModel):
    """Information about why the input could not be committed."""

    code: ResponseSteerErrorCode
    """A machine-readable steering error code.

    Clients should handle unknown values because additional codes may be introduced.
    Known values include:

    - `response_not_found`: The target response is not available on this connection.
    - `invalid_input`: The event or input failed validation.
    - `steering_not_supported`: The model or response execution mode does not
      support steering.
    - `too_many_pending_steers`: Too much steering input is pending for the
      response.
    - `response_already_completed`: The response completed and is no longer
      accepting steering input.
    - `response_not_active`: The response is no longer accepting steering input.
    - `successor_creation_failed`: The successor response could not be created.
    """

    message: str
    """A human-readable description of the error."""

    type: Literal["invalid_request_error"]
    """The error type. Always `invalid_request_error`."""


class Steer(BaseModel):
    """The steering submission that could not be committed."""

    input: ResponseSteerInput
    """Input to queue for a continuation of the response.

    Uses the same string or input-item shape as `response.create.input`, with a
    non-empty array when supplying input items.

    Steering accepts only messages with the `user` role. Each message may contain
    only `type`, `role`, and `content`, with `content` as a string or an array of
    `input_text`, `input_image`, and `input_file` parts. The optional `type` must be
    `message`. Other roles, tool outputs, and item types are not supported for
    steering.
    """

    previous_response_id: str
    """The ID of the response that was targeted for steering."""

    id: Optional[str] = None
    """The ID assigned to the steering submission, if one was allocated."""


class ResponseSteerFailedEvent(BaseModel):
    """
    Emitted when steering input is rejected or cannot be committed to a
    successor response. Returns the original, uncommitted input so the client
    can carry it into `response.create` when appropriate. Invalid input must
    be corrected before retrying.

    Failures after acceptance include the same steering ID. Failures before an
    ID is allocated omit `steer.id`. A lost connection or missing acknowledgement
    leaves the outcome unknown; it is not proof that the input was rejected.
    """

    error: Error
    """Information about why the input could not be committed."""

    sequence_number: int
    """The sequence number for this event."""

    steer: Steer
    """The steering submission that could not be committed."""

    type: Literal["response.steer.failed"]
    """The event discriminator. Always `response.steer.failed`."""

    stream_id: Optional[str] = None
    """
    The WebSocket lane that emitted this event, when the target response is
    available and its `response.create` event supplied a `stream_id`.
    """
