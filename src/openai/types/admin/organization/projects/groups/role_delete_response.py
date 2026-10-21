# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ......_models import BaseModel

__all__ = ["RoleDeleteResponse"]


class RoleDeleteResponse(BaseModel):
    """Confirmation payload returned after unassigning a role."""

    deleted: bool
    """Whether the assignment was removed."""

    object: str
    """
    Identifier for the deleted assignment, such as `group.role.deleted` or
    `user.role.deleted`.
    """
