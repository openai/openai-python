# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel
from .response_steer_input import ResponseSteerInput

__all__ = ["ResponseSteerEvent"]


class ResponseSteerEvent(BaseModel):
    """Queues user input to steer a response on this WebSocket connection.

    Input
    can contain text, images, and files. Steering is supported only for
    single-agent responses on models and execution modes that support steering.
    Responses bound to a conversation or using automatic compaction do not
    support steering.

    A `response.steer.accepted` event acknowledges that the server owns the
    queued input, not that it has been applied. The successor's `response.created`
    event is the commit point. Input that cannot be committed is returned in
    `response.steer.failed`.

    Steering may cause the active response to finish at a safe output boundary
    with `response.incomplete` and `incomplete_details.reason` set to `steered`,
    followed automatically by a successor `response.created`. Normal completion
    can also be followed by an automatic successor. Automatic successors inherit
    the previous response's settings and continue from it with the queued input.

    If the response stops for client-owned tool output or approval, accepted
    steering input remains queued and `response.steer.pending` is emitted after
    `response.completed`. Fill the `required_input` stubs from that event with
    saved tool results or approval decisions, and send one explicit
    `response.create` per parent with the same `previous_response_id` and
    WebSocket lane. Do not rerun tools or resend accepted steering input. The
    queued input is prepended in submission order to that request's input, and
    the explicit request retains its own settings.

    This event accepts only `type`, `previous_response_id`, and `input`. Do not
    send `stream_id`; the target response determines the WebSocket lane.
    """

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
    """The ID of the response to steer on this WebSocket connection."""

    type: Literal["response.steer"]
    """The event discriminator. Always `response.steer`."""
