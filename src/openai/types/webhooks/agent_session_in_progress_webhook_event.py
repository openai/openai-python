# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["AgentSessionInProgressWebhookEvent", "Data"]


class Data(BaseModel):
    id: str
    """The ID of the session."""

    environment_type: str
    """The environment type: `none`, `openai_hosted`, or `self_hosted`."""

    environment_id: Optional[str] = None
    """The ID of the environment, when one exists."""


class AgentSessionInProgressWebhookEvent(BaseModel):
    """Sent when an agent session enters the in-progress state."""

    id: str
    """The unique ID of the event."""

    created_at: int
    """The Unix timestamp, in seconds, when the event was created."""

    data: Data

    object: Literal["event"]
    """The object type. Always `event`."""

    type: Literal["agent.session.in_progress"]
    """The event type. Always `agent.session.in_progress`."""
