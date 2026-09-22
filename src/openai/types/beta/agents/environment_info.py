# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from ...._models import BaseModel
from ..hosted_skill import HostedSkill
from ..hosted_plugin import HostedPlugin
from ..hosted_environment_file import HostedEnvironmentFile

__all__ = ["EnvironmentInfo"]


class EnvironmentInfo(BaseModel):
    """Safe metadata for a first-class execution environment."""

    id: str
    """The ID of the environment."""

    files: List[HostedEnvironmentFile]
    """Files installed in the environment, without their contents."""

    object: Literal["agent.environment"]
    """The object type. Always `agent.environment`."""

    plugins: List[HostedPlugin]
    """Plugins installed in the environment, without their archive contents."""

    skills: List[HostedSkill]
    """Skills installed in the environment, without their archive contents."""

    status: Literal["pending", "connected", "disconnected", "expired", "failed"]
    """The current environment connection status."""

    type: Literal["openai_hosted", "self_hosted"]
    """Whether the environment is hosted by OpenAI or by the application."""
