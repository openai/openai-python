# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from ..._types import SequenceNotStr
from .custom_tool_param import CustomToolParam
from .computer_tool_param import ComputerToolParam
from .function_tool_param import FunctionToolParam
from .web_search_tool_param import WebSearchToolParam
from .apply_patch_tool_param import ApplyPatchToolParam
from .file_search_tool_param import FileSearchToolParam
from .tool_search_tool_param import ToolSearchToolParam
from .function_shell_tool_param import FunctionShellToolParam
from .web_search_preview_tool_param import WebSearchPreviewToolParam
from .computer_use_preview_tool_param import ComputerUsePreviewToolParam
from .container_network_policy_disabled_param import ContainerNetworkPolicyDisabledParam
from .tool_search_output_namespace_tool_param import ToolSearchOutputNamespaceToolParam
from .container_network_policy_allowlist_param import ContainerNetworkPolicyAllowlistParam

__all__ = [
    "ResponseToolSearchOutputItemParamParam",
    "Tool",
    "ToolMcp",
    "ToolMcpAllowedTools",
    "ToolMcpAllowedToolsMcpToolFilter",
    "ToolMcpRequireApproval",
    "ToolMcpRequireApprovalMcpToolApprovalFilter",
    "ToolMcpRequireApprovalMcpToolApprovalFilterAlways",
    "ToolMcpRequireApprovalMcpToolApprovalFilterNever",
    "ToolCodeInterpreter",
    "ToolCodeInterpreterContainer",
    "ToolCodeInterpreterContainerCodeInterpreterToolAuto",
    "ToolCodeInterpreterContainerCodeInterpreterToolAutoNetworkPolicy",
    "ToolProgrammaticToolCalling",
    "ToolImageGeneration",
    "ToolImageGenerationInputImageMask",
    "ToolLocalShell",
]


class ToolMcpAllowedToolsMcpToolFilter(TypedDict, total=False):
    """A filter object to specify which tools are allowed."""

    read_only: bool
    """Indicates whether or not a tool modifies data or is read-only.

    If an MCP server is
    [annotated with `readOnlyHint`](https://modelcontextprotocol.io/specification/2025-06-18/schema#toolannotations-readonlyhint),
    it will match this filter.
    """

    tool_names: SequenceNotStr[str]
    """List of allowed tool names."""


ToolMcpAllowedTools: TypeAlias = Union[SequenceNotStr[str], ToolMcpAllowedToolsMcpToolFilter]


class ToolMcpRequireApprovalMcpToolApprovalFilterAlways(TypedDict, total=False):
    """A filter object to specify which tools are allowed."""

    read_only: bool
    """Indicates whether or not a tool modifies data or is read-only.

    If an MCP server is
    [annotated with `readOnlyHint`](https://modelcontextprotocol.io/specification/2025-06-18/schema#toolannotations-readonlyhint),
    it will match this filter.
    """

    tool_names: SequenceNotStr[str]
    """List of allowed tool names."""


class ToolMcpRequireApprovalMcpToolApprovalFilterNever(TypedDict, total=False):
    """A filter object to specify which tools are allowed."""

    read_only: bool
    """Indicates whether or not a tool modifies data or is read-only.

    If an MCP server is
    [annotated with `readOnlyHint`](https://modelcontextprotocol.io/specification/2025-06-18/schema#toolannotations-readonlyhint),
    it will match this filter.
    """

    tool_names: SequenceNotStr[str]
    """List of allowed tool names."""


class ToolMcpRequireApprovalMcpToolApprovalFilter(TypedDict, total=False):
    """Specify which of the MCP server's tools require approval.

    Can be
    `always`, `never`, or a filter object associated with tools
    that require approval.
    """

    always: ToolMcpRequireApprovalMcpToolApprovalFilterAlways
    """A filter object to specify which tools are allowed."""

    never: ToolMcpRequireApprovalMcpToolApprovalFilterNever
    """A filter object to specify which tools are allowed."""


ToolMcpRequireApproval: TypeAlias = Union[ToolMcpRequireApprovalMcpToolApprovalFilter, Literal["always", "never"]]


