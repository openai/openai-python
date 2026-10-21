# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["BetaResponseCodeInterpreterCallCodeDoneEvent", "Agent"]


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseCodeInterpreterCallCodeDoneEvent(BaseModel):
    """Emitted when the code snippet is finalized by the code interpreter."""

    code: str
    """The final code snippet output by the code interpreter."""

    item_id: str
    """The unique identifier of the code interpreter tool call item."""

    output_index: int
    """The index of the output item in the response for which the code is finalized."""

    sequence_number: int
    """The sequence number of this event, used to order streaming events."""

    type: Literal["response.code_interpreter_call_code.done"]
    """The type of the event. Always `response.code_interpreter_call_code.done`."""

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
