# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from ..._models import BaseModel
from .agent_content import AgentContent
from .agent_function_call_status import AgentFunctionCallStatus

__all__ = ["AgentSendSubagentInputCallItem"]


class AgentSendSubagentInputCallItem(BaseModel):
    """A request to send input to another agent."""

    id: str
    """The ID of the tool call item."""

    content: List[AgentContent]
    """The input sent to the receiving agent."""

    recipient_agent_id: str
    """The ID of the agent receiving the input."""

    sender_agent_id: str
    """The ID of the agent sending the input."""

    status: AgentFunctionCallStatus
    """The status of the tool call."""

    turn_id: str
    """The ID of the turn that contains this item."""

    type: Literal["send_subagent_input_call"]
    """The item type. Always `send_subagent_input_call`.

    - `send_subagent_input_call` - The current public item type.
    """
