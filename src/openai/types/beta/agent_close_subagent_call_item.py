# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel
from .agent_function_call_status import AgentFunctionCallStatus

__all__ = ["AgentCloseSubagentCallItem"]


class AgentCloseSubagentCallItem(BaseModel):
    """A request to close a subagent."""

    id: str
    """The ID of the tool call item."""

    recipient_agent_id: str
    """The ID of the agent to close."""

    sender_agent_id: str
    """The ID of the agent requesting the close."""

    status: AgentFunctionCallStatus
    """The status of the tool call."""

    turn_id: str
    """The ID of the turn that contains this item."""

    type: Literal["close_subagent_call"]
    """The item type. Always `close_subagent_call`.

    - `close_subagent_call` - The current public item type.
    """
