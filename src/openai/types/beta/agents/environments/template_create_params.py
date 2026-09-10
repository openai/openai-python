# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

from ....._types import SequenceNotStr
from ...hosted_skill_param import HostedSkillParam
from ...hosted_plugin_param import HostedPluginParam
from ...setup_command_param import SetupCommandParam
from ...hosted_environment_file_param import HostedEnvironmentFileParam

__all__ = ["TemplateCreateParams", "Network", "Packages"]


class TemplateCreateParams(TypedDict, total=False):
    capability_directories: Optional[SequenceNotStr[str]]
    """Directories that contain capabilities exposed to the agent.

    Defaults to an empty list.
    """

    env: Optional[Dict[str, str]]
    """Environment variables made available to the agent."""

    files: Optional[Iterable[HostedEnvironmentFileParam]]
    """Files available before the agent starts. Defaults to an empty list."""

    name: Optional[str]
    """An optional human-readable display name for the template."""

    network: Optional[Network]
    """Network access for an OpenAI-hosted environment."""

    packages: Optional[Packages]
    """Packages to install in an OpenAI-hosted environment."""

    plugins: Optional[Iterable[HostedPluginParam]]
    """Plugins provided as inline ZIP archives. Defaults to an empty list."""

    setup_commands: Optional[Iterable[SetupCommandParam]]
    """Ordered, confidential setup commands. Command bodies are never returned."""

    skills: Optional[Iterable[HostedSkillParam]]
    """Skills referenced by ID or provided as inline ZIP archives.

    Defaults to an empty list.
    """


class Network(TypedDict, total=False):
    """Network access for an OpenAI-hosted environment."""

    access: Required[Literal["enabled", "disabled", "restricted"]]
    """The environment's network access mode.

    - `enabled` - Allows unrestricted network access, matching an omitted network
      policy.
    - `disabled` - Disables network access.
    - `restricted` - Allows access only to configured domains.
    """

    allowed_domains: Optional[SequenceNotStr[str]]
    """Domains the environment may access when network access is restricted."""


class Packages(TypedDict, total=False):
    """Packages to install in an OpenAI-hosted environment."""

    npm: Optional[SequenceNotStr[str]]
    """npm packages to install globally. Defaults to an empty list."""

    python: Optional[SequenceNotStr[str]]
    """Python packages to install. Defaults to an empty list."""

    system: Optional[SequenceNotStr[str]]
    """System packages to install. Defaults to an empty list."""
