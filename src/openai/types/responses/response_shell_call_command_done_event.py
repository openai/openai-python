# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseShellCallCommandDoneEvent"]


class ResponseShellCallCommandDoneEvent(BaseModel):
    """A streaming event that indicated a shell command was completed."""

    command: str
    """The final shell command that was emitted."""

    command_index: int
    """The index of the shell command that was completed."""

    output_index: int
    """The index of the output item that was updated."""

    sequence_number: int
    """The sequence number of the event that was emitted."""

    type: Literal["response.shell_call_command.done"]
    """The type of the event, always `response.shell_call_command.done`."""
