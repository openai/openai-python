# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .beta_tool import BetaTool
from .beta_response_input_file import BetaResponseInputFile
from .beta_response_input_text import BetaResponseInputText
from .beta_response_input_image import BetaResponseInputImage
from .beta_response_output_text import BetaResponseOutputText
from .beta_response_output_message import BetaResponseOutputMessage
from .beta_response_output_refusal import BetaResponseOutputRefusal
from .beta_response_reasoning_item import BetaResponseReasoningItem
from .beta_response_compaction_item import BetaResponseCompactionItem
from .beta_response_custom_tool_call import BetaResponseCustomToolCall
from .beta_response_tool_search_call import BetaResponseToolSearchCall
from .beta_response_computer_tool_call import BetaResponseComputerToolCall
from .beta_response_function_tool_call import BetaResponseFunctionToolCall
from .beta_response_function_web_search import BetaResponseFunctionWebSearch
from .beta_response_apply_patch_tool_call import BetaResponseApplyPatchToolCall
from .beta_response_file_search_tool_call import BetaResponseFileSearchToolCall
from .beta_response_tool_search_output_item import BetaResponseToolSearchOutputItem
from .beta_response_function_shell_tool_call import BetaResponseFunctionShellToolCall
from .beta_response_code_interpreter_tool_call import BetaResponseCodeInterpreterToolCall
from .beta_response_apply_patch_tool_call_output import BetaResponseApplyPatchToolCallOutput
from .beta_response_custom_tool_call_output_item import BetaResponseCustomToolCallOutputItem
from .beta_response_computer_tool_call_output_item import BetaResponseComputerToolCallOutputItem
from .beta_response_function_tool_call_output_item import BetaResponseFunctionToolCallOutputItem
from .beta_response_function_shell_tool_call_output import BetaResponseFunctionShellToolCallOutput

__all__ = [
    "BetaResponseOutputItem",
    "AgentMessage",
    "AgentMessageContent",
    "AgentMessageContentText",
    "AgentMessageContentSummaryText",
    "AgentMessageContentReasoningText",
    "AgentMessageContentComputerScreenshot",
    "AgentMessageContentComputerScreenshotPromptCacheBreakpoint",
    "AgentMessageContentEncryptedContent",
    "AgentMessageAgent",
    "MultiAgentCall",
    "MultiAgentCallAgent",
    "MultiAgentCallOutput",
    "MultiAgentCallOutputAgent",
    "Program",
    "ProgramAgent",
    "ProgramOutput",
    "ProgramOutputAgent",
    "AdditionalTools",
    "AdditionalToolsAgent",
    "ImageGenerationCall",
    "ImageGenerationCallAgent",
    "LocalShellCall",
    "LocalShellCallAction",
    "LocalShellCallAgent",
    "LocalShellCallOutput",
    "LocalShellCallOutputAgent",
    "McpCall",
    "McpCallAgent",
    "McpListTools",
    "McpListToolsTool",
    "McpListToolsAgent",
    "McpApprovalRequest",
    "McpApprovalRequestAgent",
    "McpApprovalResponse",
    "McpApprovalResponseAgent",
]


class AgentMessageContentText(BaseModel):
    """A text content."""

    text: str

    type: Literal["text"]


class AgentMessageContentSummaryText(BaseModel):
    """A summary text from the model."""

    text: str
    """A summary of the reasoning output from the model so far."""

    type: Literal["summary_text"]
    """The type of the object. Always `summary_text`."""


class AgentMessageContentReasoningText(BaseModel):
    """Reasoning text from the model."""

    text: str
    """The reasoning text from the model."""

    type: Literal["reasoning_text"]
    """The type of the reasoning text. Always `reasoning_text`."""


