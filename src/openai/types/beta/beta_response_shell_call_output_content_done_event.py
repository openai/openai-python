# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel

__all__ = [
    "BetaResponseShellCallOutputContentDoneEvent",
    "Output",
    "OutputOutcome",
    "OutputOutcomeTimeout",
    "OutputOutcomeExit",
    "Agent",
]


class OutputOutcomeTimeout(BaseModel):
    """Indicates that the shell call exceeded its configured time limit."""

    type: Literal["timeout"]
    """The outcome type. Always `timeout`."""


class OutputOutcomeExit(BaseModel):
    """Indicates that the shell commands finished and returned an exit code."""

    exit_code: int
    """Exit code from the shell process."""

    type: Literal["exit"]
    """The outcome type. Always `exit`."""


OutputOutcome: TypeAlias = Annotated[Union[OutputOutcomeTimeout, OutputOutcomeExit], PropertyInfo(discriminator="type")]


class Output(BaseModel):
    """The content of a shell tool call output that was emitted."""

    outcome: OutputOutcome
    """
    Represents either an exit outcome (with an exit code) or a timeout outcome for a
    shell call output chunk.
    """

    stderr: str
    """The standard error output that was captured."""

    stdout: str
    """The standard output that was captured."""

    created_by: Optional[str] = None
    """The identifier of the actor that created the item."""


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseShellCallOutputContentDoneEvent(BaseModel):
    """A streaming event that indicated shell call output was completed."""

    command_index: int
    """The index of the shell command that produced output."""

    item_id: str
    """The ID of the output item that was updated."""

    output: List[Output]
    """The output contents emitted for the shell command."""

    output_index: int
    """The index of the output item that was updated."""

    sequence_number: int
    """The sequence number of the event that was emitted."""

    type: Literal["response.shell_call_output_content.done"]
    """The type of the event, always `response.shell_call_output_content.done`."""

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
