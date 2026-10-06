# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

from ....._types import SequenceNotStr
from ...hosted_skill_param import HostedSkillParam
from ...hosted_plugin_param import HostedPluginParam
from ...setup_command_param import SetupCommandParam
from ...hosted_environment_file_param import HostedEnvironmentFileParam

__all__ = ["TemplateUpdateParams", "Desktop", "Network", "Packages"]


class TemplateUpdateParams(TypedDict, total=False):
    capability_directories: Optional[SequenceNotStr[str]]
    """Directories that expose capabilities to the agent."""

    desktop: Optional[Desktop]
    """Replacement desktop configuration, or null to disable the desktop."""

    env: Optional[Dict[str, str]]
    """Replacement confidential environment values."""

    files: Optional[Iterable[HostedEnvironmentFileParam]]
    """Replacement file configuration materialized for each new session."""

    name: Optional[str]
    """A replacement human-readable display name, or `null` to clear the name."""

    network: Optional[Network]
    """Network access available after setup completes.

    Omit to preserve the current policy, or pass `null` to reset to the default
    policy.
    """

    packages: Optional[Packages]
    """Packages installed before the runtime network policy applies."""

    plugins: Optional[Iterable[HostedPluginParam]]
    """Replacement plugin configuration installed for each new session."""

    setup_commands: Optional[Iterable[SetupCommandParam]]
    """Replacement confidential setup commands, never included in returned resources."""

    skills: Optional[Iterable[HostedSkillParam]]
    """Replacement skill configuration installed for each new session."""


class Desktop(TypedDict, total=False):
    """Replacement desktop configuration, or null to disable the desktop."""

    enabled: Required[bool]
    """Whether to provision the desktop and its browser proxy."""


class Network(TypedDict, total=False):
    """Network access available after setup completes.

    Omit to preserve the current policy, or pass `null` to reset to the default policy.
    """

    access: Required[Literal["enabled", "disabled", "restricted"]]
    """The environment's network access mode.

    - `enabled` - Allows unrestricted network access.
    - `disabled` - Disables network access.
    - `restricted` - Applies the configured domain restrictions.
    """

    allowed_domains: Optional[SequenceNotStr[str]]
    """Domains the environment may access when network access is restricted."""

    blocked_domains: Optional[SequenceNotStr[str]]
    """Domains blocked for both executor and browser when access is restricted.

    A nonempty list requires `access: restricted` and cannot be combined with
    nonempty `allowed_domains`. Wildcard domains are not supported.
    """


class Packages(TypedDict, total=False):
    """Packages installed before the runtime network policy applies."""

    npm: Optional[SequenceNotStr[str]]
    """npm packages to install globally. Defaults to an empty list."""

    python: Optional[SequenceNotStr[str]]
    """Python packages to install. Defaults to an empty list."""

    system: Optional[SequenceNotStr[str]]
    """System packages to install. Defaults to an empty list."""