class ToolMcp(TypedDict, total=False):
    """
    Give the model access to additional tools via remote Model Context Protocol
    (MCP) servers. [Learn more about MCP](https://developers.openai.com/api/docs/guides/tools-connectors-mcp).
    """

    server_label: Required[str]
    """A label for this MCP server, used to identify it in tool calls."""

    type: Required[Literal["mcp"]]
    """The type of the MCP tool. Always `mcp`."""

    allowed_callers: Optional[List[Literal["direct", "programmatic"]]]
    """The tool invocation context(s)."""

    allowed_tools: Optional[ToolMcpAllowedTools]
    """List of allowed tool names or a filter object."""

    authorization: str
    """
    An OAuth access token that can be used with a remote MCP server, either with a
    custom MCP server URL or a service connector. Your application must handle the
    OAuth authorization flow and provide the token here.
    """

    connector_id: Literal[
        "connector_dropbox",
        "connector_gmail",
        "connector_googlecalendar",
        "connector_googledrive",
        "connector_microsoftteams",
        "connector_outlookcalendar",
        "connector_outlookemail",
        "connector_sharepoint",
    ]
    """Identifier for service connectors, like those available in ChatGPT.

    One of `server_url`, `connector_id`, or `tunnel_id` must be provided. Learn more
    about service connectors
    [here](https://developers.openai.com/api/docs/guides/tools-connectors-mcp#connectors).

    This field is deprecated for models released after September 1, 2026. Use
    `server_url` to connect to a remote MCP server, or `tunnel_id` to connect
    through a Secure MCP Tunnel.

    Currently supported `connector_id` values are:

    - Dropbox: `connector_dropbox`
    - Gmail: `connector_gmail`
    - Google Calendar: `connector_googlecalendar`
    - Google Drive: `connector_googledrive`
    - Microsoft Teams: `connector_microsoftteams`
    - Outlook Calendar: `connector_outlookcalendar`
    - Outlook Email: `connector_outlookemail`
    - SharePoint: `connector_sharepoint`
    """

    defer_loading: bool
    """Whether this MCP tool is deferred and discovered via tool search."""

    headers: Optional[Dict[str, str]]
    """Optional HTTP headers to send to the MCP server.

    Use for authentication or other purposes.
    """

    require_approval: Optional[ToolMcpRequireApproval]
    """Specify which of the MCP server's tools require approval."""

    server_description: str
    """Optional description of the MCP server, used to provide more context."""

    server_url: str
    """The URL for the MCP server.

    One of `server_url`, `connector_id`, or `tunnel_id` must be provided.
    """

    tunnel_id: str
    """The Secure MCP Tunnel ID to use instead of a direct server URL.

    One of `server_url`, `connector_id`, or `tunnel_id` must be provided.
    """


ToolCodeInterpreterContainerCodeInterpreterToolAutoNetworkPolicy: TypeAlias = Union[
    ContainerNetworkPolicyDisabledParam, ContainerNetworkPolicyAllowlistParam
]


class ToolCodeInterpreterContainerCodeInterpreterToolAuto(TypedDict, total=False):
    """Configuration for a code interpreter container.

    Optionally specify the IDs of the files to run the code on.
    """

    type: Required[Literal["auto"]]
    """Always `auto`."""

    file_ids: SequenceNotStr[str]
    """An optional list of uploaded files to make available to your code."""

    memory_limit: Optional[Literal["1g", "4g", "16g", "64g"]]
    """The memory limit for the code interpreter container."""

    network_policy: ToolCodeInterpreterContainerCodeInterpreterToolAutoNetworkPolicy
    """Network access policy for the container."""


ToolCodeInterpreterContainer: TypeAlias = Union[str, ToolCodeInterpreterContainerCodeInterpreterToolAuto]


class ToolCodeInterpreter(TypedDict, total=False):
    """A tool that runs Python code to help generate a response to a prompt."""

    container: Required[ToolCodeInterpreterContainer]
    """The code interpreter container.

    Can be a container ID or an object that specifies uploaded file IDs to make
    available to your code, along with an optional `memory_limit` setting.
    """

    type: Required[Literal["code_interpreter"]]
    """The type of the code interpreter tool. Always `code_interpreter`."""

    allowed_callers: Optional[List[Literal["direct", "programmatic"]]]
    """The tool invocation context(s)."""


class ToolProgrammaticToolCalling(TypedDict, total=False):
    type: Required[Literal["programmatic_tool_calling"]]
    """The type of the tool. Always `programmatic_tool_calling`."""


class ToolImageGenerationInputImageMask(TypedDict, total=False):
    """Optional mask for inpainting.

    Contains `image_url`
    (string, optional) and `file_id` (string, optional).
    """

    file_id: str
    """File ID for the mask image."""

    image_url: str
    """Base64-encoded mask image."""


