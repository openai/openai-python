# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ...role import Role
from ......_models import BaseModel

__all__ = ["RoleCreateResponse", "Group"]


class Group(BaseModel):
    """Summary information about a group returned in role assignment responses."""

    id: str
    """Identifier for the group."""

    created_at: int
    """Unix timestamp (in seconds) when the group was created."""

    name: str
    """Display name of the group."""

    object: Literal["group"]
    """Always `group`."""

    scim_managed: bool
    """Whether the group is managed through SCIM."""


class RoleCreateResponse(BaseModel):
    """Role assignment linking a group to a role."""

    group: Group
    """Summary information about a group returned in role assignment responses."""

    object: Literal["group.role"]
    """Always `group.role`."""

    role: Role
    """Details about a role that can be assigned through the public Roles API."""
