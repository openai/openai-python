# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .agent_function_call_status import AgentFunctionCallStatus

__all__ = ["AgentCommandExecutionItem"]


class AgentCommandExecutionItem(BaseModel):
    """A command execution produced by the agent."""

    id: str
    """The ID of the command execution item."""

    command: str
    """The command that was executed."""

    cwd: Optional[str] = None
    """The working directory used to execute the command."""

    duration_ms: Optional[int] = None
    """The command duration in milliseconds."""

    exit_code: Optional[int] = None
    """The process exit code, if the command completed."""

    output: Optional[str] = None
    """The command output, if available."""

    status: AgentFunctionCallStatus
    """The status of the command execution."""

    turn_id: str
    """The ID of the turn that contains this item."""

    type: Literal["command_execution"]
    """The item type. Always `command_execution`."""
