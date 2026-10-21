# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..role import Role
from ....._models import BaseModel
from ..organization_user import OrganizationUser

__all__ = ["RoleCreateResponse"]


class RoleCreateResponse(BaseModel):
    """Role assignment linking a user to a role."""

    object: Literal["user.role"]
    """Always `user.role`."""

    role: Role
    """Details about a role that can be assigned through the public Roles API."""

    user: OrganizationUser
    """Represents an individual `user` within an organization."""
