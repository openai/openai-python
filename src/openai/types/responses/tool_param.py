# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .computer_tool_param import ComputerToolParam
from .function_tool_param import FunctionToolParam
from .web_search_tool_param import WebSearchToolParam
from .file_search_tool_param import FileSearchToolParam
from ..chat.chat_completion_tool_param import ChatCompletionToolParam

__all__ = [
    "ToolParam",
    "Mcp",
    "McpAllowedTools",
    "McpAllowedToolsMcpAllowedToolsFilter",
    "McpRequireApproval",
    "McpRequireApprovalMcpToolApprovalFilter",
    "McpRequireApprovalMcpToolApprovalFilterAlways",
    "McpRequireApprovalMcpToolApprovalFilterNever",
    "CodeInterpreter",
    "CodeInterpreterContainer",
    "CodeInterpreterContainerCodeInterpreterToolAuto",
    "ImageGeneration",
    "ImageGenerationInputImageMask",
    "LocalShell",
]

class McpAllowedToolsMcpAllowedToolsFilter(TypedDict, total=False):
    tool_names: List[str]
    """List of allowed tool names."""


McpAllowedTools: TypeAlias = Union[List[str], McpAllowedToolsMcpAllowedToolsFilter]


class McpRequireApprovalMcpToolApprovalFilterAlways(TypedDict, total=False):
    tool_names: List[str]
    """List of tools that require approval."""


class McpRequireApprovalMcpToolApprovalFilterNever(TypedDict, total=False):
    tool_names: List[str]
    """List of tools that do not require approval."""


class McpRequireApprovalMcpToolApprovalFilter(TypedDict, total=False):
    always: McpRequireApprovalMcpToolApprovalFilterAlways
    """A list of tools that always require approval."""

    never: McpRequireApprovalMcpToolApprovalFilterNever
    """A list of tools that never require approval."""

    tool_names: List[str]
    """List of allowed tool names."""


McpRequireApproval: TypeAlias = Union[McpRequireApprovalMcpToolApprovalFilter, Literal["always", "never"]]


class Mcp(TypedDict, total=False):
    server_label: Required[str]
    """A label for this MCP server, used to identify it in tool calls."""

    server_url: Required[str]
    """The URL for the MCP server."""

    type: Required[Literal["mcp"]]
    """The type of the MCP tool. Always `mcp`."""

    allowed_tools: Optional[McpAllowedTools]
    """List of allowed tool names or a filter object."""

    headers: Optional[Dict[str, str]]
    """Optional HTTP headers to send to the MCP server.

    Use for authentication or other purposes.
    """

    require_approval: Optional[McpRequireApproval]
    """Specify which of the MCP server's tools require approval."""


class CodeInterpreterContainerCodeInterpreterToolAuto(TypedDict, total=False):
    type: Required[Literal["auto"]]
    """Always `auto`."""

    file_ids: List[str]
    """An optional list of uploaded files to make available to your code."""


CodeInterpreterContainer: TypeAlias = Union[str, CodeInterpreterContainerCodeInterpreterToolAuto]


class CodeInterpreter(TypedDict, total=False):
    container: Required[CodeInterpreterContainer]
    """The code interpreter container.

    Can be a container ID or an object that specifies uploaded file IDs to make
    available to your code.
    """

    type: Required[Literal["code_interpreter"]]
    """The type of the code interpreter tool. Always `code_interpreter`."""


class ImageGenerationInputImageMask(TypedDict, total=False):
    file_id: str
    """File ID for the mask image."""

    image_url: str
    """Base64-encoded mask image."""


class ImageGeneration(TypedDict, total=False):
    type: Required[Literal["image_generation"]]
    """The type of the image generation tool. Always `image_generation`."""

    background: Literal["transparent", "opaque", "auto"]
    """Background type for the generated image.

    One of `transparent`, `opaque`, or `auto`. Default: `auto`.
    """

    input_image_mask: ImageGenerationInputImageMask
    """Optional mask for inpainting.

    Contains `image_url` (string, optional) and `file_id` (string, optional).
    """

    model: Literal["gpt-image-1"]
    """The image generation model to use. Default: `gpt-image-1`."""

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

    quality: Literal["low", "medium", "high", "auto"]
    """The quality of the generated image.

    One of `low`, `medium`, `high`, or `auto`. Default: `auto`.
    """

    size: Literal["1024x1024", "1024x1536", "1536x1024", "auto"]
    """The size of the generated image.

    One of `1024x1024`, `1024x1536`, `1536x1024`, or `auto`. Default: `auto`.
    """


class LocalShell(TypedDict, total=False):
    type: Required[Literal["local_shell"]]
    """The type of the local shell tool. Always `local_shell`."""


ToolParam: TypeAlias = Union[
    FunctionToolParam,
    FileSearchToolParam,
    WebSearchToolParam,
    ComputerToolParam,
    Mcp,
    CodeInterpreter,
    ImageGeneration,
    LocalShell,
]

  
ParseableToolParam: TypeAlias = Union[ToolParam, ChatCompletionToolParam]
