# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .hosted_skill_reference import HostedSkillReference

__all__ = ["HostedSkill", "HostedSkillResourceInline"]


class HostedSkillResourceInline(BaseModel):
    """A skill installed from an inline ZIP archive."""

    description: str
    """The installed skill description."""

    name: str
    """The installed skill name."""

    type: Literal["inline"]
    """The type of the object. Always `inline`."""


HostedSkill: TypeAlias = Annotated[
    Union[HostedSkillReference, HostedSkillResourceInline], PropertyInfo(discriminator="type")
]
