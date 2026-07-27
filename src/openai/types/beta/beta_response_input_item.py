# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .beta_tool import BetaTool
from .beta_local_environment import BetaLocalEnvironment
from .beta_easy_input_message import BetaEasyInputMessage
from .beta_container_reference import BetaContainerReference
from .beta_response_output_message import BetaResponseOutputMessage
from .beta_response_reasoning_item import BetaResponseReasoningItem
from .beta_response_custom_tool_call import BetaResponseCustomToolCall
from .beta_response_computer_tool_call import BetaResponseComputerToolCall
from .beta_response_function_tool_call import BetaResponseFunctionToolCall
from .beta_response_input_text_content import BetaResponseInputTextContent
from .beta_response_function_web_search import BetaResponseFunctionWebSearch
from .beta_response_input_image_content import BetaResponseInputImageContent
from .beta_response_compaction_item_param import BetaResponseCompactionItemParam
from .beta_response_file_search_tool_call import BetaResponseFileSearchToolCall
from .beta_response_custom_tool_call_output import BetaResponseCustomToolCallOutput
from .beta_response_code_interpreter_tool_call import BetaResponseCodeInterpreterToolCall
from .beta_response_input_message_content_list import BetaResponseInputMessageContentList
from .beta_response_tool_search_output_item_param import BetaResponseToolSearchOutputItemParam
from .beta_response_function_call_output_item_list import BetaResponseFunctionCallOutputItemList
from .beta_response_function_shell_call_output_content import BetaResponseFunctionShellCallOutputContent
from .beta_response_computer_tool_call_output_screenshot import BetaResponseComputerToolCallOutputScreenshot

__all__ = [
    "BetaResponseInputItem",
    "Message",
    "MessageAgent",
    "ComputerCallOutput",
    "ComputerCallOutputAcknowledgedSafetyCheck",
    "ComputerCallOutputAgent",
    "FunctionCallOutput",
    "FunctionCallOutputAgent",
    "FunctionCallOutputCaller",
    "FunctionCallOutputCallerDirect",
    "FunctionCallOutputCallerProgram",
    "AgentMessage",
    "AgentMessageContent",
    "AgentMessageContentEncryptedContent",
    "AgentMessageAgent",
    "MultiAgentCall",
    "MultiAgentCallAgent",
    "MultiAgentCallOutput",
    "MultiAgentCallOutputOutput",
    "MultiAgentCallOutputOutputAnnotation",
    "MultiAgentCallOutputOutputAnnotationFileCitation",
    "MultiAgentCallOutputOutputAnnotationURLCitation",
    "MultiAgentCallOutputOutputAnnotationContainerFileCitation",
    "MultiAgentCallOutputAgent",
    "ToolSearchCall",
    "ToolSearchCallAgent",
    "AdditionalTools",
    "AdditionalToolsAgent",
    "ImageGenerationCall",
    "ImageGenerationCallAgent",
    "LocalShellCall",
    "LocalShellCallAction",
    "LocalShellCallAgent",
    "LocalShellCallOutput",
    "LocalShellCallOutputAgent",
    "ShellCall",
    "ShellCallAction",
    "ShellCallAgent",
    "ShellCallCaller",
    "ShellCallCallerDirect",
    "ShellCallCallerProgram",
    "ShellCallEnvironment",
    "ShellCallOutput",
    "ShellCallOutputAgent",
    "ShellCallOutputCaller",
    "ShellCallOutputCallerDirect",
    "ShellCallOutputCallerProgram",
    "ApplyPatchCall",
    "ApplyPatchCallOperation",
    "ApplyPatchCallOperationCreateFile",
    "ApplyPatchCallOperationDeleteFile",
    "ApplyPatchCallOperationUpdateFile",
    "ApplyPatchCallAgent",
    "ApplyPatchCallCaller",
    "ApplyPatchCallCallerDirect",
    "ApplyPatchCallCallerProgram",
    "ApplyPatchCallOutput",
    "ApplyPatchCallOutputAgent",
    "ApplyPatchCallOutputCaller",
    "ApplyPatchCallOutputCallerDirect",
    "ApplyPatchCallOutputCallerProgram",
    "McpListTools",
    "McpListToolsTool",
    "McpListToolsAgent",
    "McpApprovalRequest",
    "McpApprovalRequestAgent",
    "McpApprovalResponse",
    "McpApprovalResponseAgent",
    "McpCall",
    "McpCallAgent",
    "CompactionTrigger",
    "CompactionTriggerAgent",
    "ItemReference",
    "ItemReferenceAgent",
    "Program",
    "ProgramAgent",
    "ProgramOutput",
    "ProgramOutputAgent",
]


class MessageAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class Message(BaseModel):
    """
    A message input to the model with a role indicating instruction following
    hierarchy. Instructions given with the `developer` or `system` role take
    precedence over instructions given with the `user` role.
    """

    content: BetaResponseInputMessageContentList
    """
    A list of one or many input items to the model, containing different content
    types.
    """

    role: Literal["user", "system", "developer"]
    """The role of the message input. One of `user`, `system`, or `developer`."""

    agent: Optional[MessageAgent] = None
    """The agent that produced this item."""

    status: Optional[Literal["in_progress", "completed", "incomplete"]] = None
    """The status of item.

    One of `in_progress`, `completed`, or `incomplete`. Populated when items are
    returned via API.
    """

    type: Optional[Literal["message"]] = None
    """The type of the message input. Always set to `message`."""


class ComputerCallOutputAcknowledgedSafetyCheck(BaseModel):
    """A pending safety check for the computer call."""

    id: str
    """The ID of the pending safety check."""

    code: Optional[str] = None
    """The type of the pending safety check."""

    message: Optional[str] = None
    """Details about the pending safety check."""


class ComputerCallOutputAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class ComputerCallOutput(BaseModel):
    """The output of a computer tool call."""

    call_id: str
    """The ID of the computer tool call that produced the output."""

    output: BetaResponseComputerToolCallOutputScreenshot
    """A computer screenshot image used with the computer use tool."""

    type: Literal["computer_call_output"]
    """The type of the computer tool call output. Always `computer_call_output`."""

    id: Optional[str] = None
    """The ID of the computer tool call output."""

    acknowledged_safety_checks: Optional[List[ComputerCallOutputAcknowledgedSafetyCheck]] = None
    """
    The safety checks reported by the API that have been acknowledged by the
    developer.
    """

    agent: Optional[ComputerCallOutputAgent] = None
    """The agent that produced this item."""

    status: Optional[Literal["in_progress", "completed", "incomplete"]] = None
    """The status of the message input.

    One of `in_progress`, `completed`, or `incomplete`. Populated when input items
    are returned via API.
    """


class FunctionCallOutputAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class FunctionCallOutputCallerDirect(BaseModel):
    type: Literal["direct"]
    """The caller type. Always `direct`."""


class FunctionCallOutputCallerProgram(BaseModel):
    caller_id: str
    """The call ID of the program item that produced this tool call."""

    type: Literal["program"]
    """The caller type. Always `program`."""


FunctionCallOutputCaller: TypeAlias = Annotated[
    Union[FunctionCallOutputCallerDirect, FunctionCallOutputCallerProgram, None], PropertyInfo(discriminator="type")
]


