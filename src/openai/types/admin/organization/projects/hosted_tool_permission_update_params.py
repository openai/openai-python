# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["HostedToolPermissionUpdateParams", "CodeInterpreter", "FileSearch", "ImageGeneration", "Mcp", "WebSearch"]


class HostedToolPermissionUpdateParams(TypedDict, total=False):
    code_interpreter: Optional[CodeInterpreter]
    """The code interpreter permission update."""

    file_search: Optional[FileSearch]
    """The file search permission update."""

    image_generation: Optional[ImageGeneration]
    """The image generation permission update."""

    mcp: Optional[Mcp]
    """The MCP permission update."""

    web_search: Optional[WebSearch]
    """The web search permission update."""


class CodeInterpreter(TypedDict, total=False):
    """The code interpreter permission update."""

    enabled: Required[bool]
    """Whether to enable the hosted tool for the project."""


class FileSearch(TypedDict, total=False):
    """The file search permission update."""

    enabled: Required[bool]
    """Whether to enable the hosted tool for the project."""


class ImageGeneration(TypedDict, total=False):
    """The image generation permission update."""

    enabled: Required[bool]
    """Whether to enable the hosted tool for the project."""


class Mcp(TypedDict, total=False):
    """The MCP permission update."""

    enabled: Required[bool]
    """Whether to enable the hosted tool for the project."""


class WebSearch(TypedDict, total=False):
    """The web search permission update."""

    enabled: Required[bool]
    """Whether to enable the hosted tool for the project."""
