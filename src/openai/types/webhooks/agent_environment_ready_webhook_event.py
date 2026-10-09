# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["AgentEnvironmentReadyWebhookEvent", "Data"]


class Data(BaseModel):
    """Identifies the environment whose lifecycle changed."""

    id: str
    """The ID of the environment."""


class AgentEnvironmentReadyWebhookEvent(BaseModel):
    """
    Sent when a prewarmed OpenAI-hosted environment finishes setup before being attached to a session.
    """

    id: str
    """The unique ID of the event."""

    created_at: int
    """The Unix timestamp, in seconds, when the event was created."""

    data: Data
    """Identifies the environment whose lifecycle changed."""

    object: Literal["event"]
    """The object type. Always `event`."""

    type: Literal["agent.environment.ready"]
    """The event type. Always `agent.environment.ready`."""
