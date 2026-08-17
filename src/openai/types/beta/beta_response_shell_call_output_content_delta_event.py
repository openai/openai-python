# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["BetaResponseShellCallOutputContentDeltaEvent", "Delta", "Agent"]


class Delta(BaseModel):
    """The stdout/stderr delta that was emitted."""

    stderr: Optional[str] = None
    """The stderr delta that was emitted."""

    stdout: Optional[str] = None
    """The stdout delta that was emitted."""


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseShellCallOutputContentDeltaEvent(BaseModel):
    """A streaming event that indicated shell call output was incrementally added."""

    command_index: int
    """The index of the shell command that produced output."""

    delta: Delta
    """The stdout/stderr delta that was emitted."""

    item_id: str
    """The ID of the output item that was updated."""

    output_index: int
    """The index of the output item that was updated."""

    sequence_number: int
    """The sequence number of the event that was emitted."""

    type: Literal["response.shell_call_output_content.delta"]
    """The type of the event, always `response.shell_call_output_content.delta`."""

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
