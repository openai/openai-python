# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["BetaResponseShellCallCommandAddedEvent", "Agent"]


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseShellCallCommandAddedEvent(BaseModel):
    """A streaming event that indicated a shell command was added to a tool call."""

    command: str
    """The shell command that was added."""

    command_index: int
    """The index of the shell command that was added."""

    output_index: int
    """The index of the output item that was updated."""

    sequence_number: int
    """The sequence number of the event that was emitted."""

    type: Literal["response.shell_call_command.added"]
    """The type of the event, always `response.shell_call_command.added`."""

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
