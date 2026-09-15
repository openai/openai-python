# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["AgentOutputCommandExecutionOutputDeltaEvent"]


class AgentOutputCommandExecutionOutputDeltaEvent(BaseModel):
    """Emitted when command execution produces an output delta."""

    delta: str
    """The output text that was appended."""

    event_id: str
    """The unique ID of the event."""

    item_id: str
    """The ID of the command execution item."""

    output_index: int
    """The index of the item in the turn output."""

    session_id: str
    """The ID of the session associated with the event."""

    turn_id: Optional[str] = None
    """The ID of the turn associated with the event, when applicable."""

    type: Literal["agent.output.command_execution_output.delta"]
    """The type of the object. Always `agent.output.command_execution_output.delta`."""
