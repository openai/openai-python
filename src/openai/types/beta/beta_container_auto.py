# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .beta_inline_skill import BetaInlineSkill
from .beta_skill_reference import BetaSkillReference
from .beta_container_network_policy_disabled import BetaContainerNetworkPolicyDisabled
from .beta_container_network_policy_allowlist import BetaContainerNetworkPolicyAllowlist

__all__ = ["BetaContainerAuto", "NetworkPolicy", "Skill"]

NetworkPolicy: TypeAlias = Annotated[
    Union[BetaContainerNetworkPolicyDisabled, BetaContainerNetworkPolicyAllowlist], PropertyInfo(discriminator="type")
]

Skill: TypeAlias = Annotated[Union[BetaSkillReference, BetaInlineSkill], PropertyInfo(discriminator="type")]


class BetaContainerAuto(BaseModel):
    type: Literal["container_auto"]
    """Automatically creates a container for this request"""

    file_ids: Optional[List[str]] = None
    """An optional list of uploaded files to make available to your code."""

    memory_limit: Optional[Literal["1g", "4g", "16g", "64g"]] = None
    """The memory limit for the container."""

    network_policy: Optional[NetworkPolicy] = None
    """Network access policy for the container."""

    skills: Optional[List[Skill]] = None
    """An optional list of skills referenced by id or inline data."""
