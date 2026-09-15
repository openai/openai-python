# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ....._utils import PropertyInfo
from ....._models import BaseModel
from ...hosted_plugin import HostedPlugin

__all__ = [
    "EnvironmentTemplate",
    "File",
    "FileHostedTemplateFileResourceFileID",
    "FileHostedTemplateFileResourceInline",
    "Network",
    "Packages",
    "Skill",
    "SkillHostedTemplateSkillResourceSkillReference",
    "SkillHostedTemplateSkillResourceInline",
]


class FileHostedTemplateFileResourceFileID(BaseModel):
    """A project-scoped Files API reference resolved separately for each session."""

    file_id: str
    """The ID of the uploaded file."""

    path: str
    """The file's absolute path inside the environment."""

    type: Literal["file_id"]
    """The type of the object. Always `file_id`."""


class FileHostedTemplateFileResourceInline(BaseModel):
    """Metadata for confidential inline file contents."""

    path: str
    """The file's absolute path inside the environment."""

    size_bytes: int
    """The decoded size of the inline file in bytes."""

    type: Literal["inline"]
    """The type of the object. Always `inline`."""


File: TypeAlias = Annotated[
    Union[FileHostedTemplateFileResourceFileID, FileHostedTemplateFileResourceInline],
    PropertyInfo(discriminator="type"),
]


class Network(BaseModel):
    """Runtime network access for each OpenAI-hosted environment."""

    access: Literal["enabled", "disabled", "restricted"]
    """The environment's network access mode.

    - `enabled` - Allows unrestricted network access.
    - `disabled` - Disables network access.
    - `restricted` - Allows access only to configured domains.
    """

    allowed_domains: List[str]
    """Domains the environment may access when network access is restricted."""


class Packages(BaseModel):
    """Packages installed in each fresh OpenAI-hosted environment."""

    npm: List[str]
    """npm packages installed globally in the environment."""

    python: List[str]
    """Python packages installed in the environment."""

    system: List[str]
    """System packages installed in the environment."""


class SkillHostedTemplateSkillResourceSkillReference(BaseModel):
    """A skill resolved afresh from the Skills API whenever a session starts."""

    skill_id: str
    """The referenced skill ID."""

    type: Literal["skill_reference"]
    """The type of the object. Always `skill_reference`."""

    version: Optional[str] = None
    """The requested version selector, including `latest`."""


class SkillHostedTemplateSkillResourceInline(BaseModel):
    """Safe metadata for an inline skill archive."""

    description: str
    """The skill description declared in `SKILL.md`."""

    name: str
    """The skill name declared in `SKILL.md`."""

    type: Literal["inline"]
    """The type of the object. Always `inline`."""


Skill: TypeAlias = Annotated[
    Union[SkillHostedTemplateSkillResourceSkillReference, SkillHostedTemplateSkillResourceInline],
    PropertyInfo(discriminator="type"),
]


class EnvironmentTemplate(BaseModel):
    """
    Reusable configuration that provisions a fresh OpenAI-hosted environment for each session.
    """

    id: str
    """The ID of the reusable environment template."""

    capability_directories: List[str]
    """Directories that expose capabilities to the agent."""

    created_at: int
    """The Unix timestamp, in seconds, when the template was created."""

    files: List[File]
    """Safe file metadata, excluding contents and session-scoped file IDs."""

    name: Optional[str] = None
    """An optional human-readable display name for the template."""

    network: Network
    """Runtime network access for each OpenAI-hosted environment."""

    object: Literal["agent.environment.template"]
    """The object type. Always `agent.environment.template`."""

    packages: Packages
    """Packages installed in each fresh OpenAI-hosted environment."""

    plugins: List[HostedPlugin]
    """Safe plugin metadata, excluding inline archive contents."""

    skills: List[Skill]
    """Safe skill metadata, preserving unresolved version selectors."""

    updated_at: int
    """The Unix timestamp, in seconds, when the template was last updated."""
