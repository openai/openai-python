# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ...._utils import PropertyInfo
from ...._models import BaseModel
from ..hosted_plugin import HostedPlugin

__all__ = [
    "AutomationEnvironment",
    "AutomationEnvironmentResourceNone",
    "AutomationEnvironmentResourceOpenAIHosted",
    "AutomationEnvironmentResourceOpenAIHostedDesktop",
    "AutomationEnvironmentResourceOpenaiHostedFile",
    "AutomationEnvironmentResourceOpenAIHostedFileHostedTemplateFileResourceFileID",
    "AutomationEnvironmentResourceOpenAIHostedFileHostedTemplateFileResourceInline",
    "AutomationEnvironmentResourceOpenAIHostedNetwork",
    "AutomationEnvironmentResourceOpenAIHostedPackages",
    "AutomationEnvironmentResourceOpenaiHostedSkill",
    "AutomationEnvironmentResourceOpenAIHostedSkillHostedTemplateSkillResourceSkillReference",
    "AutomationEnvironmentResourceOpenAIHostedSkillHostedTemplateSkillResourceInline",
    "AutomationEnvironmentResourceSelfHosted",
]


class AutomationEnvironmentResourceNone(BaseModel):
    type: Literal["none"]
    """The type of the object. Always `none`."""


class AutomationEnvironmentResourceOpenAIHostedDesktop(BaseModel):
    """Desktop overrides, or null to inherit the template or creation default."""

    enabled: bool
    """Whether the environment provisions a desktop and browser proxy."""


class AutomationEnvironmentResourceOpenAIHostedFileHostedTemplateFileResourceFileID(BaseModel):
    """A project-scoped Files API reference resolved separately for each session."""

    file_id: str
    """The ID of the uploaded file."""

    path: str
    """The file's absolute path inside the environment."""

    type: Literal["file_id"]
    """The type of the object. Always `file_id`."""


class AutomationEnvironmentResourceOpenAIHostedFileHostedTemplateFileResourceInline(BaseModel):
    """Metadata for confidential inline file contents."""

    path: str
    """The file's absolute path inside the environment."""

    size_bytes: int
    """The decoded size of the inline file in bytes."""

    type: Literal["inline"]
    """The type of the object. Always `inline`."""


AutomationEnvironmentResourceOpenaiHostedFile: TypeAlias = Annotated[
    Union[
        AutomationEnvironmentResourceOpenAIHostedFileHostedTemplateFileResourceFileID,
        AutomationEnvironmentResourceOpenAIHostedFileHostedTemplateFileResourceInline,
    ],
    PropertyInfo(discriminator="type"),
]


class AutomationEnvironmentResourceOpenAIHostedNetwork(BaseModel):
    """Network overrides, or null to inherit the template or creation default."""

    access: Literal["enabled", "disabled", "restricted"]
    """The environment's network access mode.

    - `enabled` - Allows unrestricted network access.
    - `disabled` - Disables network access.
    - `restricted` - Applies the configured domain restrictions.
    """

    allowed_domains: List[str]
    """Domains the environment may access when network access is restricted."""


class AutomationEnvironmentResourceOpenAIHostedPackages(BaseModel):
    """Package overrides, or null to inherit the template or creation default."""

    npm: List[str]
    """npm packages installed globally in the environment."""

    python: List[str]
    """Python packages installed in the environment."""

    system: List[str]
    """System packages installed in the environment."""


class AutomationEnvironmentResourceOpenAIHostedSkillHostedTemplateSkillResourceSkillReference(BaseModel):
    """A skill resolved afresh from the Skills API whenever a session starts."""

    skill_id: str
    """The referenced skill ID."""

    type: Literal["skill_reference"]
    """The type of the object. Always `skill_reference`."""

    version: Optional[str] = None
    """The requested version selector, including `latest`."""


class AutomationEnvironmentResourceOpenAIHostedSkillHostedTemplateSkillResourceInline(BaseModel):
    """Safe metadata for an inline skill archive."""

    description: str
    """The skill description declared in `SKILL.md`."""

    name: str
    """The skill name declared in `SKILL.md`."""

    type: Literal["inline"]
    """The type of the object. Always `inline`."""


AutomationEnvironmentResourceOpenaiHostedSkill: TypeAlias = Annotated[
    Union[
        AutomationEnvironmentResourceOpenAIHostedSkillHostedTemplateSkillResourceSkillReference,
        AutomationEnvironmentResourceOpenAIHostedSkillHostedTemplateSkillResourceInline,
    ],
    PropertyInfo(discriminator="type"),
]


class AutomationEnvironmentResourceOpenAIHosted(BaseModel):
    """
    Hosted environment selection with confidential setup commands and variables omitted.
    """

    capability_directories: Optional[List[str]] = None
    """Directory overrides, or null to inherit the template or creation default."""

    container_size: Optional[Literal["small", "medium", "large"]] = None
    """The configured container size, or null to use the creation default."""

    desktop: Optional[AutomationEnvironmentResourceOpenAIHostedDesktop] = None
    """Desktop overrides, or null to inherit the template or creation default."""

    environment_id: Optional[str] = None
    """An existing environment reference, or null when provisioning a new environment."""

    environment_template_id: Optional[str] = None
    """A template reference, or null when no template is selected."""

    files: Optional[List[AutomationEnvironmentResourceOpenaiHostedFile]] = None
    """File overrides, excluding contents, or null to inherit."""

    network: Optional[AutomationEnvironmentResourceOpenAIHostedNetwork] = None
    """Network overrides, or null to inherit the template or creation default."""

    packages: Optional[AutomationEnvironmentResourceOpenAIHostedPackages] = None
    """Package overrides, or null to inherit the template or creation default."""

    plugins: Optional[List[HostedPlugin]] = None
    """Plugin overrides, excluding archive contents, or null to inherit."""

    skills: Optional[List[AutomationEnvironmentResourceOpenaiHostedSkill]] = None
    """Skill overrides, excluding archive contents, or null to inherit."""

    type: Literal["openai_hosted"]
    """The type of the object. Always `openai_hosted`."""


class AutomationEnvironmentResourceSelfHosted(BaseModel):
    capability_directories: List[str]
    """Directories that expose capabilities to the agent."""

    environment_id: Optional[str] = None
    """An existing registration, or null to create a session-owned environment."""

    type: Literal["self_hosted"]
    """The type of the object. Always `self_hosted`."""

    workspace_directory: str
    """The absolute project directory in the environment."""


AutomationEnvironment: TypeAlias = Annotated[
    Union[
        AutomationEnvironmentResourceNone,
        AutomationEnvironmentResourceOpenAIHosted,
        AutomationEnvironmentResourceSelfHosted,
    ],
    PropertyInfo(discriminator="type"),
]