class AgentMessageContentComputerScreenshotPromptCacheBreakpoint(BaseModel):
    """Marks the exact end of a reusable prompt prefix.

    The breakpoint inherits its TTL from the request's `prompt_cache_options.ttl`; the boundary is not rounded to a token block.
    """

    mode: Literal["explicit"]
    """The breakpoint mode. Always `explicit`."""


class AgentMessageContentComputerScreenshot(BaseModel):
    """A screenshot of a computer."""

    detail: Literal["low", "high", "auto", "original"]
    """The detail level of the screenshot image to be sent to the model.

    One of `high`, `low`, `auto`, or `original`. Defaults to `auto`.
    """

    file_id: Optional[str] = None
    """The identifier of an uploaded file that contains the screenshot."""

    image_url: Optional[str] = None
    """The URL of the screenshot image."""

    type: Literal["computer_screenshot"]
    """Specifies the event type.

    For a computer screenshot, this property is always set to `computer_screenshot`.
    """

    prompt_cache_breakpoint: Optional[AgentMessageContentComputerScreenshotPromptCacheBreakpoint] = None
    """Marks the exact end of a reusable prompt prefix.

    The breakpoint inherits its TTL from the request's `prompt_cache_options.ttl`;
    the boundary is not rounded to a token block.
    """


class AgentMessageContentEncryptedContent(BaseModel):
    """
    Opaque encrypted content that Responses API decrypts inside trusted model execution.
    """

    encrypted_content: str
    """Opaque encrypted content."""

    type: Literal["encrypted_content"]
    """The type of the input item. Always `encrypted_content`."""


AgentMessageContent: TypeAlias = Annotated[
    Union[
        BetaResponseInputText,
        BetaResponseOutputText,
        AgentMessageContentText,
        AgentMessageContentSummaryText,
        AgentMessageContentReasoningText,
        BetaResponseOutputRefusal,
        BetaResponseInputImage,
        AgentMessageContentComputerScreenshot,
        BetaResponseInputFile,
        AgentMessageContentEncryptedContent,
    ],
    PropertyInfo(discriminator="type"),
]


class AgentMessageAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class AgentMessage(BaseModel):
    id: str
    """The unique ID of the agent message."""

    author: str
    """The sending agent identity."""

    content: List[AgentMessageContent]
    """Encrypted content sent between agents."""

    recipient: str
    """The destination agent identity."""

    type: Literal["agent_message"]
    """The type of the item. Always `agent_message`."""

    agent: Optional[AgentMessageAgent] = None
    """The agent that produced this item."""


class MultiAgentCallAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class MultiAgentCall(BaseModel):
    id: str
    """The unique ID of the multi-agent call item."""

    action: Literal["spawn_agent", "interrupt_agent", "list_agents", "send_message", "followup_task", "wait_agent"]
    """The multi-agent action to execute."""

    arguments: str
    """The JSON string of arguments generated for the action."""

    call_id: str
    """The unique ID linking this call to its output."""

    type: Literal["multi_agent_call"]
    """The type of the multi-agent call. Always `multi_agent_call`."""

    agent: Optional[MultiAgentCallAgent] = None
    """The agent that produced this item."""


class MultiAgentCallOutputAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class MultiAgentCallOutput(BaseModel):
    id: str
    """The unique ID of the multi-agent call output item."""

    action: Literal["spawn_agent", "interrupt_agent", "list_agents", "send_message", "followup_task", "wait_agent"]
    """The multi-agent action that produced this result."""

    call_id: str
    """The unique ID of the multi-agent call."""

    output: List[BetaResponseOutputText]
    """Text output returned by the multi-agent action."""

    type: Literal["multi_agent_call_output"]
    """The type of the multi-agent result. Always `multi_agent_call_output`."""

    agent: Optional[MultiAgentCallOutputAgent] = None
    """The agent that produced this item."""


class ProgramAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class Program(BaseModel):
    id: str
    """The unique ID of the program item."""

    call_id: str
    """The stable call ID of the program item."""

    code: str
    """The JavaScript source executed by programmatic tool calling."""

    fingerprint: str
    """Opaque program replay fingerprint that must be round-tripped."""

    type: Literal["program"]
    """The type of the item. Always `program`."""

    agent: Optional[ProgramAgent] = None
    """The agent that produced this item."""


class ProgramOutputAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class ProgramOutput(BaseModel):
    id: str
    """The unique ID of the program output item."""

    call_id: str
    """The call ID of the program item."""

    result: str
    """The result produced by the program item."""

    status: Literal["completed", "incomplete"]
    """The terminal status of the program output item."""

    type: Literal["program_output"]
    """The type of the item. Always `program_output`."""

    agent: Optional[ProgramOutputAgent] = None
    """The agent that produced this item."""


class AdditionalToolsAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class AdditionalTools(BaseModel):
    id: str
    """The unique ID of the additional tools item."""

    role: Literal["unknown", "user", "assistant", "system", "critic", "discriminator", "developer", "tool"]
    """The role that provided the additional tools."""

    tools: List[BetaTool]
    """The additional tool definitions made available at this item."""

    type: Literal["additional_tools"]
    """The type of the item. Always `additional_tools`."""

    agent: Optional[AdditionalToolsAgent] = None
    """The agent that produced this item."""


class ImageGenerationCallAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class ImageGenerationCall(BaseModel):
    """An image generation request made by the model."""

    id: str
    """The unique ID of the image generation call."""

    result: Optional[str] = None
    """The generated image encoded in base64."""

    status: Literal["in_progress", "completed", "generating", "failed"]
    """The status of the image generation call."""

    type: Literal["image_generation_call"]
    """The type of the image generation call. Always `image_generation_call`."""

    agent: Optional[ImageGenerationCallAgent] = None
    """The agent that produced this item."""


class LocalShellCallAction(BaseModel):
    """Execute a shell command on the server."""

    command: List[str]
    """The command to run."""

    env: Dict[str, str]
    """Environment variables to set for the command."""

    type: Literal["exec"]
    """The type of the local shell action. Always `exec`."""

    timeout_ms: Optional[int] = None
    """Optional timeout in milliseconds for the command."""

    user: Optional[str] = None
    """Optional user to run the command as."""

    working_directory: Optional[str] = None
    """Optional working directory to run the command in."""


class LocalShellCallAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class LocalShellCall(BaseModel):
    """A tool call to run a command on the local shell."""

    id: str
    """The unique ID of the local shell call."""

    action: LocalShellCallAction
    """Execute a shell command on the server."""

    call_id: str
    """The unique ID of the local shell tool call generated by the model."""

    status: Literal["in_progress", "completed", "incomplete"]
    """The status of the local shell call."""

    type: Literal["local_shell_call"]
    """The type of the local shell call. Always `local_shell_call`."""

    agent: Optional[LocalShellCallAgent] = None
    """The agent that produced this item."""


class LocalShellCallOutputAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class LocalShellCallOutput(BaseModel):
    """The output of a local shell tool call."""

    id: str
    """The unique ID of the local shell tool call generated by the model."""

    output: str
    """A JSON string of the output of the local shell tool call."""

    type: Literal["local_shell_call_output"]
    """The type of the local shell tool call output. Always `local_shell_call_output`."""

    agent: Optional[LocalShellCallOutputAgent] = None
    """The agent that produced this item."""

    status: Optional[Literal["in_progress", "completed", "incomplete"]] = None
    """The status of the item. One of `in_progress`, `completed`, or `incomplete`."""


class McpCallAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class McpCall(BaseModel):
    """An invocation of a tool on an MCP server."""

    id: str
    """The unique ID of the tool call."""

    arguments: str
    """A JSON string of the arguments passed to the tool."""

    name: str
    """The name of the tool that was run."""

    server_label: str
    """The label of the MCP server running the tool."""

    type: Literal["mcp_call"]
    """The type of the item. Always `mcp_call`."""

    agent: Optional[McpCallAgent] = None
    """The agent that produced this item."""

    approval_request_id: Optional[str] = None
    """
    Unique identifier for the MCP tool call approval request. Include this value in
    a subsequent `mcp_approval_response` input to approve or reject the
    corresponding tool call.
    """

    error: Optional[str] = None
    """The error from the tool call, if any."""

    output: Optional[str] = None
    """The output from the tool call."""

    status: Optional[Literal["in_progress", "completed", "incomplete", "calling", "failed"]] = None
    """The status of the tool call.

    One of `in_progress`, `completed`, `incomplete`, `calling`, or `failed`.
    """


class McpListToolsTool(BaseModel):
    """A tool available on an MCP server."""

    input_schema: object
    """The JSON schema describing the tool's input."""

    name: str
    """The name of the tool."""

    annotations: Optional[object] = None
    """Additional annotations about the tool."""

    description: Optional[str] = None
    """The description of the tool."""


class McpListToolsAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class McpListTools(BaseModel):
    """A list of tools available on an MCP server."""

    id: str
    """The unique ID of the list."""

    server_label: str
    """The label of the MCP server."""

    tools: List[McpListToolsTool]
    """The tools available on the server."""

    type: Literal["mcp_list_tools"]
    """The type of the item. Always `mcp_list_tools`."""

    agent: Optional[McpListToolsAgent] = None
    """The agent that produced this item."""

    error: Optional[str] = None
    """Error message if the server could not list tools."""


class McpApprovalRequestAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class McpApprovalRequest(BaseModel):
    """A request for human approval of a tool invocation."""

    id: str
    """The unique ID of the approval request."""

    arguments: str
    """A JSON string of arguments for the tool."""

    name: str
    """The name of the tool to run."""

    server_label: str
    """The label of the MCP server making the request."""

    type: Literal["mcp_approval_request"]
    """The type of the item. Always `mcp_approval_request`."""

    agent: Optional[McpApprovalRequestAgent] = None
    """The agent that produced this item."""


class McpApprovalResponseAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class McpApprovalResponse(BaseModel):
    """A response to an MCP approval request."""

    id: str
    """The unique ID of the approval response"""

    approval_request_id: str
    """The ID of the approval request being answered."""

    approve: bool
    """Whether the request was approved."""

    type: Literal["mcp_approval_response"]
    """The type of the item. Always `mcp_approval_response`."""

    agent: Optional[McpApprovalResponseAgent] = None
    """The agent that produced this item."""

    reason: Optional[str] = None
    """Optional reason for the decision."""


BetaResponseOutputItem: TypeAlias = Annotated[
    Union[
        BetaResponseOutputMessage,
        BetaResponseFileSearchToolCall,
        BetaResponseFunctionToolCall,
        BetaResponseFunctionToolCallOutputItem,
        AgentMessage,
        MultiAgentCall,
        MultiAgentCallOutput,
        BetaResponseFunctionWebSearch,
        BetaResponseComputerToolCall,
        BetaResponseComputerToolCallOutputItem,
        BetaResponseReasoningItem,
        Program,
        ProgramOutput,
        BetaResponseToolSearchCall,
        BetaResponseToolSearchOutputItem,
        AdditionalTools,
        BetaResponseCompactionItem,
        ImageGenerationCall,
        BetaResponseCodeInterpreterToolCall,
        LocalShellCall,
        LocalShellCallOutput,
        BetaResponseFunctionShellToolCall,
        BetaResponseFunctionShellToolCallOutput,
        BetaResponseApplyPatchToolCall,
        BetaResponseApplyPatchToolCallOutput,
        McpCall,
        McpListTools,
        McpApprovalRequest,
        McpApprovalResponse,
        BetaResponseCustomToolCall,
        BetaResponseCustomToolCallOutputItem,
    ],
    PropertyInfo(discriminator="type"),
]
