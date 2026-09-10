# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseShellCallCommandDeltaEvent"]


class ResponseShellCallCommandDeltaEvent(BaseModel):
    """A streaming event that indicated a shell command was incrementally updated."""

    command_index: int
    """The index of the shell command that was updated."""

    delta: str
    """The shell command delta that was appended."""

    output_index: int
    """The index of the output item that was updated."""

    sequence_number: int
    """The sequence number of the event that was emitted."""

    type: Literal["response.shell_call_command.delta"]
    """The type of the event, always `response.shell_call_command.delta`."""

    obfuscation: Optional[str] = None
    """An obfuscation string that was added to pad the event payload."""
