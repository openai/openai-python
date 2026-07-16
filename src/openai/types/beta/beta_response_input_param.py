# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from ..._types import SequenceNotStr
from .beta_tool_param import BetaToolParam
from .beta_local_environment_param import BetaLocalEnvironmentParam
from .beta_easy_input_message_param import BetaEasyInputMessageParam
from .beta_container_reference_param import BetaContainerReferenceParam
from .beta_response_output_message_param import BetaResponseOutputMessageParam
from .beta_response_reasoning_item_param import BetaResponseReasoningItemParam
from .beta_response_custom_tool_call_param import BetaResponseCustomToolCallParam
from .beta_response_computer_tool_call_param import BetaResponseComputerToolCallParam
from .beta_response_function_tool_call_param import BetaResponseFunctionToolCallParam
from .beta_response_input_text_content_param import BetaResponseInputTextContentParam
from .beta_response_function_web_search_param import BetaResponseFunctionWebSearchParam
from .beta_response_input_image_content_param import BetaResponseInputImageContentParam
from .beta_response_compaction_item_param_param import BetaResponseCompactionItemParamParam
from .beta_response_file_search_tool_call_param import BetaResponseFileSearchToolCallParam
from .beta_response_custom_tool_call_output_param import BetaResponseCustomToolCallOutputParam
from .beta_response_code_interpreter_tool_call_param import BetaResponseCodeInterpreterToolCallParam
from .beta_response_input_message_content_list_param import BetaResponseInputMessageContentListParam
from .beta_response_tool_search_output_item_param_param import BetaResponseToolSearchOutputItemParamParam
from .beta_response_function_call_output_item_list_param import BetaResponseFunctionCallOutputItemListParam
from .beta_response_function_shell_call_output_content_param import BetaResponseFunctionShellCallOutputContentParam
from .beta_response_computer_tool_call_output_screenshot_param import BetaResponseComputerToolCallOutputScreenshotParam

