# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel
from .agent_function_call_status import AgentFunctionCallStatus

__all__ = ["AgentInterruptSubagentCallItem"]


class AgentInterruptSubagentCallItem(BaseModel):
    """A request to interrupt a subagent's current turn.

    The subagent remains available.
    """

    id: str
    """The ID of the tool call item."""

    recipient_agent_id: str
    """The ID of the agent to interrupt."""

    sender_agent_id: str
    """The ID of the agent requesting the interrupt."""

    status: AgentFunctionCallStatus
    """The status of the tool call."""

    turn_id: str
    """The ID of the turn that contains this item."""

    type: Literal["interrupt_subagent_call"]
    """The item type. Always `interrupt_subagent_call`.

    - `interrupt_subagent_call` - The current public item type.
    """
