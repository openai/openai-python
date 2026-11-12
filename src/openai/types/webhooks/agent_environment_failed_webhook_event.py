# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["AgentEnvironmentFailedWebhookEvent", "Data"]


class Data(BaseModel):
    """Identifies the environment whose lifecycle changed."""

    id: str
    """The ID of the environment."""


class AgentEnvironmentFailedWebhookEvent(BaseModel):
    """
    Sent when setup fails for a prewarmed OpenAI-hosted environment before it is attached to a session.
    """

    id: str
    """The unique ID of the event."""

    created_at: int
    """The Unix timestamp, in seconds, when the event was created."""

    data: Data
    """Identifies the environment whose lifecycle changed."""

    object: Literal["event"]
    """The object type. Always `event`."""

    type: Literal["agent.environment.failed"]
    """The event type. Always `agent.environment.failed`."""
