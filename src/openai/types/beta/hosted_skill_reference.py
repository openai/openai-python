# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["HostedSkillReference"]


class HostedSkillReference(BaseModel):
    """A skill installed from the Skills API."""

    description: str
    """The installed skill description."""

    name: str
    """The installed skill name."""

    skill_id: str
    """The referenced skill ID."""

    type: Literal["skill_reference"]
    """The type of the object. Always `skill_reference`."""

    version: str
    """The concrete skill version installed for this session."""
