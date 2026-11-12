# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from ..decision import Decision

__all__ = ["DecisionEvent", "Event"]


class Event(BaseModel):
    decision: Decision
    """
    The native Decision API response, including its model, ordered answers, and
    token usage.
    """

    type: Literal["decision.completed"]


class DecisionEvent(BaseModel):
    """A Decision API event for a Live delegation or transcript trigger.

    For a trigger, source_event_id identifies the transcript delta that caused this evaluation.
    """

    delegation_id: Optional[str] = None
    """The Live delegation ID, or null for a transcript trigger."""

    event: Event

    event_id: str
    """The unique ID of this Live server event."""

    source_event_id: Optional[str] = None
    """
    The event_id of the transcript delta that fired this trigger, or null for a
    delegation.
    """

    source_event_type: Union[Literal["session.input_transcript.delta", "session.output_transcript.delta"], None] = None

    trigger_id: Optional[str] = None
    """The Live-assigned ID of this trigger firing, or null for a delegation."""

    type: Literal["decision.event"]
