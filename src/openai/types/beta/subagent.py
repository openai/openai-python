# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .agent_content import AgentContent

__all__ = ["Subagent"]


class Subagent(BaseModel):
    """A subagent created within a session."""

    id: str
    """The ID of the subagent."""

    closed_at: Optional[int] = None
    """The Unix timestamp, in seconds, when the subagent was closed.

    Null while active, including after resume.
    """

    instructions: Optional[List[AgentContent]] = None
    """Initial task content, or null when unavailable.

    Text may contain placeholders for images or audio when only a preview is
    available.
    """

    name: Optional[str] = None
    """The runner-assigned nickname, or null when unavailable."""

    object: Literal["agent.session.subagent"]
    """The object type. Always `agent.session.subagent`."""

    opened_at: int
    """The Unix timestamp, in seconds, when the subagent was first opened.

    Resuming does not change it.
    """

    parent_agent_id: str
    """The ID of the agent that created this subagent."""

    session_id: str
    """The ID of the session that owns the subagent."""

    status: Literal["active", "closed"]
    """The current status of the subagent.

    - `active` - The subagent remains available, including while idle between turns.
    - `closed` - The subagent is closed.
    """
