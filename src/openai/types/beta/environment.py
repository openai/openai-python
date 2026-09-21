# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Union
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .hosted_skill import HostedSkill
from .hosted_plugin import HostedPlugin
from .hosted_environment_file import HostedEnvironmentFile

__all__ = [
    "Environment",
    "EnvironmentResourceNone",
    "EnvironmentResourceOpenAIHosted",
    "EnvironmentResourceOpenAIHostedNetwork",
    "EnvironmentResourceOpenAIHostedPackages",
    "EnvironmentResourceSelfHosted",
]


class EnvironmentResourceNone(BaseModel):
    """
    The session talks to CCA without selecting or provisioning an execution environment.
    """

    type: Literal["none"]
    """The type of the object. Always `none`."""


class EnvironmentResourceOpenAIHostedNetwork(BaseModel):
    """The effective network access policy for the environment."""

    access: Literal["enabled", "disabled", "restricted"]
    """The environment's network access mode.

    - `enabled` - Allows unrestricted network access.
    - `disabled` - Disables network access.
    - `restricted` - Allows access only to configured domains.
    """

    allowed_domains: List[str]
    """Domains the environment may access when network access is restricted."""


class EnvironmentResourceOpenAIHostedPackages(BaseModel):
    """Packages installed in the environment."""

    npm: List[str]
    """npm packages installed globally in the environment."""

    python: List[str]
    """Python packages installed in the environment."""

    system: List[str]
    """System packages installed in the environment."""


class EnvironmentResourceOpenAIHosted(BaseModel):
    """An environment hosted by OpenAI."""

    id: str
    """The public ID of the environment."""

    capability_directories: List[str]
    """Directories that contain capabilities exposed to the agent."""

    files: List[HostedEnvironmentFile]
    """Files available in the environment, excluding their contents."""

    network: EnvironmentResourceOpenAIHostedNetwork
    """The effective network access policy for the environment."""

    packages: EnvironmentResourceOpenAIHostedPackages
    """Packages installed in the environment."""

    plugins: List[HostedPlugin]
    """Plugins installed in the environment, excluding their archive contents."""

    skills: List[HostedSkill]
    """Skills installed in the environment, excluding their archive contents."""

    type: Literal["openai_hosted"]
    """The type of the object. Always `openai_hosted`."""


class EnvironmentResourceSelfHosted(BaseModel):
    """An environment hosted by the application."""

    id: str
    """The public ID of the environment."""

    capability_directories: List[str]
    """Directories that contain capabilities exposed to the agent."""

    remote_url: str
    """
    Pass this URL unchanged to `codex exec-server --remote` when connecting this
    environment.
    """

    type: Literal["self_hosted"]
    """The type of the object. Always `self_hosted`."""

    workspace_directory: str
    """The absolute project directory inside the environment.

    Defaults to `/workspace`.
    """


Environment: TypeAlias = Annotated[
    Union[EnvironmentResourceNone, EnvironmentResourceOpenAIHosted, EnvironmentResourceSelfHosted],
    PropertyInfo(discriminator="type"),
]
