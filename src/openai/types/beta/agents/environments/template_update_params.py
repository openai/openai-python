# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

from ....._types import SequenceNotStr
from ...hosted_skill_param import HostedSkillParam
from ...hosted_plugin_param import HostedPluginParam
from ...setup_command_param import SetupCommandParam
from ...hosted_environment_file_param import HostedEnvironmentFileParam

__all__ = ["TemplateUpdateParams", "Network", "Packages"]


class TemplateUpdateParams(TypedDict, total=False):
    capability_directories: Optional[SequenceNotStr[str]]
    """Directories that expose capabilities to the agent."""

    env: Optional[Dict[str, str]]
    """Replacement confidential environment values."""

    files: Optional[Iterable[HostedEnvironmentFileParam]]
    """Replacement file configuration materialized for each new session."""

    name: Optional[str]
    """A replacement human-readable display name, or `null` to clear the name."""

    network: Optional[Network]
    """Network access for an OpenAI-hosted environment."""

    packages: Optional[Packages]
    """Packages to install in an OpenAI-hosted environment."""

    plugins: Optional[Iterable[HostedPluginParam]]
    """Replacement plugin configuration installed for each new session."""

    setup_commands: Optional[Iterable[SetupCommandParam]]
    """Replacement confidential setup commands, never included in returned resources."""

    skills: Optional[Iterable[HostedSkillParam]]
    """Replacement skill configuration installed for each new session."""


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
