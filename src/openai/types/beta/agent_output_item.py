# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .agent_mcp_call_item import AgentMcpCallItem
from .agent_reasoning_item import AgentReasoningItem
from .agent_function_call_item import AgentFunctionCallItem
from .agent_function_call_status import AgentFunctionCallStatus
from .agent_web_search_call_item import AgentWebSearchCallItem
from .agent_command_execution_item import AgentCommandExecutionItem
from .agent_close_subagent_call_item import AgentCloseSubagentCallItem
from .agent_create_subagent_call_item import AgentCreateSubagentCallItem
from .agent_resume_subagent_call_item import AgentResumeSubagentCallItem
from .agent_session_assistant_message import AgentSessionAssistantMessage
from .agent_interrupt_subagent_call_item import AgentInterruptSubagentCallItem
from .agent_wait_for_subagents_call_item import AgentWaitForSubagentsCallItem
from .agent_send_subagent_input_call_item import AgentSendSubagentInputCallItem

__all__ = [
    "AgentOutputItem",
    "ComputerUseCallItemResource",
    "ComputerUseCallItemResourceOutput",
    "BrowserAuthenticationRequestItemResource",
    "BrowserAuthenticationRequestItemResourceRequest",
    "BrowserAuthenticationRequestItemResourceRequestField",
    "BrowserAuthenticationRequestItemResourceRequestOption",
]


class ComputerUseCallItemResourceOutput(BaseModel):
    """The last screenshot emitted by the model.

    Null when screenshot inclusion is disabled or the call emitted no screenshot.
    """

    image_url: str
    """The complete JPEG image as a base64 data URL."""

    type: Literal["computer_screenshot"]
    """The content type. Always `computer_screenshot`."""


class ComputerUseCallItemResource(BaseModel):
    """One execution of the platform-provided computer-use capability."""

    id: str
    """The ID of the activity item."""

    output: Optional[ComputerUseCallItemResourceOutput] = None
    """The last screenshot emitted by the model.

    Null when screenshot inclusion is disabled or the call emitted no screenshot.
    """

    status: AgentFunctionCallStatus
    """The execution status of the activity."""

    title: Optional[str] = None
    """A model-generated description of the activity, when available."""

    turn_id: str
    """The ID of the turn that contains this item."""

    type: Literal["computer_use_call"]
    """The item type. Always `computer_use_call`."""


class BrowserAuthenticationRequestItemResourceRequestField(BaseModel):
    """A control in a registered browser-login form."""

    id: str
    """The field ID to submit as field_id in a fields entry."""

    label: str
    """The label to display beside the control."""

    required: bool
    """Whether this control requires a nonempty value."""

    type: str
    """The rendering type, such as email, password, or text."""


class BrowserAuthenticationRequestItemResourceRequestOption(BaseModel):
    """A sign-in method and the fields that belong to it."""

    id: str
    """The option ID to submit as selected_option."""

    field_ids: List[str]
    """IDs from the registered fields that this method accepts."""

    label: str
    """The method label to display."""


class BrowserAuthenticationRequestItemResourceRequest(BaseModel):
    """A registered form awaiting the application's response."""

    credential_origin: Optional[str] = None
    """The registered form or frame origin where values will be entered."""

    fields: List[BrowserAuthenticationRequestItemResourceRequestField]
    """Controls to render. All submitted values are sensitive."""

    options: List[BrowserAuthenticationRequestItemResourceRequestOption]
    """Sign-in methods. Empty for a plain form."""

    reason: Optional[str] = None
    """Why the agent needs the user to sign in."""

    type: Literal["browser_authentication"]
    """The type of the object. Always `browser_authentication`."""


class BrowserAuthenticationRequestItemResource(BaseModel):
    """A credential-free history record of the emitted login request."""

    id: str
    """The stable history item ID."""

    request: BrowserAuthenticationRequestItemResourceRequest
    """A registered form awaiting the application's response."""

    request_id: str

    turn_id: str

    type: Literal["computer_use_approval_request"]
    """The item type. Always computer_use_approval_request."""


AgentOutputItem: TypeAlias = Annotated[
    Union[
        AgentSessionAssistantMessage,
        AgentReasoningItem,
        AgentFunctionCallItem,
        AgentMcpCallItem,
        ComputerUseCallItemResource,
        BrowserAuthenticationRequestItemResource,
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
