# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .agent_content import AgentContent
from .agent_function_call_status import AgentFunctionCallStatus

__all__ = ["AgentCreateSubagentCallItem"]


class AgentCreateSubagentCallItem(BaseModel):
    """A request to spawn a subagent."""

    id: str
    """The ID of the tool call item."""

    agent_id: str
    """The ID of the agent that requested the subagent."""

    content: List[AgentContent]
    """The task given to the spawned agent."""

    model: Optional[str] = None
    """The model requested for the spawned agent."""

    reasoning_effort: Optional[str] = None
    """The reasoning effort requested for the spawned agent."""

    status: AgentFunctionCallStatus
    """The status of the tool call."""

    turn_id: str
    """The ID of the turn that contains this item."""

    type: Literal["create_subagent_call"]
    """The item type. Always `create_subagent_call`.

    - `create_subagent_call` - The current public item type.
    """
