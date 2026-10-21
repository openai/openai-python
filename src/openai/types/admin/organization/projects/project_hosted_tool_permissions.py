# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ....._models import BaseModel

__all__ = ["ProjectHostedToolPermissions", "CodeInterpreter", "FileSearch", "ImageGeneration", "Mcp", "WebSearch"]


class CodeInterpreter(BaseModel):
    """Permission state for a single hosted tool on a project."""

    enabled: bool
    """Whether the hosted tool is enabled for the project."""


class FileSearch(BaseModel):
    """Permission state for a single hosted tool on a project."""

    enabled: bool
    """Whether the hosted tool is enabled for the project."""


class ImageGeneration(BaseModel):
    """Permission state for a single hosted tool on a project."""

    enabled: bool
    """Whether the hosted tool is enabled for the project."""


class Mcp(BaseModel):
    """Permission state for a single hosted tool on a project."""

    enabled: bool
    """Whether the hosted tool is enabled for the project."""


class WebSearch(BaseModel):
    """Permission state for a single hosted tool on a project."""

    enabled: bool
    """Whether the hosted tool is enabled for the project."""


class ProjectHostedToolPermissions(BaseModel):
    """Represents hosted tool permissions for a project."""

    code_interpreter: CodeInterpreter
    """Permission state for a single hosted tool on a project."""

    file_search: FileSearch
    """Permission state for a single hosted tool on a project."""

    image_generation: ImageGeneration
    """Permission state for a single hosted tool on a project."""

    mcp: Mcp
    """Permission state for a single hosted tool on a project."""

    web_search: WebSearch
    """Permission state for a single hosted tool on a project."""
