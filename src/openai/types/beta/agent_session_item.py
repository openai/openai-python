# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .agent_content import AgentContent
from .agent_mcp_call_item import AgentMcpCallItem
from .agent_reasoning_item import AgentReasoningItem
from .agent_session_message import AgentSessionMessage
from .agent_function_call_item import AgentFunctionCallItem
from .agent_function_call_output import AgentFunctionCallOutput
from .agent_function_call_status import AgentFunctionCallStatus
from .agent_web_search_call_item import AgentWebSearchCallItem
from .agent_command_execution_item import AgentCommandExecutionItem
from .agent_close_subagent_call_item import AgentCloseSubagentCallItem
from .agent_create_subagent_call_item import AgentCreateSubagentCallItem
from .agent_resume_subagent_call_item import AgentResumeSubagentCallItem
from .agent_interrupt_subagent_call_item import AgentInterruptSubagentCallItem
from .agent_wait_for_subagents_call_item import AgentWaitForSubagentsCallItem
from .agent_send_subagent_input_call_item import AgentSendSubagentInputCallItem

__all__ = ["AgentSessionItem", "FunctionCallOutputItemResource", "AgentMessageItemResource"]


class FunctionCallOutputItemResource(BaseModel):
    """The result supplied for a function call."""

    id: str
    """The ID of the function call output item."""

    call_id: str
    """The ID of the function call that produced this output."""

    error: Optional[str] = None
    """The error message, if the call failed."""

    output: Optional[AgentFunctionCallOutput] = None
    """The text or model-input content supplied as a function result."""

    status: AgentFunctionCallStatus
    """The status of the function call."""

    turn_id: str
    """The ID of the turn that contains this item."""

    type: Literal["function_call_output"]
    """The item type. Always `function_call_output`."""


class AgentMessageItemResource(BaseModel):
    """A message exchanged between agent threads."""

    id: str
    """The ID of the message."""

    content: List[AgentContent]
    """The content exchanged between the agents."""

    recipient_agent_id: str
    """The ID or name of the receiving agent."""

    sender_agent_id: str
    """The ID or name of the sending agent."""

    turn_id: str
    """The ID of the turn that contains this item."""

    type: Literal["agent_message"]
    """The item type. Always `agent_message`."""


AgentSessionItem: TypeAlias = Annotated[
    Union[
        AgentSessionMessage,
        AgentReasoningItem,
        AgentFunctionCallItem,
        FunctionCallOutputItemResource,
        AgentMessageItemResource,
        AgentMcpCallItem,
        AgentWebSearchCallItem,
        AgentCommandExecutionItem,
        AgentCreateSubagentCallItem,
        AgentSendSubagentInputCallItem,
        AgentResumeSubagentCallItem,
        AgentWaitForSubagentsCallItem,
        AgentInterruptSubagentCallItem,
        AgentCloseSubagentCallItem,
    ],
    PropertyInfo(discriminator="type"),
]
