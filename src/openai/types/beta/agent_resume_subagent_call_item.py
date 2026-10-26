# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel
from .agent_function_call_status import AgentFunctionCallStatus

__all__ = ["AgentResumeSubagentCallItem"]


class AgentResumeSubagentCallItem(BaseModel):
    """A request to resume a subagent."""

    id: str
    """The ID of the tool call item."""

    recipient_agent_id: str
    """The ID of the agent to resume."""

    sender_agent_id: str
    """The ID of the agent requesting the resume."""

    status: AgentFunctionCallStatus
    """The status of the tool call."""

    turn_id: str
    """The ID of the turn that contains this item."""

    type: Literal["resume_subagent_call"]
    """The item type. Always `resume_subagent_call`.

    - `resume_subagent_call` - The current public item type.
    """
