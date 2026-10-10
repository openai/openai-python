# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["AgentEnvironmentExpiredWebhookEvent", "Data"]


class Data(BaseModel):
    """Identifies the environment whose lifecycle changed."""

    id: str
    """The ID of the environment."""


class AgentEnvironmentExpiredWebhookEvent(BaseModel):
    """
    Sent when an agent environment expires and can no longer resume from a snapshot.
    """

    id: str
    """The unique ID of the event."""

    created_at: int
    """The Unix timestamp, in seconds, when the event was created."""

    data: Data
    """Identifies the environment whose lifecycle changed."""

    object: Literal["event"]
    """The object type. Always `event`."""

    type: Literal["agent.environment.expired"]
    """The event type. Always `agent.environment.expired`."""
