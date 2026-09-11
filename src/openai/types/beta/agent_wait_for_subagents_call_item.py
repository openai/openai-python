# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from ..._models import BaseModel
from .agent_function_call_status import AgentFunctionCallStatus

__all__ = ["AgentWaitForSubagentsCallItem"]


class AgentWaitForSubagentsCallItem(BaseModel):
    """A request to wait for one or more subagents."""

    id: str
    """The ID of the tool call item."""

    recipient_agent_ids: List[str]
    """The IDs of the agents to wait for."""

    sender_agent_id: str
    """The ID of the agent waiting for results."""

    status: AgentFunctionCallStatus
    """The status of the tool call."""

    turn_id: str
    """The ID of the turn that contains this item."""

    type: Literal["wait_for_subagents_call"]
    """The item type. Always `wait_for_subagents_call`.

    - `wait_for_subagents_call` - The current public item type.
    """
