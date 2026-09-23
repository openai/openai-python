# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated, TypeAlias

from ..._utils import PropertyInfo
from .agent_mcp_call_item import AgentMcpCallItem
from .agent_reasoning_item import AgentReasoningItem
from .agent_function_call_item import AgentFunctionCallItem
from .agent_web_search_call_item import AgentWebSearchCallItem
from .agent_command_execution_item import AgentCommandExecutionItem
from .agent_close_subagent_call_item import AgentCloseSubagentCallItem
from .agent_create_subagent_call_item import AgentCreateSubagentCallItem
from .agent_resume_subagent_call_item import AgentResumeSubagentCallItem
from .agent_session_assistant_message import AgentSessionAssistantMessage
from .agent_interrupt_subagent_call_item import AgentInterruptSubagentCallItem
from .agent_wait_for_subagents_call_item import AgentWaitForSubagentsCallItem
from .agent_send_subagent_input_call_item import AgentSendSubagentInputCallItem

__all__ = ["AgentOutputItem"]

AgentOutputItem: TypeAlias = Annotated[
    Union[
        AgentSessionAssistantMessage,
        AgentReasoningItem,
        AgentFunctionCallItem,
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
