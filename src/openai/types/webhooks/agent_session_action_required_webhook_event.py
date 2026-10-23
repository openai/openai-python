# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["AgentSessionActionRequiredWebhookEvent", "Data", "DataRequiredAction"]


class DataRequiredAction(BaseModel):
    """The action type. Retrieve the session for action details."""

    type: Literal["computer_use_approval_request", "function_call", "environment_connection"]


class Data(BaseModel):
    id: str
    """The ID of the session."""

    required_action: DataRequiredAction
    """The action type. Retrieve the session for action details."""


class AgentSessionActionRequiredWebhookEvent(BaseModel):
    """Sent when an agent session requires an action.

    Retrieve the session for action details.
    """

    id: str
    """The unique ID of the event."""

    created_at: int
    """The Unix timestamp, in seconds, when the event was created."""

    data: Data

    object: Literal["event"]
    """The object type. Always `event`."""

    type: Literal["agent.session.action_required"]
    """The event type. Always `agent.session.action_required`."""