__all__ = [
    "BetaResponseInputParam",
    "BetaResponseInputItemParam",
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
    "MultiAgentCallOutputOutputAnnotationsUnionMember0",
    "MultiAgentCallOutputOutputAnnotationsUnionMember1",
    "MultiAgentCallOutputOutputAnnotationsUnionMember2",
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


class MessageAgent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class Message(TypedDict, total=False):
    """
    A message input to the model with a role indicating instruction following
    hierarchy. Instructions given with the `developer` or `system` role take
    precedence over instructions given with the `user` role.
    """

    content: Required[BetaResponseInputMessageContentListParam]
    """
    A list of one or many input items to the model, containing different content
    types.
    """

    role: Required[Literal["user", "system", "developer"]]
    """The role of the message input. One of `user`, `system`, or `developer`."""

    agent: Optional[MessageAgent]
    """The agent that produced this item."""

    status: Literal["in_progress", "completed", "incomplete"]
    """The status of item.

    One of `in_progress`, `completed`, or `incomplete`. Populated when items are
    returned via API.
    """

    type: Literal["message"]
    """The type of the message input. Always set to `message`."""


class ComputerCallOutputAcknowledgedSafetyCheck(TypedDict, total=False):
    """A pending safety check for the computer call."""

    id: Required[str]
    """The ID of the pending safety check."""

    code: Optional[str]
    """The type of the pending safety check."""

    message: Optional[str]
    """Details about the pending safety check."""


class ComputerCallOutputAgent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class ComputerCallOutput(TypedDict, total=False):
    """The output of a computer tool call."""

    call_id: Required[str]
    """The ID of the computer tool call that produced the output."""

    output: Required[BetaResponseComputerToolCallOutputScreenshotParam]
    """A computer screenshot image used with the computer use tool."""

    type: Required[Literal["computer_call_output"]]
    """The type of the computer tool call output. Always `computer_call_output`."""

    id: Optional[str]
    """The ID of the computer tool call output."""

    acknowledged_safety_checks: Optional[Iterable[ComputerCallOutputAcknowledgedSafetyCheck]]
    """
    The safety checks reported by the API that have been acknowledged by the
    developer.
    """

    agent: Optional[ComputerCallOutputAgent]
    """The agent that produced this item."""

    status: Optional[Literal["in_progress", "completed", "incomplete"]]
    """The status of the message input.

    One of `in_progress`, `completed`, or `incomplete`. Populated when input items
    are returned via API.
    """


class FunctionCallOutputAgent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class FunctionCallOutputCallerDirect(TypedDict, total=False):
    type: Required[Literal["direct"]]
    """The caller type. Always `direct`."""


class FunctionCallOutputCallerProgram(TypedDict, total=False):
    caller_id: Required[str]
    """The call ID of the program item that produced this tool call."""

    type: Required[Literal["program"]]
    """The caller type. Always `program`."""


FunctionCallOutputCaller: TypeAlias = Union[FunctionCallOutputCallerDirect, FunctionCallOutputCallerProgram]


class FunctionCallOutput(TypedDict, total=False):
    """The output of a function tool call."""

    call_id: Required[str]
    """The unique ID of the function tool call generated by the model."""

    output: Required[Union[str, BetaResponseFunctionCallOutputItemListParam]]
    """Text, image, or file output of the function tool call."""

    type: Required[Literal["function_call_output"]]
    """The type of the function tool call output. Always `function_call_output`."""

    id: Optional[str]
    """The unique ID of the function tool call output.

    Populated when this item is returned via API.
    """

    agent: Optional[FunctionCallOutputAgent]
    """The agent that produced this item."""

    caller: Optional[FunctionCallOutputCaller]
    """The execution context that produced this tool call."""

    status: Optional[Literal["in_progress", "completed", "incomplete"]]
    """The status of the item.

    One of `in_progress`, `completed`, or `incomplete`. Populated when items are
    returned via API.
    """


class AgentMessageContentEncryptedContent(TypedDict, total=False):
    """
    Opaque encrypted content that Responses API decrypts inside trusted model execution.
    """

    encrypted_content: Required[str]
    """Opaque encrypted content."""

    type: Required[Literal["encrypted_content"]]
    """The type of the input item. Always `encrypted_content`."""


AgentMessageContent: TypeAlias = Union[
    BetaResponseInputTextContentParam, BetaResponseInputImageContentParam, AgentMessageContentEncryptedContent
]


class AgentMessageAgent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class AgentMessage(TypedDict, total=False):
    """A message routed between agents."""

    author: Required[str]
    """The sending agent identity."""

    content: Required[Iterable[AgentMessageContent]]
    """Plaintext, image, or encrypted content sent between agents."""

    recipient: Required[str]
    """The destination agent identity."""

    type: Required[Literal["agent_message"]]
    """The item type. Always `agent_message`."""

    id: Optional[str]
    """The unique ID of this agent message item."""

    agent: Optional[AgentMessageAgent]
    """The agent that produced this item."""


class MultiAgentCallAgent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class MultiAgentCall(TypedDict, total=False):
    action: Required[
        Literal["spawn_agent", "interrupt_agent", "list_agents", "send_message", "followup_task", "wait_agent"]
    ]
    """The multi-agent action that was executed."""

    arguments: Required[str]
    """The action arguments as a JSON string."""

    call_id: Required[str]
    """The unique ID linking this call to its output."""

    type: Required[Literal["multi_agent_call"]]
    """The item type. Always `multi_agent_call`."""

    id: Optional[str]
    """The unique ID of this multi-agent call."""

    agent: Optional[MultiAgentCallAgent]
    """The agent that produced this item."""


class MultiAgentCallOutputOutputAnnotationFileCitation(TypedDict, total=False):
    file_id: Required[str]
    """The ID of the file."""

    filename: Required[str]
    """The filename of the file cited."""

    index: Required[int]
    """The index of the file in the list of files."""

    type: Required[Literal["file_citation"]]
    """The citation type. Always `file_citation`."""


class MultiAgentCallOutputOutputAnnotationURLCitation(TypedDict, total=False):
    end_index: Required[int]
    """The index of the last character of the citation in the message."""

    start_index: Required[int]
    """The index of the first character of the citation in the message."""

    title: Required[str]
    """The title of the cited resource."""

    type: Required[Literal["url_citation"]]
    """The citation type. Always `url_citation`."""

    url: Required[str]
    """The URL of the cited resource."""


class MultiAgentCallOutputOutputAnnotationContainerFileCitation(TypedDict, total=False):
    container_id: Required[str]
    """The ID of the container."""

    end_index: Required[int]
    """The index of the last character of the citation in the message."""

    file_id: Required[str]
    """The ID of the container file."""

    filename: Required[str]
    """The filename of the container file cited."""

    start_index: Required[int]
    """The index of the first character of the citation in the message."""

    type: Required[Literal["container_file_citation"]]
    """The citation type. Always `container_file_citation`."""


MultiAgentCallOutputOutputAnnotation: TypeAlias = Union[
    MultiAgentCallOutputOutputAnnotationFileCitation,
    MultiAgentCallOutputOutputAnnotationURLCitation,
    MultiAgentCallOutputOutputAnnotationContainerFileCitation,
]


# Backwards-compatible aliases for names generated before the annotation schemas
# received explicit names.
class MultiAgentCallOutputOutputAnnotationsUnionMember0(MultiAgentCallOutputOutputAnnotationFileCitation):
    pass


class MultiAgentCallOutputOutputAnnotationsUnionMember1(MultiAgentCallOutputOutputAnnotationURLCitation):
    pass


class MultiAgentCallOutputOutputAnnotationsUnionMember2(MultiAgentCallOutputOutputAnnotationContainerFileCitation):
    pass


class MultiAgentCallOutputOutput(TypedDict, total=False):
    text: Required[str]
    """The text content."""

    type: Required[Literal["output_text"]]
    """The content type. Always `output_text`."""

    annotations: Iterable[MultiAgentCallOutputOutputAnnotation]
    """Citations associated with the text content."""


class MultiAgentCallOutputAgent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class MultiAgentCallOutput(TypedDict, total=False):
    action: Required[
        Literal["spawn_agent", "interrupt_agent", "list_agents", "send_message", "followup_task", "wait_agent"]
    ]
    """The multi-agent action that produced this result."""

    call_id: Required[str]
    """The unique ID of the multi-agent call."""

    output: Required[Iterable[MultiAgentCallOutputOutput]]
    """Text output returned by the multi-agent action."""

    type: Required[Literal["multi_agent_call_output"]]
    """The item type. Always `multi_agent_call_output`."""

    id: Optional[str]
    """The unique ID of this multi-agent call output."""

    agent: Optional[MultiAgentCallOutputAgent]
    """The agent that produced this item."""


class ToolSearchCallAgent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class ToolSearchCall(TypedDict, total=False):
    arguments: Required[object]
    """The arguments supplied to the tool search call."""

    type: Required[Literal["tool_search_call"]]
    """The item type. Always `tool_search_call`."""

    id: Optional[str]
    """The unique ID of this tool search call."""

    agent: Optional[ToolSearchCallAgent]
    """The agent that produced this item."""

    call_id: Optional[str]
    """The unique ID of the tool search call generated by the model."""

    execution: Literal["server", "client"]
    """Whether tool search was executed by the server or by the client."""

    status: Optional[Literal["in_progress", "completed", "incomplete"]]
    """The status of the tool search call."""


class AdditionalToolsAgent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class AdditionalTools(TypedDict, total=False):
    role: Required[Literal["developer"]]
    """The role that provided the additional tools. Only `developer` is supported."""

    tools: Required[Iterable[BetaToolParam]]
    """A list of additional tools made available at this item."""

    type: Required[Literal["additional_tools"]]
    """The item type. Always `additional_tools`."""

    id: Optional[str]
    """The unique ID of this additional tools item."""

    agent: Optional[AdditionalToolsAgent]
    """The agent that produced this item."""


class ImageGenerationCallAgent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class ImageGenerationCall(TypedDict, total=False):
    """An image generation request made by the model."""

    id: Required[str]
    """The unique ID of the image generation call."""

    result: Required[Optional[str]]
    """The generated image encoded in base64."""

    status: Required[Literal["in_progress", "completed", "generating", "failed"]]
    """The status of the image generation call."""

    type: Required[Literal["image_generation_call"]]
    """The type of the image generation call. Always `image_generation_call`."""

    agent: Optional[ImageGenerationCallAgent]
    """The agent that produced this item."""


class LocalShellCallAction(TypedDict, total=False):
    """Execute a shell command on the server."""

    command: Required[SequenceNotStr[str]]
    """The command to run."""

    env: Required[Dict[str, str]]
    """Environment variables to set for the command."""

    type: Required[Literal["exec"]]
    """The type of the local shell action. Always `exec`."""

    timeout_ms: Optional[int]
    """Optional timeout in milliseconds for the command."""

    user: Optional[str]
    """Optional user to run the command as."""

    working_directory: Optional[str]
    """Optional working directory to run the command in."""


class LocalShellCallAgent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class LocalShellCall(TypedDict, total=False):
    """A tool call to run a command on the local shell."""

    id: Required[str]
    """The unique ID of the local shell call."""

    action: Required[LocalShellCallAction]
    """Execute a shell command on the server."""

    call_id: Required[str]
    """The unique ID of the local shell tool call generated by the model."""

    status: Required[Literal["in_progress", "completed", "incomplete"]]
    """The status of the local shell call."""

    type: Required[Literal["local_shell_call"]]
    """The type of the local shell call. Always `local_shell_call`."""

    agent: Optional[LocalShellCallAgent]
    """The agent that produced this item."""


class LocalShellCallOutputAgent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class LocalShellCallOutput(TypedDict, total=False):
    """The output of a local shell tool call."""

    id: Required[str]
    """The unique ID of the local shell tool call generated by the model."""

    output: Required[str]
    """A JSON string of the output of the local shell tool call."""

    type: Required[Literal["local_shell_call_output"]]
    """The type of the local shell tool call output. Always `local_shell_call_output`."""

    agent: Optional[LocalShellCallOutputAgent]
    """The agent that produced this item."""

    status: Optional[Literal["in_progress", "completed", "incomplete"]]
    """The status of the item. One of `in_progress`, `completed`, or `incomplete`."""


class ShellCallAction(TypedDict, total=False):
    """The shell commands and limits that describe how to run the tool call."""

    commands: Required[SequenceNotStr[str]]
    """Ordered shell commands for the execution environment to run."""

    max_output_length: Optional[int]
    """
    Maximum number of UTF-8 characters to capture from combined stdout and stderr
    output.
    """

    timeout_ms: Optional[int]
    """Maximum wall-clock time in milliseconds to allow the shell commands to run."""


class ShellCallAgent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class ShellCallCallerDirect(TypedDict, total=False):
    type: Required[Literal["direct"]]
    """The caller type. Always `direct`."""


class ShellCallCallerProgram(TypedDict, total=False):
    caller_id: Required[str]
    """The call ID of the program item that produced this tool call."""

    type: Required[Literal["program"]]
    """The caller type. Always `program`."""


ShellCallCaller: TypeAlias = Union[ShellCallCallerDirect, ShellCallCallerProgram]

ShellCallEnvironment: TypeAlias = Union[BetaLocalEnvironmentParam, BetaContainerReferenceParam]


class ShellCall(TypedDict, total=False):
    """A tool representing a request to execute one or more shell commands."""

    action: Required[ShellCallAction]
    """The shell commands and limits that describe how to run the tool call."""

    call_id: Required[str]
    """The unique ID of the shell tool call generated by the model."""

    type: Required[Literal["shell_call"]]
    """The type of the item. Always `shell_call`."""

    id: Optional[str]
    """The unique ID of the shell tool call.

    Populated when this item is returned via API.
    """

    agent: Optional[ShellCallAgent]
    """The agent that produced this item."""

    caller: Optional[ShellCallCaller]
    """The execution context that produced this tool call."""

    environment: Optional[ShellCallEnvironment]
    """The environment to execute the shell commands in."""

    status: Optional[Literal["in_progress", "completed", "incomplete"]]
    """The status of the shell call.

    One of `in_progress`, `completed`, or `incomplete`.
    """


class ShellCallOutputAgent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class ShellCallOutputCallerDirect(TypedDict, total=False):
    type: Required[Literal["direct"]]
    """The caller type. Always `direct`."""


class ShellCallOutputCallerProgram(TypedDict, total=False):
    caller_id: Required[str]
    """The call ID of the program item that produced this tool call."""

    type: Required[Literal["program"]]
    """The caller type. Always `program`."""


ShellCallOutputCaller: TypeAlias = Union[ShellCallOutputCallerDirect, ShellCallOutputCallerProgram]


class ShellCallOutput(TypedDict, total=False):
    """The streamed output items emitted by a shell tool call."""

    call_id: Required[str]
    """The unique ID of the shell tool call generated by the model."""

    output: Required[Iterable[BetaResponseFunctionShellCallOutputContentParam]]
    """
    Captured chunks of stdout and stderr output, along with their associated
    outcomes.
    """

    type: Required[Literal["shell_call_output"]]
    """The type of the item. Always `shell_call_output`."""

    id: Optional[str]
    """The unique ID of the shell tool call output.

    Populated when this item is returned via API.
    """

    agent: Optional[ShellCallOutputAgent]
    """The agent that produced this item."""

    caller: Optional[ShellCallOutputCaller]
    """The execution context that produced this tool call."""

    max_output_length: Optional[int]
    """
    The maximum number of UTF-8 characters captured for this shell call's combined
    output.
    """

    status: Optional[Literal["in_progress", "completed", "incomplete"]]
    """The status of the shell call output."""


class ApplyPatchCallOperationCreateFile(TypedDict, total=False):
    """Instruction for creating a new file via the apply_patch tool."""

    diff: Required[str]
    """Unified diff content to apply when creating the file."""

    path: Required[str]
    """Path of the file to create relative to the workspace root."""

    type: Required[Literal["create_file"]]
    """The operation type. Always `create_file`."""


class ApplyPatchCallOperationDeleteFile(TypedDict, total=False):
    """Instruction for deleting an existing file via the apply_patch tool."""

    path: Required[str]
    """Path of the file to delete relative to the workspace root."""

    type: Required[Literal["delete_file"]]
    """The operation type. Always `delete_file`."""


class ApplyPatchCallOperationUpdateFile(TypedDict, total=False):
    """Instruction for updating an existing file via the apply_patch tool."""

    diff: Required[str]
    """Unified diff content to apply to the existing file."""

    path: Required[str]
    """Path of the file to update relative to the workspace root."""

    type: Required[Literal["update_file"]]
    """The operation type. Always `update_file`."""


ApplyPatchCallOperation: TypeAlias = Union[
    ApplyPatchCallOperationCreateFile, ApplyPatchCallOperationDeleteFile, ApplyPatchCallOperationUpdateFile
]


class ApplyPatchCallAgent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class ApplyPatchCallCallerDirect(TypedDict, total=False):
    type: Required[Literal["direct"]]
    """The caller type. Always `direct`."""


class ApplyPatchCallCallerProgram(TypedDict, total=False):
    caller_id: Required[str]
    """The call ID of the program item that produced this tool call."""

    type: Required[Literal["program"]]
    """The caller type. Always `program`."""


ApplyPatchCallCaller: TypeAlias = Union[ApplyPatchCallCallerDirect, ApplyPatchCallCallerProgram]


class ApplyPatchCall(TypedDict, total=False):
    """
    A tool call representing a request to create, delete, or update files using diff patches.
    """

    call_id: Required[str]
    """The unique ID of the apply patch tool call generated by the model."""

    operation: Required[ApplyPatchCallOperation]
    """
    The specific create, delete, or update instruction for the apply_patch tool
    call.
    """

    status: Required[Literal["in_progress", "completed"]]
    """The status of the apply patch tool call. One of `in_progress` or `completed`."""

    type: Required[Literal["apply_patch_call"]]
    """The type of the item. Always `apply_patch_call`."""

    id: Optional[str]
    """The unique ID of the apply patch tool call.

    Populated when this item is returned via API.
    """

    agent: Optional[ApplyPatchCallAgent]
    """The agent that produced this item."""

    caller: Optional[ApplyPatchCallCaller]
    """The execution context that produced this tool call."""


class ApplyPatchCallOutputAgent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class ApplyPatchCallOutputCallerDirect(TypedDict, total=False):
    type: Required[Literal["direct"]]
    """The caller type. Always `direct`."""


class ApplyPatchCallOutputCallerProgram(TypedDict, total=False):
    caller_id: Required[str]
    """The call ID of the program item that produced this tool call."""

    type: Required[Literal["program"]]
    """The caller type. Always `program`."""


ApplyPatchCallOutputCaller: TypeAlias = Union[ApplyPatchCallOutputCallerDirect, ApplyPatchCallOutputCallerProgram]


class ApplyPatchCallOutput(TypedDict, total=False):
    """The streamed output emitted by an apply patch tool call."""

    call_id: Required[str]
    """The unique ID of the apply patch tool call generated by the model."""

    status: Required[Literal["completed", "failed"]]
    """The status of the apply patch tool call output. One of `completed` or `failed`."""

    type: Required[Literal["apply_patch_call_output"]]
    """The type of the item. Always `apply_patch_call_output`."""

    id: Optional[str]
    """The unique ID of the apply patch tool call output.

    Populated when this item is returned via API.
    """

    agent: Optional[ApplyPatchCallOutputAgent]
    """The agent that produced this item."""

    caller: Optional[ApplyPatchCallOutputCaller]
    """The execution context that produced this tool call."""

    output: Optional[str]
    """
    Optional human-readable log text from the apply patch tool (e.g., patch results
    or errors).
    """


class McpListToolsTool(TypedDict, total=False):
    """A tool available on an MCP server."""

    input_schema: Required[object]
    """The JSON schema describing the tool's input."""

    name: Required[str]
    """The name of the tool."""

    annotations: Optional[object]
    """Additional annotations about the tool."""

    description: Optional[str]
    """The description of the tool."""


class McpListToolsAgent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class McpListTools(TypedDict, total=False):
    """A list of tools available on an MCP server."""

    id: Required[str]
    """The unique ID of the list."""

    server_label: Required[str]
    """The label of the MCP server."""

    tools: Required[Iterable[McpListToolsTool]]
    """The tools available on the server."""

    type: Required[Literal["mcp_list_tools"]]
    """The type of the item. Always `mcp_list_tools`."""

    agent: Optional[McpListToolsAgent]
    """The agent that produced this item."""

    error: Optional[str]
    """Error message if the server could not list tools."""


class McpApprovalRequestAgent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class McpApprovalRequest(TypedDict, total=False):
    """A request for human approval of a tool invocation."""

    id: Required[str]
    """The unique ID of the approval request."""

    arguments: Required[str]
    """A JSON string of arguments for the tool."""

    name: Required[str]
    """The name of the tool to run."""

    server_label: Required[str]
    """The label of the MCP server making the request."""

    type: Required[Literal["mcp_approval_request"]]
    """The type of the item. Always `mcp_approval_request`."""

    agent: Optional[McpApprovalRequestAgent]
    """The agent that produced this item."""


class McpApprovalResponseAgent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class McpApprovalResponse(TypedDict, total=False):
    """A response to an MCP approval request."""

    approval_request_id: Required[str]
    """The ID of the approval request being answered."""

    approve: Required[bool]
    """Whether the request was approved."""

    type: Required[Literal["mcp_approval_response"]]
    """The type of the item. Always `mcp_approval_response`."""

    id: Optional[str]
    """The unique ID of the approval response"""

    agent: Optional[McpApprovalResponseAgent]
    """The agent that produced this item."""

    reason: Optional[str]
    """Optional reason for the decision."""


class McpCallAgent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class McpCall(TypedDict, total=False):
    """An invocation of a tool on an MCP server."""

    id: Required[str]
    """The unique ID of the tool call."""

    arguments: Required[str]
    """A JSON string of the arguments passed to the tool."""

    name: Required[str]
    """The name of the tool that was run."""

    server_label: Required[str]
    """The label of the MCP server running the tool."""

    type: Required[Literal["mcp_call"]]
    """The type of the item. Always `mcp_call`."""

    agent: Optional[McpCallAgent]
    """The agent that produced this item."""

    approval_request_id: Optional[str]
    """
    Unique identifier for the MCP tool call approval request. Include this value in
    a subsequent `mcp_approval_response` input to approve or reject the
    corresponding tool call.
    """

    error: Optional[str]
    """The error from the tool call, if any."""

    output: Optional[str]
    """The output from the tool call."""

    status: Literal["in_progress", "completed", "incomplete", "calling", "failed"]
    """The status of the tool call.

    One of `in_progress`, `completed`, `incomplete`, `calling`, or `failed`.
    """


class CompactionTriggerAgent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class CompactionTrigger(TypedDict, total=False):
    """Compacts the current context. Must be the final input item."""

    type: Required[Literal["compaction_trigger"]]
    """The type of the item. Always `compaction_trigger`."""

    agent: Optional[CompactionTriggerAgent]
    """The agent that produced this item."""


class ItemReferenceAgent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class ItemReference(TypedDict, total=False):
    """An internal identifier for an item to reference."""

    id: Required[str]
    """The ID of the item to reference."""

    agent: Optional[ItemReferenceAgent]
    """The agent that produced this item."""

    type: Optional[Literal["item_reference"]]
    """The type of item to reference. Always `item_reference`."""


class ProgramAgent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class Program(TypedDict, total=False):
    id: Required[str]
    """The unique ID of this program item."""

    call_id: Required[str]
    """The stable call ID of the program item."""

    code: Required[str]
    """The JavaScript source executed by programmatic tool calling."""

    fingerprint: Required[str]
    """Opaque program replay fingerprint that must be round-tripped."""

    type: Required[Literal["program"]]
    """The item type. Always `program`."""

    agent: Optional[ProgramAgent]
    """The agent that produced this item."""


class ProgramOutputAgent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class ProgramOutput(TypedDict, total=False):
    id: Required[str]
    """The unique ID of this program output item."""

    call_id: Required[str]
    """The call ID of the program item."""

    result: Required[str]
    """The result produced by the program item."""

    status: Required[Literal["completed", "incomplete"]]
    """The terminal status of the program output."""

    type: Required[Literal["program_output"]]
    """The item type. Always `program_output`."""

    agent: Optional[ProgramOutputAgent]
    """The agent that produced this item."""


BetaResponseInputItemParam: TypeAlias = Union[
    BetaEasyInputMessageParam,
    Message,
    BetaResponseOutputMessageParam,
    BetaResponseFileSearchToolCallParam,
    BetaResponseComputerToolCallParam,
    ComputerCallOutput,
    BetaResponseFunctionWebSearchParam,
    BetaResponseFunctionToolCallParam,
    FunctionCallOutput,
    AgentMessage,
    MultiAgentCall,
    MultiAgentCallOutput,
    ToolSearchCall,
    BetaResponseToolSearchOutputItemParamParam,
    AdditionalTools,
    BetaResponseReasoningItemParam,
    BetaResponseCompactionItemParamParam,
    ImageGenerationCall,
    BetaResponseCodeInterpreterToolCallParam,
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
    BetaResponseCustomToolCallOutputParam,
    BetaResponseCustomToolCallParam,
    CompactionTrigger,
    ItemReference,
    Program,
    ProgramOutput,
]

BetaResponseInputParam: TypeAlias = List[BetaResponseInputItemParam]
