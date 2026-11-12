# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["DelegationCreatedEvent", "Delegation"]


class Delegation(BaseModel):
    """The delegated work identifier and destination.

    This object contains metadata, not the task text.
    """

    id: str
    """The unique ID of the delegation.

    Use this as delegation_id when replying to client-owned work or correlating
    backend events.
    """

    target: Literal["client", "responses", "decisions"]
    """Where the Live model delegated the work: `client`, `responses`, or `decisions`."""

    type: Literal["delegation"]
    """The object type, always `delegation`."""

    response_id: Optional[str] = None
    """The ID of the Responses API response associated with a Responses delegation.

    Omitted for client delegations.
    """


class DelegationCreatedEvent(BaseModel):
    """
    Returned when the Live model delegates work to your application, Responses, or Decisions. Contains delegation metadata and the position on the session timeline where the work was delegated.
    """

    delegation: Delegation
    """The delegated work identifier and destination.

    This object contains metadata, not the task text.
    """

    event_id: str
    """The unique ID of the Live server event."""

    offset_ms: int
    """
    The position on the Live session timeline where the delegation was created, in
    milliseconds from the beginning of the session.
    """

    type: Literal["session.delegation.created"]
    """The event type, always `session.delegation.created`."""

    client_event_id: Optional[str] = None
    """
    The event_id of the client command associated with this server event, when
    supplied.
    """
