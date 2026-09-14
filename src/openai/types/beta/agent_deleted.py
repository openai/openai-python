# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["AgentDeleted"]


class AgentDeleted(BaseModel):
    """A deleted reusable agent."""

    id: str
    """The ID of the deleted agent."""

    deleted: bool
    """Whether the agent was deleted. Always `true`."""

    object: Literal["agent.deleted"]
    """The object type. Always `agent.deleted`."""
