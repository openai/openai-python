# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["AgentSessionCreatedWebhookEvent", "Data", "DataConnect"]


class DataConnect(BaseModel):
    remote_url: str
    """The URL used to connect the self-hosted environment."""


class Data(BaseModel):
    id: str
    """The ID of the session."""

    environment_type: str
    """The environment type: `none`, `openai_hosted`, or `self_hosted`."""

    connect: Optional[DataConnect] = None

    environment_id: Optional[str] = None
    """The ID of the environment, when one exists."""


class AgentSessionCreatedWebhookEvent(BaseModel):
    """Sent when an agent session is created."""

    id: str
    """The unique ID of the event."""

    created_at: int
    """The Unix timestamp, in seconds, when the event was created."""

    data: Data

    object: Literal["event"]
    """The object type. Always `event`."""

    type: Literal["agent.session.created"]
    """The event type. Always `agent.session.created`."""