class ToolImageGeneration(TypedDict, total=False):
    """A tool that generates images using the GPT image models."""

    type: Required[Literal["image_generation"]]
    """The type of the image generation tool. Always `image_generation`."""

    action: Literal["generate", "edit", "auto"]
    """Whether to generate a new image or edit an existing image. Default: `auto`."""

    background: Literal["transparent", "opaque", "auto"]
    """Allows to set transparency for the background of the generated image(s).

    Must be one of `transparent`, `opaque`, or `auto` (default value). When `auto`
    is used, the model will automatically determine the best background for the
    image.

    `gpt-image-2.5-sunburst` and `gpt-image-2.5-flare`, including their `2026-09-08`
    snapshots, support `opaque` and `transparent` backgrounds. Transparent
    backgrounds are available for supported GPT Image models. For `gpt-image-2` and
    `gpt-image-2-2026-04-21`, this support is in preview. When using `transparent`,
    set the output format to `png` or `webp`.
    """

    input_fidelity: Optional[Literal["high", "low"]]
    """
    Control how much effort the model will exert to match the style and features,
    especially facial features, of input images. Supports `high` and `low` on
    `gpt-image-1` and `gpt-image-1.5`; `gpt-image-1-mini` supports only `low`. For
    `gpt-image-2`, omit this parameter. Defaults to `low` on supported models.
    """

    input_image_mask: ToolImageGenerationInputImageMask
    """Optional mask for inpainting.

    Contains `image_url` (string, optional) and `file_id` (string, optional).
    """

    model: Union[
        str,
        Literal[
            "gpt-image-1",
            "gpt-image-1-mini",
            "gpt-image-2",
            "gpt-image-2-2026-04-21",
            "gpt-image-2.5-sunburst",
            "gpt-image-2.5-sunburst-2026-09-08",
            "gpt-image-2.5-flare",
            "gpt-image-2.5-flare-2026-09-08",
            "gpt-image-1.5",
            "chatgpt-image-latest",
        ],
    ]
    """The image generation model to use.

    One of `gpt-image-1`, `gpt-image-1-mini`, `gpt-image-1.5`, `gpt-image-2`,
    `gpt-image-2-2026-04-21`, `gpt-image-2.5-sunburst`,
    `gpt-image-2.5-sunburst-2026-09-08`, `gpt-image-2.5-flare`,
    `gpt-image-2.5-flare-2026-09-08`, or `chatgpt-image-latest`. Default:
    `gpt-image-1`.
    """

    moderation: Literal["auto", "low"]
    """Moderation level for the generated image. Default: `auto`."""

    output_compression: int
    """Compression level for the output image. Default: 100."""

    output_format: Literal["png", "webp", "jpeg"]
    """The output format of the generated image.

    One of `png`, `webp`, or `jpeg`. Default: `png`.
    """

    partial_images: int
    """
    Number of partial images to generate in streaming mode, from 0 (default value)
    to 3.
    """

    quality: Literal["low", "medium", "high", "xhigh", "max", "auto"]
    """The quality of the generated image.

    The GPT image models support `low`, `medium`, and `high`.
    `gpt-image-2.5-sunburst` and `gpt-image-2.5-flare`, including their `2026-09-08`
    snapshots, also support `xhigh` and `max`. Default: `auto`.
    """

    size: Union[str, Literal["1024x1024", "1024x1536", "1536x1024", "auto"]]
    """The size of the generated images.

    For `gpt-image-2`, `gpt-image-2-2026-04-21`, `gpt-image-2.5-sunburst`,
    `gpt-image-2.5-sunburst-2026-09-08`, `gpt-image-2.5-flare`, and
    `gpt-image-2.5-flare-2026-09-08`, arbitrary resolutions are supported as
    `WIDTHxHEIGHT` strings, for example `1536x864`. Width and height must both be
    divisible by 16 and the requested aspect ratio must be between 1:3 and 3:1.
    Resolutions above `2560x1440` are experimental, and the maximum supported
    resolution is `3840x2160`. The requested size must also satisfy the model's
    current pixel and edge limits. The standard sizes `1024x1024`, `1536x1024`, and
    `1024x1536` are supported by the GPT image models; `auto` is supported for
    models that allow automatic sizing.
    """


class ToolLocalShell(TypedDict, total=False):
    """A tool that allows the model to execute shell commands in a local environment."""

    type: Required[Literal["local_shell"]]
    """The type of the local shell tool. Always `local_shell`."""


Tool: TypeAlias = Union[
    FunctionToolParam,
    FileSearchToolParam,
    ComputerToolParam,
    ComputerUsePreviewToolParam,
    WebSearchToolParam,
    ToolMcp,
    ToolCodeInterpreter,
    ToolProgrammaticToolCalling,
    ToolImageGeneration,
    ToolLocalShell,
    FunctionShellToolParam,
    CustomToolParam,
    ToolSearchOutputNamespaceToolParam,
    ToolSearchToolParam,
    WebSearchPreviewToolParam,
    ApplyPatchToolParam,
]


class ResponseToolSearchOutputItemParamParam(TypedDict, total=False):
    tools: Required[Iterable[Tool]]
    """The loaded tool definitions returned by the tool search output."""

    type: Required[Literal["tool_search_output"]]
    """The item type. Always `tool_search_output`."""

    id: Optional[str]
    """The unique ID of this tool search output."""

    call_id: Optional[str]
    """The unique ID of the tool search call generated by the model."""

    execution: Literal["server", "client"]
    """Whether tool search was executed by the server or by the client."""

    status: Optional[Literal["in_progress", "completed", "incomplete"]]
    """The status of the tool search output."""