class FunctionCallOutput(BaseModel):
    """The output of a function tool call."""

    call_id: str
    """The unique ID of the function tool call generated by the model."""

    output: Union[str, BetaResponseFunctionCallOutputItemList]
    """Text, image, or file output of the function tool call."""

    type: Literal["function_call_output"]
    """The type of the function tool call output. Always `function_call_output`."""

    id: Optional[str] = None
    """The unique ID of the function tool call output.

    Populated when this item is returned via API.
    """

    agent: Optional[FunctionCallOutputAgent] = None
    """The agent that produced this item."""

    caller: Optional[FunctionCallOutputCaller] = None
    """The execution context that produced this tool call."""

    status: Optional[Literal["in_progress", "completed", "incomplete"]] = None
    """The status of the item.

    One of `in_progress`, `completed`, or `incomplete`. Populated when items are
    returned via API.
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
    Union[BetaResponseInputTextContent, BetaResponseInputImageContent, AgentMessageContentEncryptedContent],
    PropertyInfo(discriminator="type"),
]


class AgentMessageAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class AgentMessage(BaseModel):
    """A message routed between agents."""

    author: str
    """The sending agent identity."""

    content: List[AgentMessageContent]
    """Plaintext, image, or encrypted content sent between agents."""

    recipient: str
    """The destination agent identity."""

    type: Literal["agent_message"]
    """The item type. Always `agent_message`."""

    id: Optional[str] = None
    """The unique ID of this agent message item."""

    agent: Optional[AgentMessageAgent] = None
    """The agent that produced this item."""


class MultiAgentCallAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class MultiAgentCall(BaseModel):
    action: Literal["spawn_agent", "interrupt_agent", "list_agents", "send_message", "followup_task", "wait_agent"]
    """The multi-agent action that was executed."""

    arguments: str
    """The action arguments as a JSON string."""

    call_id: str
    """The unique ID linking this call to its output."""

    type: Literal["multi_agent_call"]
    """The item type. Always `multi_agent_call`."""

    id: Optional[str] = None
    """The unique ID of this multi-agent call."""

    agent: Optional[MultiAgentCallAgent] = None
    """The agent that produced this item."""


class MultiAgentCallOutputOutputAnnotationFileCitation(BaseModel):
    file_id: str
    """The ID of the file."""

    filename: str
    """The filename of the file cited."""

    index: int
    """The index of the file in the list of files."""

    type: Literal["file_citation"]
    """The citation type. Always `file_citation`."""


class MultiAgentCallOutputOutputAnnotationURLCitation(BaseModel):
    end_index: int
    """The index of the last character of the citation in the message."""

    start_index: int
    """The index of the first character of the citation in the message."""

    title: str
    """The title of the cited resource."""

    type: Literal["url_citation"]
    """The citation type. Always `url_citation`."""

    url: str
    """The URL of the cited resource."""


class MultiAgentCallOutputOutputAnnotationContainerFileCitation(BaseModel):
    container_id: str
    """The ID of the container."""

    end_index: int
    """The index of the last character of the citation in the message."""

    file_id: str
    """The ID of the container file."""

    filename: str
    """The filename of the container file cited."""

    start_index: int
    """The index of the first character of the citation in the message."""

    type: Literal["container_file_citation"]
    """The citation type. Always `container_file_citation`."""


MultiAgentCallOutputOutputAnnotation: TypeAlias = Annotated[
    Union[
        MultiAgentCallOutputOutputAnnotationFileCitation,
        MultiAgentCallOutputOutputAnnotationURLCitation,
        MultiAgentCallOutputOutputAnnotationContainerFileCitation,
    ],
    PropertyInfo(discriminator="type"),
]


class MultiAgentCallOutputOutput(BaseModel):
    text: str
    """The text content."""

    type: Literal["output_text"]
    """The content type. Always `output_text`."""

    annotations: Optional[List[MultiAgentCallOutputOutputAnnotation]] = None
    """Citations associated with the text content."""


class MultiAgentCallOutputAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class MultiAgentCallOutput(BaseModel):
    action: Literal["spawn_agent", "interrupt_agent", "list_agents", "send_message", "followup_task", "wait_agent"]
    """The multi-agent action that produced this result."""

    call_id: str
    """The unique ID of the multi-agent call."""

    output: List[MultiAgentCallOutputOutput]
    """Text output returned by the multi-agent action."""

    type: Literal["multi_agent_call_output"]
    """The item type. Always `multi_agent_call_output`."""

    id: Optional[str] = None
    """The unique ID of this multi-agent call output."""

    agent: Optional[MultiAgentCallOutputAgent] = None
    """The agent that produced this item."""


class ToolSearchCallAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class ToolSearchCall(BaseModel):
    arguments: object
    """The arguments supplied to the tool search call."""

    type: Literal["tool_search_call"]
    """The item type. Always `tool_search_call`."""

    id: Optional[str] = None
    """The unique ID of this tool search call."""

    agent: Optional[ToolSearchCallAgent] = None
    """The agent that produced this item."""

    call_id: Optional[str] = None
    """The unique ID of the tool search call generated by the model."""

    execution: Optional[Literal["server", "client"]] = None
    """Whether tool search was executed by the server or by the client."""

    status: Optional[Literal["in_progress", "completed", "incomplete"]] = None
    """The status of the tool search call."""


class AdditionalToolsAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class AdditionalTools(BaseModel):
    role: Literal["developer"]
    """The role that provided the additional tools. Only `developer` is supported."""

    tools: List[BetaTool]
    """A list of additional tools made available at this item."""

    type: Literal["additional_tools"]
    """The item type. Always `additional_tools`."""

    id: Optional[str] = None
    """The unique ID of this additional tools item."""

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


class ShellCallAction(BaseModel):
    """The shell commands and limits that describe how to run the tool call."""

    commands: List[str]
    """Ordered shell commands for the execution environment to run."""

    max_output_length: Optional[int] = None
    """
    Maximum number of UTF-8 characters to capture from combined stdout and stderr
    output.
    """

    timeout_ms: Optional[int] = None
    """Maximum wall-clock time in milliseconds to allow the shell commands to run."""


class ShellCallAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class ShellCallCallerDirect(BaseModel):
    type: Literal["direct"]
    """The caller type. Always `direct`."""


class ShellCallCallerProgram(BaseModel):
    caller_id: str
    """The call ID of the program item that produced this tool call."""

    type: Literal["program"]
    """The caller type. Always `program`."""


ShellCallCaller: TypeAlias = Annotated[
    Union[ShellCallCallerDirect, ShellCallCallerProgram, None], PropertyInfo(discriminator="type")
]

ShellCallEnvironment: TypeAlias = Annotated[
    Union[BetaLocalEnvironment, BetaContainerReference, None], PropertyInfo(discriminator="type")
]


class ShellCall(BaseModel):
    """A tool representing a request to execute one or more shell commands."""

    action: ShellCallAction
    """The shell commands and limits that describe how to run the tool call."""

    call_id: str
    """The unique ID of the shell tool call generated by the model."""

    type: Literal["shell_call"]
    """The type of the item. Always `shell_call`."""

    id: Optional[str] = None
    """The unique ID of the shell tool call.

    Populated when this item is returned via API.
    """

    agent: Optional[ShellCallAgent] = None
    """The agent that produced this item."""

    caller: Optional[ShellCallCaller] = None
    """The execution context that produced this tool call."""

    environment: Optional[ShellCallEnvironment] = None
    """The environment to execute the shell commands in."""

    status: Optional[Literal["in_progress", "completed", "incomplete"]] = None
    """The status of the shell call.

    One of `in_progress`, `completed`, or `incomplete`.
    """


class ShellCallOutputAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class ShellCallOutputCallerDirect(BaseModel):
    type: Literal["direct"]
    """The caller type. Always `direct`."""


class ShellCallOutputCallerProgram(BaseModel):
    caller_id: str
    """The call ID of the program item that produced this tool call."""

    type: Literal["program"]
    """The caller type. Always `program`."""


ShellCallOutputCaller: TypeAlias = Annotated[
    Union[ShellCallOutputCallerDirect, ShellCallOutputCallerProgram, None], PropertyInfo(discriminator="type")
]


class ShellCallOutput(BaseModel):
    """The streamed output items emitted by a shell tool call."""

    call_id: str
    """The unique ID of the shell tool call generated by the model."""

    output: List[BetaResponseFunctionShellCallOutputContent]
    """
    Captured chunks of stdout and stderr output, along with their associated
    outcomes.
    """

    type: Literal["shell_call_output"]
    """The type of the item. Always `shell_call_output`."""

    id: Optional[str] = None
    """The unique ID of the shell tool call output.

    Populated when this item is returned via API.
    """

    agent: Optional[ShellCallOutputAgent] = None
    """The agent that produced this item."""

    caller: Optional[ShellCallOutputCaller] = None
    """The execution context that produced this tool call."""

    max_output_length: Optional[int] = None
    """
    The maximum number of UTF-8 characters captured for this shell call's combined
    output.
    """

    status: Optional[Literal["in_progress", "completed", "incomplete"]] = None
    """The status of the shell call output."""


class ApplyPatchCallOperationCreateFile(BaseModel):
    """Instruction for creating a new file via the apply_patch tool."""

    diff: str
    """Unified diff content to apply when creating the file."""

    path: str
    """Path of the file to create relative to the workspace root."""

    type: Literal["create_file"]
    """The operation type. Always `create_file`."""


class ApplyPatchCallOperationDeleteFile(BaseModel):
    """Instruction for deleting an existing file via the apply_patch tool."""

    path: str
    """Path of the file to delete relative to the workspace root."""

    type: Literal["delete_file"]
    """The operation type. Always `delete_file`."""


class ApplyPatchCallOperationUpdateFile(BaseModel):
    """Instruction for updating an existing file via the apply_patch tool."""

    diff: str
    """Unified diff content to apply to the existing file."""

    path: str
    """Path of the file to update relative to the workspace root."""

    type: Literal["update_file"]
    """The operation type. Always `update_file`."""


ApplyPatchCallOperation: TypeAlias = Annotated[
    Union[ApplyPatchCallOperationCreateFile, ApplyPatchCallOperationDeleteFile, ApplyPatchCallOperationUpdateFile],
    PropertyInfo(discriminator="type"),
]


class ApplyPatchCallAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class ApplyPatchCallCallerDirect(BaseModel):
    type: Literal["direct"]
    """The caller type. Always `direct`."""


class ApplyPatchCallCallerProgram(BaseModel):
    caller_id: str
    """The call ID of the program item that produced this tool call."""

    type: Literal["program"]
    """The caller type. Always `program`."""


ApplyPatchCallCaller: TypeAlias = Annotated[
    Union[ApplyPatchCallCallerDirect, ApplyPatchCallCallerProgram, None], PropertyInfo(discriminator="type")
]


class ApplyPatchCall(BaseModel):
    """
    A tool call representing a request to create, delete, or update files using diff patches.
    """

    call_id: str
    """The unique ID of the apply patch tool call generated by the model."""

    operation: ApplyPatchCallOperation
    """
    The specific create, delete, or update instruction for the apply_patch tool
    call.
    """

    status: Literal["in_progress", "completed"]
    """The status of the apply patch tool call. One of `in_progress` or `completed`."""

    type: Literal["apply_patch_call"]
    """The type of the item. Always `apply_patch_call`."""

    id: Optional[str] = None
    """The unique ID of the apply patch tool call.

    Populated when this item is returned via API.
    """

    agent: Optional[ApplyPatchCallAgent] = None
    """The agent that produced this item."""

    caller: Optional[ApplyPatchCallCaller] = None
    """The execution context that produced this tool call."""


class ApplyPatchCallOutputAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class ApplyPatchCallOutputCallerDirect(BaseModel):
    type: Literal["direct"]
    """The caller type. Always `direct`."""


class ApplyPatchCallOutputCallerProgram(BaseModel):
    caller_id: str
    """The call ID of the program item that produced this tool call."""

    type: Literal["program"]
    """The caller type. Always `program`."""


ApplyPatchCallOutputCaller: TypeAlias = Annotated[
    Union[ApplyPatchCallOutputCallerDirect, ApplyPatchCallOutputCallerProgram, None], PropertyInfo(discriminator="type")
]


class ApplyPatchCallOutput(BaseModel):
    """The streamed output emitted by an apply patch tool call."""

    call_id: str
    """The unique ID of the apply patch tool call generated by the model."""

    status: Literal["completed", "failed"]
    """The status of the apply patch tool call output. One of `completed` or `failed`."""

    type: Literal["apply_patch_call_output"]
    """The type of the item. Always `apply_patch_call_output`."""

    id: Optional[str] = None
    """The unique ID of the apply patch tool call output.

    Populated when this item is returned via API.
    """

    agent: Optional[ApplyPatchCallOutputAgent] = None
    """The agent that produced this item."""

    caller: Optional[ApplyPatchCallOutputCaller] = None
    """The execution context that produced this tool call."""

    output: Optional[str] = None
    """
    Optional human-readable log text from the apply patch tool (e.g., patch results
    or errors).
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

    approval_request_id: str
    """The ID of the approval request being answered."""

    approve: bool
    """Whether the request was approved."""

    type: Literal["mcp_approval_response"]
    """The type of the item. Always `mcp_approval_response`."""

    id: Optional[str] = None
    """The unique ID of the approval response"""

    agent: Optional[McpApprovalResponseAgent] = None
    """The agent that produced this item."""

    reason: Optional[str] = None
    """Optional reason for the decision."""


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


class CompactionTriggerAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class CompactionTrigger(BaseModel):
    """Compacts the current context. Must be the final input item."""

    type: Literal["compaction_trigger"]
    """The type of the item. Always `compaction_trigger`."""

    agent: Optional[CompactionTriggerAgent] = None
    """The agent that produced this item."""


class ItemReferenceAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class ItemReference(BaseModel):
    """An internal identifier for an item to reference."""

    id: str
    """The ID of the item to reference."""

    agent: Optional[ItemReferenceAgent] = None
    """The agent that produced this item."""

    type: Optional[Literal["item_reference"]] = None
    """The type of item to reference. Always `item_reference`."""


class ProgramAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class Program(BaseModel):
    id: str
    """The unique ID of this program item."""

    call_id: str
    """The stable call ID of the program item."""

    code: str
    """The JavaScript source executed by programmatic tool calling."""

    fingerprint: str
    """Opaque program replay fingerprint that must be round-tripped."""

    type: Literal["program"]
    """The item type. Always `program`."""

    agent: Optional[ProgramAgent] = None
    """The agent that produced this item."""


class ProgramOutputAgent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class ProgramOutput(BaseModel):
    id: str
    """The unique ID of this program output item."""

    call_id: str
    """The call ID of the program item."""

    result: str
    """The result produced by the program item."""

    status: Literal["completed", "incomplete"]
    """The terminal status of the program output."""

    type: Literal["program_output"]
    """The item type. Always `program_output`."""

    agent: Optional[ProgramOutputAgent] = None
    """The agent that produced this item."""


BetaResponseInputItem: TypeAlias = Annotated[
    Union[
        BetaEasyInputMessage,
        Message,
        BetaResponseOutputMessage,
        BetaResponseFileSearchToolCall,
        BetaResponseComputerToolCall,
        ComputerCallOutput,
        BetaResponseFunctionWebSearch,
        BetaResponseFunctionToolCall,
        FunctionCallOutput,
        AgentMessage,
        MultiAgentCall,
        MultiAgentCallOutput,
        ToolSearchCall,
        BetaResponseToolSearchOutputItemParam,
        AdditionalTools,
        BetaResponseReasoningItem,
        BetaResponseCompactionItemParam,
        ImageGenerationCall,
        BetaResponseCodeInterpreterToolCall,
        LocalShellCall,
        LocalShellCallOutput,
        ShellCall,
        ShellCallOutput,
        ApplyPatchCall,
        ApplyPatchCallOutput,
        McpListTools,
        McpApprovalRequest,
        McpApprovalResponse,
        McpCall,
        BetaResponseCustomToolCallOutput,
        BetaResponseCustomToolCall,
        CompactionTrigger,
        ItemReference,
        Program,
        ProgramOutput,
    ],
    PropertyInfo(discriminator="type"),
]
